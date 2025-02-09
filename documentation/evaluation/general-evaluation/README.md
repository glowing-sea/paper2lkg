## General Evaluation

With 100 abstract-only papers plus five full papers with two different LLM decoders, we created 204 different KGs `((100 + 5) * 2 = 210)`. The tables below show the general information about these KGs and the runtimes during the construction.

- **Pipeline Complexity**: Complexity Table  
- **Five-Full-Papers + LLaMA**: KG Full Paper LLaMA Table and Runtime Table  
- **Five-Full-Papers + GPT**: KG Full Paper GPT Table and Cost Table  
- **SciERC + LLaMA**: KG SciERC LLaMA Table and Runtime Table  
- **SciERC + GPT**: KG SciERC GPT Table and Cost Table  

The complexity table shows the theoretical complexity of each stage of the pipeline. They have been derived from the previous chapters. The complexity is measured by the number of times an LLM decoder is called. That is, for a single LLM decoder call, it is `O(1)`. Since a single LLM decoder call is dominantly expensive, the complexity of all the other computations, e.g., algorithmic processes, file IOs, and LLM decoder calls, can all be ignored. The meaning of each symbol in the complexity analysis is as follows:

- **L**: The length of the paper  
- **E**: The number of entities  
- **M**: The number of mentions  
- **R**: The number of relations (triples between any two entities)  

For the rest of the tables, the meaning of each column is as follows:

- **Length**: The length of the paper, measured in tokens.  
- **Entities**: The total number of entity nodes in the output KG.  
- **Mentions**: The total number of mention nodes in the output KG. Each entity has at least one mention. Different mentions may correspond to the same entity.  
- **Relations**: The number of relations (triples between any two entities) in the output KG.  
- **Isolated Entities**: The number of entities that are not related to any other entities in the output KG. That is, there is no outward edge from these entity nodes except those pointing to their attributes, e.g., their labels, aliases, and descriptions. Commonly speaking, the fewer, the better.  

The actual complexity of KGC using LLaMA is measured by time (minutes). We have found in the Background Chapter that the complexity of the LLM decoder is at least quadratic and potentially cubic. However, since each prompt our pipeline made is approximately the same length, and thus each LLM decoder call should take roughly the same constant amount of time, if we treat the time taken by each LLM decoder call as `O(1)`, the overall runtime should align with the theoretical complexity shown in the complexity table.

The actual complexity of KGC using GPT is measured by cost (USD). Since each LLM call is done through the OpenAI API, and the network speed and the server reaction time can be very unstable, we did not use time as our measurement. However, we found that the cost for each LLM call through the OpenAI API is about linearly proportional to the length of each prompt. Since each prompt our pipeline made is approximately the same length, and thus each prompt should have a similar cost, if we treat the cost by each LLM decoder call as `O(1)`, the overall cost should also align with the theoretical complexity shown in the complexity table.