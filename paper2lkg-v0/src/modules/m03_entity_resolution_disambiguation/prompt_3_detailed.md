## Task

You are a linguistic expert involved in a description writing task for an entity or concept in a paper. Given the term "{label}", its types, the abstract of the paper (paper-level context), the specific section where the mention appears (section-level context), and the specific sentence of the entity mention (sentence-level context), your task is to write a single-sentence description that can precisely tell what the actual entity or concept the term "{label}" refers to. 

## Output Format

Write your answer in JSON format, e.g.,

```
{{
    "description": "your description"
}}
```

## Input

**Entity Mention**: {label}
**Types**: {types}
**Paper-Level Context**:
Title: {title}
Authors: {authors}
Keywords: {keywords}
Abstract:
{paper_level_context}

**Section-Level Context**:
{section_level_context}

**Sentence-Level Context**:
{sentence_level_context}

## Output

*Please provide your answer*