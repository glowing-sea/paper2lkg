## Task

You are a linguistic expert who is involved in a description writing task for an entity mentioned in a paper. Given an entity's mention "{label}", its types, the specific sentence of the entity mention (context), your task is to write a single-sentence description that can precisely tell what the actual entity the mention "{label}" refers to. 
- Your description should be as general as possible and not be specific to the given context.
- The context is mainly used to help you understand the entity or disambiguate the entity with others with the same name. 

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
**Context**: {sentence_level_context}

## Output

*Please provide your answer*