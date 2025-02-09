# Named entity extraction

# Packages
from pathlib import Path
import sys
import os
import json
import time
from datetime import datetime

# Add packages to sys.path
UTILITIES_RELATIVE_PATH = '../'
UTILITIES_ABSOLUTE_PATH = str((Path(__file__).parent / UTILITIES_RELATIVE_PATH).resolve())
if UTILITIES_ABSOLUTE_PATH not in sys.path:
    sys.path.append(UTILITIES_ABSOLUTE_PATH)

# Custom packages
from utilities.llm_response_handler_JSON import call_llm_and_return_JSON, initialise_llm
from utilities.paper_access import get_text_from_section, get_text_from_paragraph, get_text



def run(DATASET, INDEX, LLM_MODEL):


    CURRENT_DIR = Path(__file__).parent.resolve()
    OLD_KG_PATH = CURRENT_DIR / f"../../data/input/kg_{DATASET}_{INDEX}_{LLM_MODEL}.json"
    NEW_KG_PATH = CURRENT_DIR / f"../../data/output/kg_{DATASET}_{INDEX}_{LLM_MODEL}.json"
    PROMPT_PATH = CURRENT_DIR / f"prompt_1_template.md"

    # Ensure logs folder exists
    LOGS_DIR = CURRENT_DIR / "logs"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Define log path
    LOG_PATH = LOGS_DIR / f"./test_log_{INDEX}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt"

    # =============================================================================
    # Prepare the named entity extraction module

    """
    Run the named entity extraction module
    """

    start_time = time.time()

    # Initialise the llm
    llm = initialise_llm()

    # Open the paper
    with open(OLD_KG_PATH, "r") as f:
        paper = json.load(f)


    # Open the prompt template
    with open(PROMPT_PATH, "r") as file:
        prompt_template = file.read()

    # =============================================================================
    TRIPLES_PER_PROMPT = 20

    paper["triples"] += paper["triples_typing"]
    paper.pop("triples_typing")


    print(len(paper["nodes"]))
    print(len(paper["triples"]))

    for triple in paper["triples"]:
        subject_relevance = paper["nodes"][triple[0]]["relevance"]
        object_relevance = paper["nodes"][triple[2]]["relevance"]
        triple.append(subject_relevance + object_relevance)

    paper["triples"] = sorted(paper["triples"], key=lambda x: x[3], reverse=True)

    paper["kg2text"] = []

    for i in range(0, len(paper["triples"]), TRIPLES_PER_PROMPT):
        triples = paper["triples"][i: i + TRIPLES_PER_PROMPT]

        entities = {}

        for triple in triples:
            if triple[0] not in entities:
                entities[triple[0]] = paper["nodes"][triple[0]]
            if triple[2] not in entities:
                entities[triple[2]] = paper["nodes"][triple[2]]

        entities_prompt = []

        for entity in entities.values():
            entities_prompt.append({
                "entity": entity["label"],
                "aliases": entity["aliases"],
                "description": entity["description"]
            })

        triples_prompt = []

        for triple in triples:
            triples_prompt.append((
                paper["nodes"][triple[0]]["label"],
                paper["predicates"][triple[1]]["label"],
                paper["nodes"][triple[2]]["label"]
            ))

        prompt = prompt_template.format(
            entities=json.dumps(entities_prompt, indent=2),
            triples=json.dumps(triples_prompt, indent=2)
        )

        response, log, original_response = call_llm_and_return_JSON(llm, prompt)

        if original_response:
            if response and "paragraph" in response:
                paragraph = response["paragraph"]
            else:
                print("Error: JSON Parsing Error. Force Retrial")
                paragraph = original_response

            paper["kg2text"].append(paragraph)

        else:
            print("Error: No response")

        with open(LOG_PATH, "a") as f:
            f.write(log + "\n\n\n\n")
            f.flush()

    paper.pop("times")
    paper.pop("nodes")
    paper.pop("triples")
    paper.pop("predicates")

    # =============================================================================
    # Tidy up and save the KG


    finish_time = time.time() - start_time
    print(f"Finished in {finish_time} seconds")
    if "times" not in paper:
        paper["times"] = []
    paper["times"].append(finish_time)


    # Save the KG
    with open(NEW_KG_PATH, "w") as f:
        json.dump(paper, f, indent=2)


if __name__ == "__main__":
    DATASET = "SciERC"
    INDICES = list(range(100, 101))

    for INDEX in INDICES:
        LLM_MODEL = "g"
        run(DATASET, INDEX, LLM_MODEL)
