#!/bin/bash

python gen_judgment.py \
  --model-list your_model_id_1 your_model_id_2 \
  --parallel 4 \
  --judge-model qwen-max
