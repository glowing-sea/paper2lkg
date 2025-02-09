# The Pipeline Overview: Supplementary Resources

This page provides links to the full algorithm and prompt of each stage of the pipeline. The pipeline itself is at [here](../../LLM-KGC-v0/). Some prompt mentioned in the paper is further divided into several variations.

## Stage 1

Algorithm: [See page 26 of the PDF](./Implementation%20Details.pdf#page=26)

Prompt 1 ([Named Entity Extraction](../../LLM-KGC-v0/src/modules/m02_mention_extraction_typing/prompt_1_template.md), [Entity Extraction](../../LLM-KGC-v0/src/modules/m02_mention_extraction_typing/prompt_2_template.md), [Mention Extraction](../../LLM-KGC-v0/src/modules/m02_mention_extraction_typing/prompt_3_template.md))

## Stage 2

Algorithm: [See page 42 of the PDF](./Implementation%20Details.pdf#page=42)

Prompt 2.1 ([LLM Background Knowledge Check](../../LLM-KGC-v0/src/modules/m03_entity_resolution_disambiguation/prompt_2.md))

Prompt 2.2.1 ([Description Generation with Full Context](../../LLM-KGC-v0/src/modules/m03_entity_resolution_disambiguation/prompt_3_specific.md))

Prompt 2.2.2 ([Description Generation with Limited Context](../../LLM-KGC-v0/src/modules/m03_entity_resolution_disambiguation/prompt_3_general.md))

Prompt 2.3 ([LLM Double Checking (Disabled)](../../LLM-KGC-v0/src/modules/m03_entity_resolution_disambiguation/prompt_5_section.md))

*Note that the full version of the pipeline prompt the generative LLM using Prompt 2.3 to double check if the two Mentions are the same when their embeddings are found highly similar. However, this functionality is disabled because it can lead to quadratic complexity.*

## Stage 3

Algorithm: [See page 53 of the PDF](./Implementation%20Details.pdf#page=53)

Prompt 3 (([Local Relation Extraction](../../LLM-KGC-v0/src/modules/m04_local_relation_extraction/prompt_1_template.md)))

## Stage 4

Algorithm: [See page 61 of the PDF](./Implementation%20Details.pdf#page=61)

Prompt 4.1 ([Paper Summarisation](../../LLM-KGC-v0/src/modules/m05_global_relation_extraction/prompt_1_template.md))

Prompt 4.2 ([Extracting A Predicate between Two Entities](../../LLM-KGC-v0/src/modules/m05_global_relation_extraction/prompt_3_template.md), [Determining the Subject of the Relation](../../LLM-KGC-v0/src/modules/m05_global_relation_extraction/prompt_4_template.md))

## Stage 5

Algorithm: [See page 66 of the PDF](./Implementation%20Details.pdf#page=66)

Prompt 5.1 ([Entity Type Description Generation](../../LLM-KGC-v0/src/modules/m06_schema_generation/prompt_1.md))

Prompt 5.2 ([Predicate Description Generation](../../LLM-KGC-v0/src/modules/m06_schema_generation/prompt_3.md))

