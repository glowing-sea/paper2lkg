# Named entity extraction

# Packages
from pathlib import Path
import sys
import os
import json
import time
import numpy as np
from datetime import datetime
from FlagEmbedding import FlagModel

# Add packages to sys.path
UTILITIES_RELATIVE_PATH = '../../'
UTILITIES_ABSOLUTE_PATH = str((Path(__file__).parent / UTILITIES_RELATIVE_PATH).resolve())
if UTILITIES_ABSOLUTE_PATH not in sys.path:
    sys.path.append(UTILITIES_ABSOLUTE_PATH)

# Custom packages
from utilities.llm_response_handler_JSON import call_llm_and_return_JSON, initialise_llm, PROMPT_LIMIT
from utilities.paper_access import get_text_from_section, get_text_from_paragraph, get_text
from utilities.content_processor import tokenise_text


MODULE ='m05'
STAGE = 2

CURRENT_DIR = Path(__file__).parent.resolve()
OLD_KG_PATH = CURRENT_DIR / f"kg_{STAGE-1}.json"
NEW_KG_PATH = CURRENT_DIR / f"kg_{STAGE}.json"
PROMPT_PATH_CONTENT = CURRENT_DIR / f"prompt_{STAGE}_content.md"
PROMPT_PATH_INSTRUCTION = CURRENT_DIR / f"prompt_{STAGE}_instruction.md"

TIME = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
LOG_PATH = CURRENT_DIR / f"./logs/{MODULE}_log_{STAGE}_{TIME}.txt"
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


    with open(PROMPT_PATH_CONTENT, "r") as file:
        prompt_template_content = file.read()

    with open(PROMPT_PATH_INSTRUCTION, "r") as file:
        prompt_template_instruction = file.read()

    file = open(LOG_PATH, "w")


    model = FlagModel('BAAI/bge-m3',
            query_instruction_for_retrieval=prompt_template_instruction,
            use_fp16=True)
    
    


    # =============================================================================
    # Embed the paper summary

    summary = paper["summary"]
    summary_embedding = model.encode(summary)
    paper["summary_embedding"] = summary_embedding

    # =============================================================================
    # Embed the nodes

    for node in paper["nodes"].values():
        description = node["description"]
        types = str(node["types"])
        label = node["label"]

        # Encode the label, types and description
        prompt = prompt_template_content.format(label=label, types=types, description=description)
        node_embedding = model.encode(prompt)
        node_embedding = node_embedding

        log = prompt_template_instruction + "\n" + prompt + "\n\n"
        print(log, file=file)

        node["embedding"] = node_embedding

    # =============================================================================
    # Finding relevant entities

    for node in paper["nodes"].values():
        node["relevance"] = float(node["embedding"] @ paper["summary_embedding"].T / (np.linalg.norm(node["embedding"]) * np.linalg.norm(paper["summary_embedding"])))
        del node["embedding"]

    del paper["summary_embedding"]

    # =============================================================================
    # Sort based on relevance

    # Sorting based on relevance
    # https://chatgpt.com/c/6710989b-58c4-8010-86a0-532a030eade7
    sorted_nodes = dict(sorted(paper["nodes"].items(), key=lambda item: item[1]["relevance"], reverse=True))

    paper["nodes"] = sorted_nodes

    # =============================================================================
    # Tidy up and save the KG


    finish_time = time.time() - start_time
    print(f"Finished in {finish_time} seconds")
    if "times" not in paper:
        paper["times"] = []
    paper["times"].append(finish_time)

    file.close()

    # Save the KG
    with open(NEW_KG_PATH, "w") as f:
        json.dump(paper, f, indent=2)


if __name__ == "__main__":
    run()