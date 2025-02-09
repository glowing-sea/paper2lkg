## Experiment Setup

To enable all different evaluations, the starting point is to use our KGC pipeline to build KGs. The test sets we have used to build KGs are as follows:

### Dataset 1: Five Full Papers

This set consists of 4 full papers from ANU ASKG plus 1 full paper not in ANU ASKG.

The 4 papers from ANU ASKG are already semi-structured, i.e., consisting of a hierarchy of sections, paragraphs, and sentences, and they are in the TTL formats, which can be directly accepted by our KGC pipeline. The ones outside of ASKG are in raw PDF format. Therefore, we performed a manual decomposition into a similar hierarchy structure as those in ASKG and stored the result in JSON, which can then also be accepted by our pipeline by skipping the initial TTL-to-JSON stage.

Specifically, the title of each paper is:

1. MEL: Metadata Extractor & Loader  
2. Modeling Actuations in BCI-O: A Context-based Integration of SOSA and IoT-O  
3. Building An Open Source Linux Computing System On RISC-V  
4. TNNT: The Named Entity Recognition Toolkit  
5. A Pipeline For Analysing Grant Applications  

### Dataset 2: SciERC

The dataset SciERC contains the mappings between 500 semi-structured abstract-only academic papers and their corresponding KGs. We regard them as semi-structured because, as in most NLP datasets, the papers have been preprocessed and sentence-tokenized, stored in JSONs. Although the target KGs are supplied, these KGs are considered the results of traditional KGC approaches with a fixed and predefined number of types and predicates. However, they are still valuable references during our manual evaluation.

The dataset had already been split into the training set (350), test set (100), and development set (50) when we downloaded it. Therefore, we ran our pipeline on their given test set consisting of 100 abstract-only papers.

Although they are already semi-structured, basic preprocessing was done to align their structure with those in ASKG so that they match the interface of our pipeline.

### Platform

The platform to create KGs from the datasets and perform the later evaluation processes is a desktop with the following specifications:

- **CPU**: AMD Ryzen 5 5600X 6-Core Processor  
- **Memory**: 16 GB  
- **GPU**: GeForce RTX 3080 12GB  
- **OS**: Pop! OS 22.04 LTS  

### LLMs

Three of the four LLMs used are the same as the development process. However, we also used GPT-4o-Mini as the decoder of our pipeline to create KGs in order to see the portability and compatibility of our pipeline with different LLMs. Although we have listed two encoders, they are not the variable in our testing as they are used in different stages for different purposes. Only LLaMA and GPT are our variables and are switched during the testing.

**Decoder 1**:

- **Named**: `Meta-Llama-3-8B-Instruct.Q4_0.gguf`  
- **Size**: 4.66GB  
- **Context Limit**: 8192  
- **Availability**: [Meta-Llama-3-8B](https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/tree/main)  

**Decoder 2**:

- **Named**: `gpt-4o-mini`  
- **Size**: Unknown  
- **Context Limit**: 128k  
- **Availability**: [GPT-4o-Mini](https://platform.openai.com/docs/models/o1)  

**Encoder 1**:

- **Named**: `BAAI--bge-base-en-v1.5`  
- **Size**: 438.9MB  
- **Context Limit**: 512  
- **Availability**: [bge-base-en](https://huggingface.co/BAAI/bge-base-en)  

**Encoder 2**:

- **Named**: `BAAI--bge-m3`  
- **Size**: 2.29GB  
- **Context Limit**: 8192  
- **Availability**: [bge-m3](https://huggingface.co/BAAI/bge-m3) 

