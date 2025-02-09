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
STAGE = 3

CURRENT_DIR = Path(__file__).parent.resolve()
OLD_KG_PATH = CURRENT_DIR / f"kg_{STAGE-1}.json"
NEW_KG_PATH = CURRENT_DIR / f"kg_{STAGE}.json"

# PROMPT_PATH_CONTENT = CURRENT_DIR / f"prompt_{STAGE}_content.md"
# PROMPT_PATH_INSTRUCTION = CURRENT_DIR / f"prompt_{STAGE}_instruction.md"

PROMPT_PATH_TEMPLATE = CURRENT_DIR / f"prompt_{STAGE}.md"

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
    # Description Generation

    count = 0
    for edges in paper["edges"] + paper["document_level_edges"] + paper["type_edges"][:10]:
        count += 1

    print(f"Total number of edges: {count}")

    for edge in paper["edges"] + paper["document_level_edges"] + paper["type_edges"][:10]:
        subject = paper["nodes"][edge[0]]["label"]
        predicate = edge[1]
        object = paper["nodes"][edge[2]]["label"]
        edge.append("")

        prompt = prompt_template.format(subject=subject, predicate=predicate, object=object)


        description, log, _ = call_llm_and_return_JSON(llm, prompt)
        
        if description != None:
            if "description" in description and description["description"]:
                edge[3] = str(description["description"])
            else:
                print(f"Warning: description of '{predicate}' not found. Assume empty.")

        else:
            print(f"Warning: description and canonical of '{predicate}' not found. Assume empty.")

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