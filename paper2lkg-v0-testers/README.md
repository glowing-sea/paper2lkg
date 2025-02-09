# Testers Setup and Results Reproduction Guide

Put the local KGs output from the pipeline into `./data/input`. The 210 ((5 ASKG papers + 100 SciERC paper) * 2 LLMs) local KG constructed by the pipeline using either GPT or LLaMA are already in this folder

There are three testers in this package.

- [General Tester](./src/t1_general_eva/): provides general statistics of the constructed local KGs.
- [Reverse Engineering Tester](./src/t2_kg_to_text/): evaluate the reversibility of the constructed local KGs by turning it back to text using LLMs.
- [RAG Tester](./src/t3_qa/): evaluate the application of the constructed local KGs by using the local KGs to perform graph-based Retrieval Augmented Generation (RAG)

### Steps to Reproduce General Statistics

Run [`./src/t1_general_eva/statistics.ipynb`](./src/t1_general_eva/statistics.ipynb) and the results can be found under [`./data/raw_results/`](./data/raw_results/) with names starting with `gen`. The results are in the form of CSV tables.

### Steps to Reproduce the Results of Reverse Engineering Test

Run [`./src/t2_kg_to_text/run_1_kg_to_text.py`](./src/t2_kg_to_text/run_1_kg_to_text.py) and [`./src/t2_kg_to_text/run_2_generate_result.py`](./src/t2_kg_to_text/run_2_generate_result.py) in order. The synthesised articles are stored under [`./data/output/`](./data/output/). The results can be found under [`./data/raw_results/`](./data/raw_results/) with names starting with `re`. The results are in the form of JSON.

### Steps to Reproduce the Results of RAG Test

Run [`./src/t3_qa/run_1_question_generation.py`](./src/t3_qa/run_1_question_generation.py) to generate a prompt for create the ground-true question-answer pairs. Copy the prompts and paste it into an GPT-O1 model online. Store the response in JSON into [`./data/input/QA/`](./data/input/QA/). The results are already there.

Run [`./src/t3_qa/run_2_generate_answers.py`](./src/t3_qa/run_2_generate_answers.py) to generate the actual answers. The actual answers are stored under [`./data/output/QA/`](./data/output/QA/)

Run [`./src/t3_qa/run_3_analyse.ipynb`](./src/t3_qa/run_3_analyse.ipynb) to generate results. The result are stored under [`./data/raw_results/`](./data/raw_results/) with names starting with `rag`.