# scripts/build_eval_set.py
# 构建eval_set
# 完整的一条instruction 格式如下:
# ### SYSTEM PROMPT
# {system_prompt}

# ### DIALOGUE SO FAR
# User: {u0}
# Assistant: {a0}
# User: {u1}
# Assistant: {a1}
# ...
# User: {u_current}

# ### TASK
# Continue the conversation. Output ONLY the assistant's next message.


import json
import re
from pathlib import Path

ROUND_RE = re.compile(r"Round:(\d+)")

def to_role(fr):
    return "user" if fr == "human" else "assistant"

def format_for_instruction(system_prompt: str, messages):
    lines = []
    lines.append("### SYSTEM PROMPT")
    lines.append(system_prompt.strip())
    lines.append("")
    lines.append("### DIALOGUE SO FAR")
    for m in messages:
        role = "User" if m["role"] == "user" else "Assistant"
        lines.append(f"{role}: {m['content']}")
    lines.append("")
    lines.append("### TASK")
    lines.append("继续对话. 只输出assisant的下一条信息.")
    return "\n".join(lines)

def main(in_path: str, out_path: str):
    out = []
    with open(in_path, "r", encoding="utf-8") as f:
        for row_id, line in enumerate(f):
            ex = json.loads(line)
            system_prompt = ex["system_prompt"]
            conv = ex["conversations"]

            # 将 conversations 变成标准 messages
            messages = [{"role": to_role(m["from"]), "content": m["value"]} for m in conv]

            # 逐个 human turn 生成样本：取到该 human 为止（含该 human），不含其后的 assistant
            for i, m in enumerate(messages):
                if m["role"] != "user":
                    continue

                prefix = messages[: i + 1]
                instr = format_for_instruction(system_prompt, prefix)

                # 解析 Round（可用于后续自动分桶，不算“手工 tag”）
                round_num = None
                mm = ROUND_RE.search(m["content"])
                if mm:
                    round_num = int(mm.group(1))

                out.append({
                    "id": f"{row_id}_{i}",
                    "round": round_num,
                    "instruction": instr,

                    # 给生成模型用（可选字段，AlpacaEval 不用也不影响）
                    "system_prompt": system_prompt,
                    "messages": prefix,
                })

    with open(out_path, "w", encoding="utf-8") as f:
        for x in out:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main("sales_repo/data/train.jsonl", "sales_repo/data/eval_set.jsonl")