## Task Definition

You are a linguistic expert involved in a relation verification task. Given the (subject, predicate, object) triple and a document, your task is to determine if the relation form by the triple exist in the document.

Specifically, the triple you are checking is ({subject_label}, {predicate}, {object_label})


## Output Format

Please write provide your explanation and then answer true or false in JSON format.

```
{format_example}
```

## Input

### Subject: {subject_label}
**Label** : {subject_label}
**Types**: {subject_types}
**Description**: {subject_description}


### Predicate: {predicate}
**Label**: {predicate}


### Object: {object_label}
**Label** : {object_label}
**Types**: {object_types}
**Description**: {subject_description}


### Paper
**Title**: {paper_title}
**Keywords** {paper_keywords}
**Authors** {paper_authors}
**Content** {paper_content}


### Subject: {subject_label}
**Label** : {subject_label}
**Types**: {subject_types}
**Description**: {subject_description}


### Predicate: {predicate}
**Label**: {predicate}


### Object: {object_label}
**Label** : {object_label}
**Types**: {object_types}
**Description**: {subject_description}


**Output**:

*Please your answer*