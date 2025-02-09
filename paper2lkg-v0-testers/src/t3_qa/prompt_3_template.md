## Task

You are a helpful assistant in answering questions regarding a specific academic paper. Given a question about an academic paper and some recourses extracted from the knowledge graph of the paper, your task is to try to answer the question. The recourses you are given is a list of relevant entities and a list of (subject, predicate, object) triples about their relations.

## Output Format

Please write your answer in JSON format, as shown below:

```
{{
 "answer": "you answer to the question."
}}
```

## Question

{question}


## Resources (Entities)

```
{entities}
```

## Resources (Triples)

```
{triples}
```

## Answer

*Please write your answer*