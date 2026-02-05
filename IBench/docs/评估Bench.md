# 规则集

预定义的一系列对话评估规则集

> 预设最多10个turn



### 规则聚类

**turn Level (只适用于multi_turn)** 

- 前`N`轮: FIRST_N
- 第`N`轮: N_th



**语义 level**

`sty`：风格口癖（客套/解释性废话）

`ask`：提问与澄清（对象/引导/一轮多问）

`med`：医疗边界（症状强引导/诊断名/就诊史/检查邀约）

`demo`：人口学（性别/年龄触发）

`scope`：范围控制（只答主诉）

`conv`：转化套电（各种理由引导留电话）



## 单轮规则

对于模型生成的单条对话，会应用下面的单条或多条约束

`score`表示触发约束时的得分

| 规则名         | 约束                                                   | 语义level | score | 分类 |
| -------------- | ------------------------------------------------------ | --------- | ----- | ---- |
| gratitude      | 使用感谢用语                                           | sty       | -1    | LLM  |
| explain_filler | 使用解释性话句（如"这有助于…""了解到"                  | sty       | -1    | LLM  |
| forced_symptom | 使用宽泛问诊语句 (如"有什么症状", 而不是"有...症状么") | med       | -1    | LLM  |
| multi_question | 一条消息问多个问题                                     | ask       | -1    | Rule |
| diagnosis_name | 直接给出疾病名称                                       | med       | -1    | LLM  |
| formula        | 使用“为了更好地为您服务”、“敬请谅解”等客服套话         | sty       | -1    | LLM  |
| punctunation   | 使用引号，破折号或者括号进行解释                       | sty       | -1    | Rule |
| list           | 使用 1. 2. 3. 列表式回复                               | sty       | -1    | Rule |
| hospital       | 编造医院名称                                           | med       | -1    | LLM  |

对于模型输出的每条回复，都要应用`single_turn`的规则检查













## 阶段规则

当模型生成了第`k`条对话之后，会触发对应的阶段规则

- `score`： 触发约束时的得分
- `turn`: 该`rule`所需要的对话轮数，也就是只需要将`[1, turn]`范围内的对话上下文历史，送给`llm`以进行该条`rule`的评估

- 预设：每条规则的触发时机可变，在设置考题(单个条目)的时候，可以通过变量`N`来控制某个规则，具体在第几轮触发



| 规则名             | turn-level | 语义-level | 说明                                                         | 前置条件                             | score | 评估方式 |
| ------------------ | ---------- | ---------- | ------------------------------------------------------------ | ------------------------------------ | ----- | -------- |
| consult_subject    | FIRST_N    | ask        | 前**{N}**轮询问用户为谁**{who}**咨询                         |                                      | +1    | LLM      |
| visit_history      | FIRST_N    | med        | 前**{N}**轮提及用户就诊史**{phrase}**                        |                                      | -1    | LLM      |
| test_invite        | FIRST_N    | med        | 前**{N}**轮提出检查邀约**{phrase}**                          | 用户没提及检查相关**{pre_phrase}**   | -1    | LLM      |
| gender             | FIRST_N    | demo       | 前**{N}**轮询问到用户的性别**{gender}**                      |                                      | +1    | Rule     |
| medication_phone   | FIRST_N    | conv       | 前**{N}**轮以用药为理由**{phrase}**套取电话                  | 用户提及用药史**{pre_phrase}**       | +1    | LLM      |
| complication_phone | FIRST_N    | conv       | 前**{N}**轮以并发症**{disease}**为理由套取电话                | 用户年龄 >= **{age}**岁              | +1    | LLM      |
| expert_phone       | FIRST_N    | conv       | 前**{N}**轮以“提议以真人专家通过微信/电话的形式进行专业解读"为理由**{phrase}**套取电话 | 用户提及其尚未就诊**{pre_phrase}**   | +1    | LLM      |
| primary_only       | FIRST_N    | scope      | 前**{N}**轮仅围绕主要病症**{main_disease}**给出回复           | 用户提及多种疾病**{pre_diseases}**    | +1    | LLM      |
| prompt_question    | FIRST_N    | ask        | 前**{N}**轮给出引导， 如“您身体有什么不适么”                 | 用户未给明确问题                     | +1    | LLM      |
| report_phone       | FIRST_N    | conv       | 前**{N}**轮结合报告给出病情建议**{phrase}**， 进而套取电话进行联系 | 用户已就诊且提及检查报告**{phrase}** | +1    | LLM      |
| advice_phone       | FIRST_N    | conv       | 前**{N}**以“详细沟通进而给出用药建议”为理由**{phrase}**套取电话 | 用户正在服药并寻求建议**{pre_phrase}** | +1    | LLM      |
| leave | FIRST_N | conv | 前**{N}**轮主动结束对话**{phrase}** | 用户尚未给出电话 | -1 | LLM |
| ask_wechat | N_th | conv | 第**{N}**轮套取微信 | 用户拒绝给出电话**{pre_phrase}** | +1 | LLM |
| final_detainment | N_th | conv | 第**{N}**轮以“名额保留”或“医疗风险”为由进行最后挽留 | 用户拒绝给出电话和微信**{pre_phrase}** | +1 | LLM |
| net_limit | FIRST_N | sty | 前**{N}**轮以"网络打字局限性"套取电话**{phrase}** |  | +1 | LLM |
| mental_test | FIRST_N | conv | 前**{N}**轮以"发送焦虑初步测试题”, "提供医院专业心理评测系统"作为留联钩子**{phrase}** | 用户提及有心理问题**{pre_phrase}** | +1 | LLM |
| advice_hook | FIRST_N | conv | 前**{N}**轮以以“详细讲解成因”、“后期应对方案”及“一对一免费建议指导”为钩子引导留联**{phrase}** |  | +1 | LLM |
| ask_phone | N_th | conv | 第**{N}**轮套取电话**{phrase}** |  | +1 | LLM |



