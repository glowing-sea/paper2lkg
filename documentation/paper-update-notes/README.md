# Changes Regarding the Feedback

- **(Comment 1)**: The introduction to KG needs improvement.

  The introduction is rewritten and reorganised. The first paragraph in the original submit, about the how a KG is defined and looks like, is deleted because it is assumed knowledge in this workshop. Instead, the updated paper go straight to the application of KG, showing that KG is useful in Information Retrieval (IR) tasks. The example about IR with KG is changed from a tourism guide into paper.

  A review of recent academic KG is in the introduction, showing that there is a research gap in having detailed local representation in recent academic KGs, which is the main motivation of this research. Then, it links back to ASKG. This provide a broader view of the motivation of this research compared to the initial submission.

  A short paragraph about the outline of the paper is added to assist the reader in locating relevant content.

- **(Comment 2)**: There are several other academic KGs that have been developed, such as the Open Research Knowledge Graph, which are not discussed in the Related Work section.

  As mentioned, the review of several other academic KGs has been added to the new submission but not in the introduction section. We hope to make the Related Work section only focus on reviewing work about **open** **local** KGC using **generative LLMs**, which further reveal research gaps.

- **(Comment 3)**: The term 'holistic' needs to be defined more clearly.

  THe original submission of the paper contains the misuse of the term `holistic`. `holistic` in the pipeline only refer to **[Stage 4](../../paper2lkg-v0/src/modules/m05_global_relation_extraction/)**, where the Relations between Entities is extracted based on the context of the whole paper, instead of a limited context, such as a section, paragraph, and sentence only. Another feature of the pipeline is that it can extract any Entities without confining them to a predefined set of types as well as any Predicates. we also use the word `holistic` to describe this feature. However, the term `open` seems to be more suitable. Therefore, the term  `open` is replaced with `holistic` in most places, including the title. 

- **(Comment 4)**: The ontologies presented in the manuscript should be explained in more detail; currently, they are difficult to read and understand.

  A more detailed explanation about the input and output ontology is included in the first three paragraphs of Section 4 Pipeline Overview of the paper. It has defined what an Entity, Mention, Named Entity, General Concept, and Other Entity are. It should be more easy to understand. Legends are added into the graph showing how colours are related to IRI nodes and Literal nodes.

- **(Comment 5)** Figure 3 uses many different colors. Do they have specific meanings? How are they related to the categories General Concept, Named Entity, and Other?

  Using different colours only mean that all Mentions are considered different at this stage for now. For example, the Mentions `ANU` and `The Australian National University` are coloured differently until Stage 2 Entity Linking. Since it may cause confusion, in the revised version, we have coloured all mention into the same colours. In Figure 3: Stage Two Example, legends are included, showing how colours are related to Named Entity, General Concept, and Other Entity.

- **(Comment 6)** The difference between Entity and General Concept is somewhat unclear.

  General Concept is considered a subset of Entity in this research. Entity is everything. As mentioned before, the update version of the paper has all the necessary definition about Entity and General Concept in the first three paragraph of Section 4 Pipeline Overview.

- **(Comment 7)** I am not familiar with Disjoint Maximum Cliques. It would be helpful to explain this method, as it seems important for grouping Mentions.

  We have changed to wording of `Disjoint Maximum Cliques`. It is just the `maximum-sized partition of cliques` in the Mention graph. A detailed description can be found in Section 4.2, Entity Linking.

- **(Comment 8)** How should inconsistent results from broader/narrower contexts be handled?
  
  If inconsistent results are detected, e.g., an Entity is extracted as an Other Entity at the sentence level but is extracted as a Named Entity at the section level, the algorithm will be biased toward the result from a larger context. This is mentioned in the updated version of the paper.

- **(Comment 9)** In Algorithm 3, why are only Entities considered? What about General Concepts?

  As mentioned, General Concept is the subset of Entity. Therefore, all General Concepts are considered. General Concept and Entity have been clearly defined in the updated version.

- **(Comment 10)** Regarding fixing the missing links in the local KG, could it be overdone if the relations are not actually presented in the article?

  The step serves different purpose to Stage 3 Local Relation Extraction and Stage 4 Global Relation Extraction. This stage aims to extract relations that are hidden in sentence and can be easily missed in the previous two stages by focusing on taxonomic relations only. Yes, it is possible that relations that is not presented in the original article are extracted, which is mention in the paper as a limitation.

- **(Comment 11)** Prompts 5.1 and 5.2 are difficult to understand.

  The high-level prompts are written as well as the algorithm. It should be much clearer now.

- **(Comment 12)** In the Evaluation via Application section, which LLM is used as the generator in the Q&A Chatbot for 'RAG Answer,' or is it just a query answer from the KG?

  In general, the task of RAG is about combining IR and LLMs. Yes, LLMs are used in this evaluation task. If the original KG is created by LLaMA(Meta-Llama-3-8B-Instruct.Q4_0 ), then LLaMA is also use for the RAG test. The same applies for GPT(gpt-4o-mini).

- **(Comment 13)** The Conclusion needs further discussion, particularly in relation to the Expected Contribution.

  A paragraph about the whether the research goals set in Section 3: Related Work and Research Goals are achieved is added. Now the conclusion section is structured as follow: research summary, conclusion, and future work.

- **(Additional Changes)**

  The results of GPT is added to the Experiment Results section.

