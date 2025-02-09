# Named entity extraction

# Packages
from pathlib import Path
import sys
import os
import json
import time
from datetime import datetime
from FlagEmbedding import FlagModel
import numpy as np

# Add packages to sys.path
UTILITIES_RELATIVE_PATH = '../'
UTILITIES_ABSOLUTE_PATH = str((Path(__file__).parent / UTILITIES_RELATIVE_PATH).resolve())
if UTILITIES_ABSOLUTE_PATH not in sys.path:
    sys.path.append(UTILITIES_ABSOLUTE_PATH)

# Custom packages
from utilities.paper_access import get_text_from_section, get_text_from_paragraph, get_text
from utilities.llm_response_handler_JSON import call_llm_and_return_JSON, initialise_llm



def run(METHOD, INDEX, LLM_MODEL):

    llm = initialise_llm()


    CURRENT_DIR = Path(__file__).parent.resolve()


    KG_PATH = CURRENT_DIR / f"../../data/input/kg_ASKG_{INDEX}_{LLM_MODEL}.json"

    SAMPLE_ANSWER_PATH = CURRENT_DIR / f"../../data/input/QA/qa_expected_{INDEX}.json"

    ANSWER_PATH = CURRENT_DIR / f"../../data/output/QA/qa_actual_{INDEX}_{METHOD}_{LLM_MODEL}.json"

    PROMPT_PATH = CURRENT_DIR / f"prompt_2_template.md"

    PROMPT_PATH_1 = CURRENT_DIR / f"prompt_3_template.md"

    PROMPT_PATH_2 = CURRENT_DIR / f"prompt_3_template_old.md"

    model = FlagModel('BAAI/bge-base-en-v1.5',
            query_instruction_for_retrieval="Represent this sentence for searching relevant passages:",
            use_fp16=True)
    
    # Ensure logs folder exists
    LOGS_DIR = CURRENT_DIR / "logs"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH = LOGS_DIR / f"./log_{INDEX}_{METHOD}_{LLM_MODEL}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt"
 
    # =============================================================================
    # Prepare the named entity extraction module

    # Open the paper
    with open(KG_PATH, "r") as f:
        paper = json.load(f)

    # Open the prompt template
    with open(PROMPT_PATH, "r") as file:
        prompt_template = file.read()

    # Open the prompt template
    with open(PROMPT_PATH_1, "r") as file:
        prompt_template_1 = file.read()

    with open(SAMPLE_ANSWER_PATH, "r") as file:
        sample_answers = json.load(file)

    # Open the prompt template
    with open(PROMPT_PATH_2, "r") as file:
        prompt_template_2 = file.read()

    # =============================================================================

    # =============================================================================

    # Traditional RAG

    if METHOD == "DDM":

        # Embed all sentences
        sentences = []
        for section in paper['sections']:
            for paragraph in section['paragraphs']:
                for sentence in paragraph['sentences']:
                    sentences.append(get_text(sentence))

        sentence_embeddings = [model.encode(sentence) for sentence in sentences]


        # Answer each question
        for question_answer_pair in sample_answers:
            question = question_answer_pair['question']
            question_embedding = model.encode(question)
            similarity_scores = []

            for sentence_embedding in sentence_embeddings:
                similarity_scores.append(np.dot(question_embedding, sentence_embedding) / (np.linalg.norm(question_embedding) * np.linalg.norm(sentence_embedding)))

            # Top 10 similar sentences
            top_10_indices = np.argsort(similarity_scores)[-10:][::-1]
            top_10_sentences = [sentences[i] for i in top_10_indices]

            # Generate the prompt
            prompt = prompt_template_2.format(
                question=question,
                resources='\n\n'.join(top_10_sentences)
            )

            # Call the LLM
            response, log, original_response = call_llm_and_return_JSON(llm, prompt)

            if original_response:
                if response and "answer" in response:
                    question_answer_pair["LLM_answer"] = response["answer"]
                else:
                    print("Error: JSON Parsing Error. Force Retrial")
                    question_answer_pair["LLM_answer"] = original_response

            else:
                print("Error: No response")
                question_answer_pair["LLM_answer"] = ""


            with open(LOG_PATH, "a") as file:
                file.write(log)
                file.write("\n\n\n\n")
                file.flush()

    elif METHOD == "LKG":
        # Embed all entities
        for iri, node in paper['nodes'].items():
            node['embedding'] = model.encode(node['label'])
            node["iri"] = iri


        # Answer each question
        for question_answer_pair in sample_answers:
            question = question_answer_pair['question']

            # Extract Keywords

            prompt = prompt_template.format(
                question=question
            )

            response, log, original_response = call_llm_and_return_JSON(llm, prompt)

            if response and "keywords" in response:
                if isinstance(response["keywords"], list):
                    keywords = response["keywords"]
            else:
                keywords = [question]
                print("Error: JSON Parsing Error. Use the whole question as keywords")

            print(keywords)

            # For each keyword, find the closest entity in the KG
            matching_entities = {}

            for keyword in keywords:
                keyword_embedding = model.encode(keyword)

                max_similarity = -1
                max_entity = None

                for iri, node in paper['nodes'].items():
                    similarity = np.dot(keyword_embedding, node['embedding']) / (np.linalg.norm(keyword_embedding) * np.linalg.norm(node['embedding']))
                    if similarity > max_similarity:
                        max_similarity = similarity
                        max_entity = node

                if max_entity:
                    matching_entities[max_entity["iri"]] = max_entity
                    


            print(matching_entities.keys())


            # Get all relevant triples

            relevant_triples = []

            for triples in paper['triples']:
                if triples[0] in matching_entities or triples[2] in matching_entities:
                    relevant_triples.append(triples)

            print(len(relevant_triples))



            # Add more relevant entities

            for triple in relevant_triples:
                subject = triple[0]
                object = triple[2]

                if subject not in matching_entities:
                    matching_entities[subject] = paper['nodes'][subject]

                if object not in matching_entities:
                    matching_entities[object] = paper['nodes'][object]



            entities_prompt = []

            # Create the prompt

            for entity in matching_entities.values():
                entities_prompt.append({
                    "entity": entity["label"],
                    "aliases": entity["aliases"],
                    "description": entity["description"]
                })

            triples_prompt = []

            for triple in relevant_triples:
                triples_prompt.append((
                    paper["nodes"][triple[0]]["label"],
                    paper["predicates"][triple[1]]["label"],
                    paper["nodes"][triple[2]]["label"]
                ))

            prompt = prompt_template_1.format(
                entities=json.dumps(entities_prompt, indent=2),
                triples=json.dumps(triples_prompt, indent=2),
                question=question
            )


            # Call the LLM
            response, log, original_response = call_llm_and_return_JSON(llm, prompt)

            if original_response:
                if response and "answer" in response:
                    question_answer_pair["LLM_answer"] = response["answer"]
                else:
                    print("Error: JSON Parsing Error. Force Retrial")
                    question_answer_pair["LLM_answer"] = original_response

            else:
                print("Error: No response")
                question_answer_pair["LLM_answer"] = ""


            with open(LOG_PATH, "a") as file:
                file.write(log)
                file.write("\n\n\n\n")
                file.flush()
    else:
        raise ValueError("Invalid Input")

    # =============================================================================

    # Calculate Similarity Score

    for question_answer_pair in sample_answers:
        sample_answer = question_answer_pair["answer"]
        llm_answer = question_answer_pair["LLM_answer"]

        sample_answer_embedding = model.encode(sample_answer)
        llm_answer_embedding = model.encode(llm_answer)

        similarity_score = np.dot(sample_answer_embedding, llm_answer_embedding) / (np.linalg.norm(sample_answer_embedding) * np.linalg.norm(llm_answer_embedding))

        question_answer_pair["similarity_score"] = float(similarity_score)

    # =============================================================================

    with open(ANSWER_PATH, "w") as file:
        json.dump(sample_answers, file, indent=2)


if __name__ == "__main__":
    METHOD = "LKG"
    # METHOD = "DDM"

    LLM_MODEL = "l"
    # LLM_MODEL = "g"

    for i in range(1,6):
        run(METHOD, i, LLM_MODEL)

