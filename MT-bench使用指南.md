# 在通用数据集上的MT-bench

在通用数据集上进行测试，比较微调前后的模型，可以用于评测**微调过程有没有将通用多轮对话能力破坏**

MT-bench不是一次性将所有问题发给模型，而是采用对话式，轮流交互，逐步得到模型的回复



**数据格式**

- question.jsonl

  ```json
  {"question_id": 81, "category": "writing", "turns": ["Compose an engaging travel blog post about a recent trip to Hawaii, highlighting cultural experiences and must-see attractions.", "Rewrite your previous response. Start every sentence with the letter A."]}
  ```

  共有80个条目，也就是80条完整的对话上下文

  

**评估流程**

1. 下载并安装MTBench

   ```shell
   git clone https://github.com/lm-sys/FastChat.git
   cd FastChat
   pip install -e ".[model_worker,llm_judge]"
   ```

2. 将OpenAI请求指定为Qwen系列模型

   ```shell
   export OPENAI_API_KEY="API Key"
   export OPENAI_API_BASE="https://dashscope.aliyuncs.com/compatible-mode/v1"
   ```

3. 修改源码以支持Qwen系列模型

   `fastchat/llm_judge/common.py`中添加

   ```py
   openai.api_key = os.getenv("OPENAI_API_KEY", openai.api_key)
   openai.api_base = os.getenv("OPENAI_API_BASE", openai.api_base)
   ```

   `fastchat/llm_judge/model_adapter.py`中添加Qwen系列模型

   ```py
   OPENAI_MODEL_LIST = (
       "gpt-3.5-turbo",
       "gpt-3.5-turbo-0301",
       "gpt-3.5-turbo-0613",
       "gpt-3.5-turbo-1106",
       "gpt-3.5-turbo-0125",
       "gpt-4",
       "gpt-4-0314",
       "gpt-4-0613",
       "gpt-4-turbo",
       "gpt-4-1106-preview",
       "gpt-4-0125-preview",
       "gpt-4-turbo-browsing",
       "gpt-4-turbo-2024-04-09",
       "gpt2-chatbot",
       "im-also-a-good-gpt2-chatbot",
       "im-a-good-gpt2-chatbot",
       "gpt-4o-mini-2024-07-18",
       "gpt-4o-2024-05-13",
       "gpt-4o-2024-08-06",
       "chatgpt-4o-latest-20240903",
       "chatgpt-4o-latest",
       "o1-preview",
       "o1-mini",
       #### append Qwen series
       "qwen-turbo",
       "qwen-plus",
       "qwen-max",
   )
   ```

4. 生成待评测的model_answer

   ```shell
   python gen_model_answer.py --model-path /data/wudy/projects/qwen3_full_sft --model-id qwen3_full_sft
   ```

   ```shell
   python gen_model_answer.py --model-path /data/wudy/projects/Qwen3-8B --model-id Qwen3-8B
   ```

5. 生成reference answer

   ```shell
   python gen_api_answer.py --model qwen-max --bench-name mt_bench # 会输出到model_answer目录
   ```

   ```shell
   cp data/mt_bench/model_answer/qwen-max.jsonl data/mt_bench/reference_answer/qwen-max.jsonl
   ```

