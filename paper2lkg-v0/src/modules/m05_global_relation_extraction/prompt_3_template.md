## Task Definition

You are a linguistic expert involved in a relation extraction task for finding the relationship between the terms "{term_1}" and "{term_2}" in an academic paper. Given the title, authors, keywords, and content of the paper as well as the types and description of each term, your task is to extract the **most important** predicate that connect the term "{term_1}" and the term "{term_2}".

## Output Format

Please write your answer into a list in JSON format consisting of **at most one** predicate, as shown below:

```
{format_example}
```

## Input

### Term 1: {term_1}

**Label** : {term_1}
**Types**: {types_1}
**Description**: {description_1}


### Term 2: {term_2}

**Label** : {term_2}
**Types**: {types_2}
**Description**: {description_2}

### Paper
**Title**: {title}
**Keywords** {keywords}
**Authors** {authors}
**Content** {content}


### Term 1: {term_1}

**Label** : {term_1}
**Types**: {types_1}
**Description**: {description_1}


### Term 2: {term_2}

**Label** : {term_2}
**Types**: {types_2}
**Description**: {description_2}


**Output**:

*Please output a list of predicates relating Term 1 and Term 2*