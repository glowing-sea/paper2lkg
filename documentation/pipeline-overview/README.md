# Pipeline Overview

This section aims to provide provide a comprehensive overview of the design and implementation of the pipeline. It include the following components:

*Note: in this version of documentation, Stage 3: Entity Linking contains the mechanism of LLM double check before grouping Mentions into the same Entities. While it can increase the efficacy, it significantly reduce the efficiency of the pipeline as this step can lead to quadratic complexity. Therefore, this step is disable when the paper is submitted.*

- [Design of the open local KGC approach](./pipeline-design/):
  - Demo
  - Comparison to Traditional KGC
  - Comparison to Other KGC
  - SWOT Analysis

- [Overview of the Implementation and pipeline IO](./pipeline-implementation/):   
  - Interface
  - Pipeline Structure
  - Execution Diagram
  - Design Choice

- [Stage 1: Mention Extraction](./stage-1/)
  - Algorithm
  - Prompts
    - [Prompt 1: Named Entity Extraction](../../paper2lkg-v0/src/modules/m02_mention_extraction_typing/prompt_1_template.md)
    - [Prompt 1: Named Entity + General Concept Extraction](../../paper2lkg-v0/src/modules/m02_mention_extraction_typing/prompt_2_template.md)
    - [Prompt 1: Entity Extraction](../../paper2lkg-v0/src/modules/m02_mention_extraction_typing/prompt_3_template.md)
  - Assumptions
  - Limitations
  - Complexity
  - Design Choices

- [Stage 2: Entity Linking](./stage-2/)
  - Algorithm
  - Prompts
    - [Prompt 2.1: LLM Background Knowledge Check](../../paper2lkg-v0/src/modules/m03_entity_resolution_disambiguation/prompt_2.md)
    - [Prompt 2.2.1: Description Generation with Full Context](../../paper2lkg-v0/src/modules/m03_entity_resolution_disambiguation/prompt_3_specific.md)
    - [Prompt 2.2.2: Description Generation with Limited Context](../../paper2lkg-v0/src/modules/m03_entity_resolution_disambiguation/prompt_3_general.md)
    - [Prompt 2.3: LLM Double Checking (Disabled)](../../paper2lkg-v0/src/modules/m03_entity_resolution_disambiguation/prompt_5_section.md)
  - Assumptions
  - Limitations
  - Complexity
  - Design Choices

- [Stage 3: Local Relation Extraction](./stage-3/)
  - Algorithm
  - Prompts
    - [Prompt 3: Local Relation Extraction](../../paper2lkg-v0/src/modules/m04_local_relation_extraction/prompt_1_template.md)
  - Assumptions
  - Limitations
  - Complexity
  - Design Choices

- [Stage 4: Global Relation Extraction](./stage-4/)
  - Algorithm
  - Prompts
    - [Prompt 4.1: Paper Summarisation](../../paper2lkg-v0/src/modules/m05_global_relation_extraction/prompt_1_template.md)
    - [Prompt 4.2: Extracting A Predicate between Two Entities](../../paper2lkg-v0/src/modules/m03_entity_resolution_disambiguation/prompt_3_specific.md)
    - [Prompt 4.2+: Determining the Subject of the Relation](../../paper2lkg-v0/src/modules/m05_global_relation_extraction/prompt_4_template.md)
  - Assumptions
  - Limitations
  - Complexity
  - Design Choices

- [Stage 5: Taxonomy Generation and Predication Resolution](./stage-5/)
  - Algorithm
  - Prompts
    - [Prompt 5.1: Entity Type Description Generation](../../paper2lkg-v0/src/modules/m06_schema_generation/prompt_1.md)
    - [Prompt 5.2: Predicate Description Generation](../../paper2lkg-v0/src/modules/m06_schema_generation/prompt_3.md)
  - Assumptions
  - Limitations
  - Complexity
  - Design Choices