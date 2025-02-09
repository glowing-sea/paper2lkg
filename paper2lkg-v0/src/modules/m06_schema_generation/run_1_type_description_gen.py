# Named entity extraction

# Packages
from pathlib import Path
import sys
import os
import json
import time
import numpy as np
from datetime import datetime
# from FlagEmbedding import FlagModel

# Add packages to sys.path
UTILITIES_RELATIVE_PATH = '../../'
UTILITIES_ABSOLUTE_PATH = str((Path(__file__).parent / UTILITIES_RELATIVE_PATH).resolve())
if UTILITIES_ABSOLUTE_PATH not in sys.path:
    sys.path.append(UTILITIES_ABSOLUTE_PATH)

# Custom packages
from utilities.llm_response_handler_JSON import call_llm_and_return_JSON, initialise_llm, PROMPT_LIMIT
from utilities.paper_access import get_text_from_section, get_text_from_paragraph, get_text
from utilities.content_processor import tokenise_text, lemmatise_text


MODULE ='m06'
STAGE = 1

CURRENT_DIR = Path(__file__).parent.resolve()
OLD_KG_PATH = CURRENT_DIR / f"../m05_global_relation_extraction/kg_4.json"
NEW_KG_PATH = CURRENT_DIR / f"kg_{STAGE}.json"

# PROMPT_PATH_CONTENT = CURRENT_DIR / f"prompt_{STAGE}_content.md"
# PROMPT_PATH_INSTRUCTION = CURRENT_DIR / f"prompt_{STAGE}_instruction.md"

PROMPT_PATH_TEMPLATE = CURRENT_DIR / f"prompt_{STAGE}.md"

TIME = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')


# Ensure logs folder exists
LOGS_DIR = CURRENT_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Define log path
LOG_PATH = LOGS_DIR / f"{MODULE}_log_{STAGE}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt"



TERMINAL_PATH = CURRENT_DIR / f"./logs/{MODULE}_terminal_{STAGE}_{TIME}.txt"


def run():


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


    # with open(PROMPT_PATH_CONTENT, "r") as file:
    #     prompt_template_content = file.read()

    # with open(PROMPT_PATH_INSTRUCTION, "r") as file:
    #     prompt_template_instruction = file.read()

    with open(PROMPT_PATH_TEMPLATE, "r") as file:
        prompt_template = file.read()


    # model = FlagModel('BAAI/bge-m3',
    #         query_instruction_for_retrieval=prompt_template_instruction,
    #         use_fp16=True)

    # =============================================================================

    type_labels_count = 0
    type_nodes = {}

    for node in paper["nodes"].values():
        for type_label in node["types"]:
            # type_count += 1
            # type_dict[type]
            type_label_normalised = " ".join(lemmatise_text(tokenise_text(type_label)))
            if type_label_normalised not in type_nodes:
                type_nodes[type_label_normalised] = {
                    "label": type_label,
                    "aliases": [type_label],
                }
            else:
                type_nodes[type_label_normalised]["aliases"].append(type_label)
            type_labels_count += 1

    for type_node in type_nodes.values():
        type_node["aliases"] = list(set(type_node["aliases"]))


    print(f"Number of type labels: {type_labels_count}")
    print(f"Number of unique type labels (type node): {len(type_nodes)}")


    paper["type_nodes"] = type_nodes

    # =============================================================================
    # Normalised Alias

    for node in paper["nodes"].values():
        node["aliases_normalised"] = []
        for alias in node["aliases"]:
            alias_normalised = " ".join(lemmatise_text(tokenise_text(alias)))
            node["aliases_normalised"].append(alias_normalised)

    # =============================================================================
    # Alias Matching

    for type_node_label_normalised, type_node in type_nodes.items():
        type_node["matching_iris"] = []

        for iri, node in paper["nodes"].items():
            if type_node_label_normalised in node["aliases_normalised"]:
                type_node["matching_iris"].append(iri)
        
        if len(type_node["matching_iris"]) == 1:
            print(type_node["matching_iris"][0])
        if len(type_node["matching_iris"]) > 1:
            print("Warning: Multiple IRLs for the same type label")
            print(type_node["matching_iris"][0])
            
    # =============================================================================
    # Description Generation

    for type_node in type_nodes.values():
        label = type_node["label"]

        prompt = prompt_template.format(
            label=label
        )



        description, log, _ = call_llm_and_return_JSON(llm, prompt)

        if description == None or "description" not in description:
            description = ""
            print(f"Warning: description of '{label}' not found. Assume empty.")
        else:
            description = str(description["description"])

        type_node["description"] = description


        with open(LOG_PATH, "a") as file:
            file.write(log)
            file.write("\n\n\n\n")
            file.flush()





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
    run()