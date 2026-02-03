---
dataset_info:
- config_name: ifbench_constraints
  features:
  - name: key
    dtype: int64
  - name: prompt
    dtype: string
  - name: instruction_id_list
    sequence: string
  - name: kwargs
    list:
    - name: N
      dtype: int64
    - name: small_n
      dtype: int64
    - name: percentage
      dtype: int64
    - name: word
      dtype: string
    - name: sep
      dtype: string
    - name: n
      dtype: 'null'
    - name: m
      dtype: 'null'
    - name: keyword
      dtype: string
    - name: min_words
      dtype: int64
    - name: max_words
      dtype: int64
    - name: keyword1
      dtype: 'null'
    - name: keyword2
      dtype: 'null'
    - name: keyword3
      dtype: 'null'
    - name: keyword4
      dtype: 'null'
  - name: messages
    list:
    - name: role
      dtype: string
    - name: content
      dtype: string
  splits:
  - name: test
    num_bytes: 9289641
    num_examples: 1387
  download_size: 3667524
  dataset_size: 9289641
- config_name: ifeval_constraints
  features:
  - name: key
    dtype: int64
  - name: prompt
    dtype: string
  - name: instruction_id_list
    sequence: string
  - name: kwargs
    list:
    - name: keyword
      dtype: string
    - name: end_phrase
      dtype: string
    - name: keywords
      sequence: string
    - name: forbidden_words
      sequence: string
    - name: language
      dtype: string
    - name: frequency
      dtype: int64
    - name: relation
      dtype: string
    - name: num_sentences
      dtype: int64
    - name: num_paragraphs
      dtype: int64
    - name: let_frequency
      dtype: int64
    - name: letter
      dtype: string
    - name: num_bullets
      dtype: int64
    - name: capital_frequency
      dtype: int64
    - name: capital_relation
      dtype: string
    - name: num_sections
      dtype: int64
    - name: section_spliter
      dtype: string
    - name: num_words
      dtype: int64
    - name: postscript_marker
      dtype: string
    - name: num_highlights
      dtype: int64
    - name: num_placeholders
      dtype: int64
  - name: messages
    list:
    - name: role
      dtype: string
    - name: content
      dtype: string
  splits:
  - name: test
    num_bytes: 12380857
    num_examples: 1774
  download_size: 4603270
  dataset_size: 12380857
configs:
- config_name: ifbench_constraints
  data_files:
  - split: test
    path: ifbench_constraints/test-*
- config_name: ifeval_constraints
  data_files:
  - split: test
    path: ifeval_constraints/test-*
---
## Dataset

This is the test data for the multi-turn setup of IFBench.

## License

This dataset is licensed under ODC-BY-1.0. It is intended for research and educational use in accordance with Ai2's [Responsible Use Guidelines](https://allenai.org/responsible-use). This dataset includes output data generated from third party models that are subject to separate terms governing their use. 

## Citation
Please cite:
```
@misc{pyatkin2025generalizing,
   title={Generalizing Verifiable Instruction Following}, 
   author={Valentina Pyatkin and Saumya Malik and Victoria Graf and Hamish Ivison and Shengyi Huang and Pradeep Dasigi and Nathan Lambert and Hannaneh Hajishirzi},
   year={2025},
   eprint={TODO},
   archivePrefix={arXiv},
   primaryClass={cs.CL}
}
```