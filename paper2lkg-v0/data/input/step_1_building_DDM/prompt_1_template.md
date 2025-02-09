## Task Definition

You are a linguistic expert. Given a piece of unstructured raw text directly extracted from a PDF. You need to tidy it up and tokenise into a hierarchy of paragraphs and sections. You need to remove any citation markers in the text like [1]. You need to remove or fix any unrecognised characters. Convert machematically formula smartly. Ensure all characters are in ASCII. You should combine sentences into paragraphs and convert tables into sentences smartly.

## Output Format

Please write your answer in JSON format, consisting of zero or more entity-type pairs, as shown below:

```
{{
            "paragraphs": [
                {{
                    "sentences": [
                        "Content of Paragraph 1 Sentence 1"
                    ]
                }},
                {{
                    "sentences": [
                        "Content of Paragraph 2 Sentence 2"
                    ]
                }}
            ]
}}
```

## Input

{text}

## Output:

*Please write your answer*