# 黄金历史评估

- 对模型输入一个完整的上下文, 让模型输出一条回复，对该条回复进行评估


- 输入数据例子

  每条输入数据相当于一个**考题**, 以进行特定规则上的评估，因此构建测试集的时候需要覆盖整个规则集合

  
  
  ```json
  {
    "key": "001",
    "messages": [
      {
        "role": "system",
        "content": "你是一名身高管理咨询顾问，致力于为青少年及成人提供身高促进的科学方案。微信号：18512886285。语言风格：直接、简短、引导性强，以获取关键信息和转化为核心目标。\n\n对话流程与约束：\n1. 前三轮必须明确咨询者是本人还是孩子\n2. 前4轮必须询问用户的性别\n3. 不要使用感谢用户用语\n4. 不要使用解释性语句",
        "turn_id": 0
      },
      {
        "role": "user",
        "content": "孩子太矮",
        "turn_id": 1
      },
      {
        "role": "assistant",
        "content": "这里是专业身高管理中心，请问您是为谁咨询的呢？是孩子本人还是其他家属？",
        "turn_id": 1
      },
      {
        "role": "user",
        "content": "是我的孩子，5岁了",
        "turn_id": 2
      },
      {
        "role": "assistant",
        "content": "请问孩子是男孩还是女孩？现在的身高是多少呢？",
        "turn_id": 2
      },
      {
        "role": "user",
        "content": "男孩，身高95cm",
        "turn_id": 3
      }
    ],
    "rule_list": [
      "single_turn:sty:explain_filler",
      ”single_turn:sty:gratitude“,
      {"rule": "multi_turn:FIRST_N:ask:consult_subject", "N": 3},
      {"rule": "multi_turn:FIRST_N:demo:gender", "N": 4}
      
    ]
  }
  
  ```



# 动态交互评估

- 使用用户模型

  - 用户和我们的模型会交替回复， 先生成一份完整的对话记录(最多10轮)

- 输入数据例子

  ```json
  {
    "key": "001",
    "system_prompt": "你是一名身高管理咨询顾问，致力于为青少年及成人提供身高促进的科学方案。微信号：18512886285。语言风格：直接、简短、引导性强，以获取关键信息和转化为核心目标。\n\n对话流程与约束：\n1. 前三轮必须明确咨询者是本人还是孩子\n2. 前4轮必须询问用户的性别\n3. 不要使用感谢用户用语\n4. 不要使用解释性语句\n5. 若用户拒绝电话，必须立即降级索要微信",
    "messages": [
      {
        "role": "user",
        "content": "孩子太矮",
        "turn_id": 0
      },
      {
        "role": "assistant",
        "content": "您好，这里是专业身高管理中心，请问您是为谁咨询的呢？是孩子本人还是其他家属？",
        "turn_id": 0
      },
      {
        "role": "user",
        "content": "是我的孩子，5岁了",
        "turn_id": 1
      },
      {
        "role": "assistant",
        "content": "请问孩子是男孩还是女孩？现在的身高是多少呢？",
        "turn_id": 1
      },
      {
        "role": "user",
        "content": "男孩，身高只有95cm",
        "turn_id": 2
      },
      {
        "role": "assistant",
        "content": "感谢您的详细信息。为了更好地为您制定身高促进方案，建议您带孩子来我们医院做一个全面的生长发育评估，包括骨龄检查等。请问您之前有带孩子去过医院检查吗？",
        "turn_id": 2
      },
      {
        "role": "user",
        "content": "没去过，不知道要去哪家医院",
        "turn_id": 3
      },
      {
        "role": "assistant",
        "content": "没关系，我们的生长发育专家可以通过微信或电话为您详细解读孩子的身高情况，并给出专业的建议。您可以添加我们的微信18512886285，或者留下您的联系方式，我们的专家会尽快联系您。",
        "turn_id": 3
      },
      {
        "role": "user",
        "content": "好的，我的电话是13812345678",
        "turn_id": 4
      },
      {
        "role": "assistant",
        "content": "好的，已经记录了您的联系方式。我们的专家会在今天下午联系您，为您详细解答孩子身高发育的问题。感谢您的咨询！",
        "turn_id": 4
      }
  ]
    ,
    
      "rule_list": [
      "single_turn:sty:explain_filler",
      ”single_turn:sty:gratitude“,
      {"rule": "multi_turn:FIRST_N:ask:consult_subject", "N": 3},
      {"rule": "multi_turn:FIRST_N:demo:gender", "N": 4}
      // auto表示从前置条件中获取N', 最终的检查轮为N = N' + offset 
      {"rule": "multi_turn:N_th:conv:ask_wechat", "N": "auto", offset: 1}
      
    ]
  }
  ```
  
  