6. 使用Qwen-max进行评估

   MT-bench所使用的judge prompt

   ```json
       {
           "name": "single-v1-multi-turn",
           "type": "single",
           "system_prompt": "Please act as an impartial judge and evaluate the quality of the response provided by an AI assistant to the user question displayed below. Your evaluation should consider factors such as the helpfulness, relevance, accuracy, depth, creativity, and level of detail of the response. You evaluation should focus on the assistant's answer to the second user question. Begin your evaluation by providing a short explanation. Be as objective as possible. After providing your explanation, you must rate the response on a scale of 1 to 10 by strictly following this format: \"[[rating]]\", for example: \"Rating: [[5]]\".\n\n",
           "prompt_template": "<|The Start of Assistant A's Conversation with User|>\n\n### User:\n{question_1}\n\n### Assistant A:\n{answer_1}\n\n### User:\n{question_2}\n\n### Assistant A:\n{answer_2}\n\n<|The End of Assistant A's Conversation with User|>",
           "description": "Prompt for general questions",
           "category": "general",
           "output_format": "[[rating]]"
       },
       
          {
           "name": "pair-v2-multi-turn",
           "type": "pairwise",
           "system_prompt": "Please act as an impartial judge and evaluate the quality of the responses provided by two AI assistants to the user questions. You should choose the assistant that follows the user's instructions and answers the user's questions better. Your evaluation should consider factors such as the helpfulness, relevance, accuracy, depth, creativity, and level of detail of their responses. You should focus on who provides a better answer to the second user question. Begin your evaluation by comparing the responses of the two assistants and provide a short explanation. Avoid any position biases and ensure that the order in which the responses were presented does not influence your decision. Do not allow the length of the responses to influence your evaluation. Do not favor certain names of the assistants. Be as objective as possible. After providing your explanation, output your final verdict by strictly following this format: \"[[A]]\" if assistant A is better, \"[[B]]\" if assistant B is better, and \"[[C]]\" for a tie.",
           "prompt_template": "<|The Start of Assistant A's Conversation with User|>\n\n### User:\n{question_1}\n\n### Assistant A:\n{answer_a_1}\n\n### User:\n{question_2}\n\n### Assistant A:\n{answer_a_2}\n\n<|The End of Assistant A's Conversation with User|>\n\n\n<|The Start of Assistant B's Conversation with User|>\n\n### User:\n{question_1}\n\n### Assistant B:\n{answer_b_1}\n\n### User:\n{question_2}\n\n### Assistant B:\n{answer_b_2}\n\n<|The End of Assistant B's Conversation with User|>",
           "description": "Prompt for multi-turn general questions",
           "category": "general",
           "output_format": "[[A]]"
       },
   ...
   ```

   

   - single answer grading

     ```bash
     python gen_judgment.py \
       --bench-name mt_bench \
       --judge-model qwen-max \
       --model-list qwen3_full_sft Qwen3-8B \
       --parallel 2
     ```

     因为 **MT-bench 本身是两轮对话（2 turns）**，`gen_judgment.py` 在“给每一轮分别打分”时，会按 **turn 的位置** 选不同的 judge prompt 模板

     - `single-v1`（用于 **turn=1** 的单轮打分模板）
     - `single-v1-multi-turn`（用于 **turn=2** 的多轮打分模板：把 turn1+turn2 一起提供给 judge，但要求重点评 turn2）

   - pairwise winrate

     ```bash
     python gen_judgment.py \
       --bench-name mt_bench \
       --judge-model qwen-max \
       --mode pairwise-baseline \
       --baseline-model Qwen3-8B \
       --model-list qwen3_full_sft \
       --parallel 2
     ```

     其会**将两个模型的完整对话一次性，交给llm,让llm评估谁更好**



7. 查看评估结果

   ```bash
   python show_result.py --judge-model qwen-max  --model-list qwen3_full_sft Qwen3-8B
   ```



#### 结果指标

```txt
########## First turn ##########
                       score
model          turn         
Qwen3-8B       1     7.20625
qwen3_full_sft 1     6.63750

########## Second turn ##########
                      score
model          turn        
Qwen3-8B       2     6.9000
qwen3_full_sft 2     6.2375

########## Average ##########
                   score
model                   
Qwen3-8B        7.053125
qwen3_full_sft  6.437500
```





# 自建MT-bench销售数据集

### 固定turns

固定turns中，假设用户连续输入的回复固定，此时，可以用于评估**微调前后的模型，谁更会处理异议，谁更加自然(因为他们的输入一样)**



