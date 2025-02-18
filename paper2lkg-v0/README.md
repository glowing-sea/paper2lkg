# Setup and Running Guide

paper2lkg has been tested functional on a 2021 MacBook Pro with an M1 Max chip and a AMD Ryzen 5 5600X 6-Core Processor, 16 GB RAM, and GeForce RTX 3080 12GB running Pop! OS 22.04 LTS. It should be compatible with most Macs and PCs running Linux.

### Step 1: OS Environment

For Linux users with a Nvidia GPU:
1. Install the latest Nvidia driver.
2. Install cuda toolkit 12.6.

For Mac users:
1. Install the latest macOS.

*It is not recommended to run the pipeline on CPU or GPUs other than the Nvidia ones.*

### Step 2: Python Environment

Install Python 3.12.8 using Anaconda

Install the following packages:
- conda install numpy
- conda install nltk
- conda install pip
- pip install gpt4all
- pip install -U FlagEmbedding
- pip install openai
- pip install rdflib

- pip install voyageai (to run the `t2_kg_to_text` part of `paper2lkg-v0-testers`)

### Step 3: Running paper2lkg

If you want to run paper2lkg using GPT, create a JSON file call `api_key.json` under `./src/utilities`. Then, move the two files `llm_response_handler_JSON_list.py` and `llm_response_handler_JSON.py` from `./src/utilities/gpt` to `./src/utilities`.

If you want to run paper2lkg using LLaMA, move the two files `llm_response_handler_JSON_list.py` and `llm_response_handler_JSON.py` from `./src/utilities/llama` to `./src/utilities`.

If you are using a Mac to run paper2lkg with LLaMA, ensure the file `device` in the function `initialise_llm()` in the files `llm_response_handler_JSON_list.py` and `llm_response_handler_JSON.py` is set to `gpu`. If you are using a Nvidia CPU, ensure it is set to `cuda`.

Prepare the paper your want to transform to local KG in `./data/input`. There are already 10 full paper and 100 abstract-only preprocessed into the acceptable format, i.e., the Deep Document Model (DDM) representation. However, if you only have the original paper, e.g., a PDF file, you should turn it into a DDM first. You can either do it automatically or manually. To preprocess documents into DDM automatically, please to the [DDM](https://github.com/KGCP/DDM) repository for details. To convert a document into DDM manually, go to `/data/input` and follow the three steps. You should first create a JSON file like this [example](./data/input/step_2_assigning_IRI/format_example.json), where a document should have been decomposed into a hierarchy of sections, paragraphs, and sentences along with its metadata. To do so, you should use the tool in [`/data/input/step_1_building_DDM`](./data/input/step_1_building_DDM/). This tool leverage LLM to convert any unstructured section of a paper into an hierarchy paragraphs and sentence. However, you should manually construct each section of the DDM as well as the metadata. After constructing the initial DDM, run [`./data/input/step_2_assigning_IRI/IRI_assigner.ipynb`](./data/input/step_2_assigning_IRI/IRI_assigner.ipynb) to assign each node in the DDM an IRI. After this step, you paper should be ready to input into the pipeline.

To start paper2lkg, run `./src/main.py` or `./src/main_batch.py` to process multiple papers.

The output local KG of the paper is in `./data/input`. It is in either the JSON or TTL formats.