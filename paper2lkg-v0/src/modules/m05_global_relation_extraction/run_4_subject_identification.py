# Named entity extraction

# Packages
from pathlib import Path
import sys
import os
import json
import time
import math
from difflib import SequenceMatcher
from datetime import datetime

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
STAGE = 4

CURRENT_DIR = Path(__file__).parent.resolve()
OLD_KG_PATH = CURRENT_DIR / f"kg_{STAGE - 1}.json"
NEW_KG_PATH = CURRENT_DIR / f"kg_{STAGE}.json"
PROMPT_PATH = CURRENT_DIR / f"prompt_{STAGE}_template.md"
PROMPT_EXAMPLE_PATH = CURRENT_DIR / f"prompt_{STAGE}_examples.json"

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


    # Open the prompt template
    with open(PROMPT_PATH, "r") as file:
        prompt_template = file.read()

    # Open the prompt example
    with open(PROMPT_EXAMPLE_PATH, "r") as file:
        prompt_example = json.load(file)

    format_example = prompt_example["format_example"]

    file = open(LOG_PATH, "w")
    terminal = open(TERMINAL_PATH, "w")


    def prints(*args):
        print(*args, file=terminal)
        print(*args)

    # =============================================================================

    new_edges = []

    for edge in paper["document_level_edges"]:
        original_subject_id = edge[0]
        predicate = edge[1]
        original_object_id = edge[2]

        # Get the subject and object nodes
        original_subject_node = paper["nodes"][original_subject_id]
        original_object_node = paper["nodes"][original_object_id]

        # Get the subject and object descriptions
        subject_description = original_subject_node["description"]
        object_description = original_object_node["description"]

        # Get the subject and object types
        subject_types = original_subject_node["types"]
        object_types = original_object_node["types"]

        # Get the subject and object labels
        subject_label = original_subject_node["label"]
        object_label = original_object_node["label"]

        # Prepare the prompt
        prompt = prompt_template.format(
            subject_label=subject_label,
            subject_types=str(subject_types),
            subject_description=subject_description,
            object_label=object_label,
            object_types=str(object_types),
            object_description=object_description,
            predicate=predicate,

            format_example=json.dumps(format_example, indent=2)
        )

        # Call the llm

        response, log, _ = call_llm_and_return_JSON(llm, prompt)

        
        if response and "subject" in response and "object" in response:
            new_subject = response["subject"]
            new_object = response["object"]

            sim_1 = SequenceMatcher(None, subject_label, new_subject).ratio()
            sim_2 = SequenceMatcher(None, object_label, new_subject).ratio()

            if sim_1 > sim_2:
                new_edge = [original_subject_id, predicate, original_object_id]
                new_edges.append(new_edge)
                prints(new_edge[0])
                prints(new_edge[1])
                prints(new_edge[2])
                print()
            else:
                new_edge = [original_object_id, predicate, original_subject_id]
                new_edges.append(new_edge)
                prints(new_edge[0])
                prints(new_edge[1])
                prints(new_edge[2])
                print()
        else:
            prints(f"Subject Identification Failed between {subject_label} - {predicate} - {object_label}")

        file.write(log)
        file.write("\n\n\n\n")
        file.flush()

    paper["document_level_edges"] = new_edges

    # =============================================================================
    # Tidy up and save the KG


    finish_time = time.time() - start_time
    prints(f"Finished in {finish_time} seconds")
    if "times" not in paper:
        paper["times"] = []
    paper["times"].append(finish_time)


    # Save the KG
    with open(NEW_KG_PATH, "w") as f:
        json.dump(paper, f, indent=2)

    file.close()
    terminal.close()


if __name__ == "__main__":
    run()