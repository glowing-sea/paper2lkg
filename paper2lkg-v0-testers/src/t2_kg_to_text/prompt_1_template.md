## Task Definition

You are a linguistic expert involved in the task of knowledge-graph-to-text generation. Given a list of (subject, predicate, object) triples in a graph, given the label, aliases, and description of all the entities involved in these triples, your task is to generate a fluent paragraph describing these triples. 

You may use the information of entities for reference. However, the focus of your generated paragraph should be the triples, i.e., the relations between entities, rather than solely the label, aliases and description of each entity.

## Output Format

Please write your answer in JSON format, as shown below:

```
{{
 "paragraph": "Your generated text based on the graph."
}}
```

## Entities

```
{entities}
```

## Relations (Triples)

```
{triples}
```

## Your Output

*Please write your answer in JSON*