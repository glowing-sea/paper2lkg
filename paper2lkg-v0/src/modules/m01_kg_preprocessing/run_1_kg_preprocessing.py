# Named entity extraction

# Packages
from pathlib import Path
import sys
import os
import json
import time
from datetime import datetime

# Add packages to sys.path
UTILITIES_RELATIVE_PATH = '../../'
UTILITIES_ABSOLUTE_PATH = str((Path(__file__).parent / UTILITIES_RELATIVE_PATH).resolve())
if UTILITIES_ABSOLUTE_PATH not in sys.path:
    sys.path.append(UTILITIES_ABSOLUTE_PATH)

# Custom packages
# from utilities.llm_response_handler_JSON_list import call_llm_and_return_a_list, initialise_llm
# from utilities.paper_access import get_text_from_section, get_text_from_paragraph, get_text


MODULE ='m01'
STAGE = 1

CURRENT_DIR = Path(__file__).parent.resolve()
# PROMPT_PATH = CURRENT_DIR / f"prompt_{STAGE}_template.md"
# PROMPT_EXAMPLE_PATH = CURRENT_DIR / f"prompt_{STAGE}_examples.json"
# LOG_PATH = CURRENT_DIR / f"./logs/{MODULE}_log_{STAGE}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt"

# Ensure logs folder exists
LOGS_DIR = CURRENT_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Define log path
LOG_PATH = LOGS_DIR / f"{MODULE}_log_{STAGE}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt"



def run(dataset, paper_index):

    OLD_KG_PATH = CURRENT_DIR / f"../../../data/input/kg_{dataset}_{paper_index}.json"
    NEW_KG_PATH = CURRENT_DIR / f"kg_{STAGE}.json"


    # =============================================================================
    # Prepare the named entity extraction module

    """
    Run the named entity extraction module
    """

    start_time = time.time()


    # Open the paper
    with open(OLD_KG_PATH, "r") as f:
        paper = json.load(f)

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
    dataset = "val"
    paper_index =1
    run(dataset, paper_index)