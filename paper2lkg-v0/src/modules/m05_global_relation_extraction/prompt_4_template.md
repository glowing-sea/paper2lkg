## Task Definition

You are a linguistic expert involved in a subject identification task. Given the terms "{subject_label}" and "{object_label}" related by the predicate "{predicate}", your task is to determine the subject of this relation. Your answer should be a triple, providing the new orders for Term 1 and Term 2.

- Your answer should based on the labels, types, and descriptions of both terms, the predicate, and your common knowledge.
- You should also check if the predicate is active or passive in order to determine the subject
- Ask yourself whether "{subject_label} {predicate} {object_label}" is more fluent or "{object_label} {predicate} {subject_label}" is more fluent and natural


## Output Format

Please 

Please write the new triple with the correct subject and object order in JSON, as shown below:

```
{format_example}
```

## Input

### Term 1: {subject_label}

**Label** : {subject_label}
**Types**: {subject_types}
**Description**: {subject_description}

### Predicate: {predicate}
**Label**: {predicate}

### Term 2: {object_label}

**Label** : {object_label}
**Types**: {object_types}
**Description**: {object_description}


**Output**:

*Please provide your answer*