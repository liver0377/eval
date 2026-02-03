import pandas as pd
import glob
import os

# 假设你的文件在 ./IFBench_multi-turn 目录下
input_dir = '/data/wudy/projects/IFBench/dataset/IFBench_multi-turn'
output_file = '/data/wudy/projects/IFBench/data/IFBench_multi-turn.jsonl'

# 找到所有的 parquet 文件
files = glob.glob(os.path.join(input_dir, "**/*.parquet"), recursive=True)

all_dfs = []
for f in files:
    print(f"正在读取: {f}")
    all_dfs.append(pd.read_parquet(f))

# 合并并保存
if all_dfs:
    df = pd.concat(all_dfs, ignore_index=True)
    # orient='records' 和 lines=True 会生成标准的 JSONL 格式
    df.to_json(output_file, orient='records', lines=True, force_ascii=False)
    print(f"转换完成！文件保存至: {output_file}")
else:
    print("未找到 Parquet 文件，请检查路径。")