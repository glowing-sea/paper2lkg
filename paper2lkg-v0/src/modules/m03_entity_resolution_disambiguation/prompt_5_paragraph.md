## Task

You are a linguistic expert who is involved in the task of disambiguating two terms in a paper. Given the abstract of the paper (paper-level context), the term "{label_1}" and the term "{label_2}", each with its label, types, description, the specific paragraph where the mention appears (paragraph-level context), and the specific sentence of the entity mention (sentence-level context), your task is to determine whether these two terms refer to **exactly** the same entity or concept. Please provide a short explanation and then answer true or false in JSON format, e.g.,


```
{{
    "explanation": "your explanation"
    "answer": true
}}
```

## Input

### Paper-Level Context:
Title: {title}
Authors: {authors}
Keywords: {keywords}
Abstract:
{paper_level_context}

### Term 1: {label_1}

**Label**: {label_1}
**Types**: {types_1}
**Description 1**: {description_1}

**Paragraph-Level Context**:
{paragraph_level_context_1}

**Sentence-Level Context**:
{sentence_level_context_1}

### Term 2: {label_2}

**Label**: {label_2}
**Types**: {types_2}
**Description**: {description_2}

**Paragraph-Level Context**:
{paragraph_level_context_2}

**Sentence-Level Context**:
{sentence_level_context_2}


## Output

*Please provide your answer*