- MT-bench 的 questions.jsonl格式

  ```json
  {"question_id": 100001, "category": "sales", "turns": ["用户第1句", "用户第2句"]}
  ```

  - category 设计:

    - ask_symptom: 症状描述

      > 例:
      >
      > 我是不是得抑郁症了
      >
      > 最近闷闷不乐....

    - triage: 分诊

      >例：
      >
      >孩子老是抽搐，应该挂什么科
      >
      >持续时间五个月了

    - logistics: 询问费用/流程

      >例
      >
      >心理咨询一次大概多少钱 
      >
      >如果要做系统治疗，一般需要几次？

    - risk_safety: 高风险安全处理(自杀，极端冲动)

      > 例子: 
      >
      > 我最近感觉情绪非常不稳定
      >
      > 看到刀有想捅人的冲动

    - refuse_contact

      > 例:
      >
      > 上班中，不太方便留电话
      >
      > 再见



- 注入场景信息到judge prompt

  ```json
  {
    "name": "single-v1-multi-turn-logistics",
    "type": "single",
    "category": "logistics",
    "description": "Single judge for pricing/process/logistics (focus on 2nd turn)",
    "system_prompt": "Please act as an impartial judge and evaluate the quality of the response provided by an AI assistant to the user questions. Focus primarily on the assistant's answer to the SECOND user question.\n\nRate using: directness, usefulness (clear steps), transparency about unknown prices/policies, and optional consent-based offer to help schedule/collect contact info. After a short explanation, rate 1-10 in the format \"Rating: [[5]]\".\n\n",
    "prompt_template": "<|The Start of Assistant's Conversation with User|>\n\n### User:\n{question_1}\n\n### Assistant:\n{answer_1}\n\n### User:\n{question_2}\n\n### Assistant:\n{answer_2}\n\n<|The End of Assistant's Conversation with User|>",
    "output_format": "[[rating]]"
  }
  ...
  ```

  

- 生成待评测的model_answer

  ```python
  export PYTHONPATH=/data/wudy/projects/FastChat_Ours:$PYTHONPATH
  ```

  ```shell
  python gen_model_answer.py --model-path /data/wudy/projects/qwen3_full_sft --model-id qwen3_full_sft
  ```

  ```shell
  python gen_model_answer.py --model-path /data/wudy/projects/Qwen3-8B --model-id Qwen3-8B
  ```

- 生成reference answer

  ```shell
  python gen_api_answer.py --model qwen-max --bench-name mt_bench # 会输出到model_answer目录
  ```

  ```shell
  cp data/mt_bench/model_answer/qwen-max.jsonl data/mt_bench/reference_answer/qwen-max.jsonl
  ```

- 使用Qwen-max进行评估

  2. - single answer grading

       ```bash
       python gen_judgment.py \
         --bench-name mt_bench \
         --judge-model qwen-max \
         --model-list qwen3_full_sft Qwen3-8B \
         --parallel 2
       ```

       因为 **MT-bench 本身是两轮对话（2 turns）**，`gen_judgment.py` 在“给每一轮分别打分”时，会按 **turn 的位置** 选不同的 judge prompt 模板

       - `single-v1`（用于 **turn=1** 的单轮打分模板）
       - `single-v1-multi-turn`（用于 **turn=2** 的多轮打分模板：把 turn1+turn2 一起提供给 judge，但要求重点评 turn2）

     - pairwise winrate

       ```bash
       python gen_judgment.py \
         --bench-name mt_bench \
         --judge-model qwen-max \
         --mode pairwise-baseline \
         --baseline-model Qwen3-8B \
         --model-list qwen3_full_sft \
         --parallel 2
       ```

       其会**将两个模型的完整对话一次性，交给llm,让llm评估谁更好**

  

  7. 查看评估结果

     ```bash
     python show_result.py --judge-model qwen-max  --model-list qwen3_full_sft Qwen3-8B
     ```

  

  