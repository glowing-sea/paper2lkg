# put paragraph and section-level mentions back to its original sentence level
# classifying the mentions through set subtraction

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
from utilities.llm_response_handler_JSON import call_llm_and_return_JSON, initialise_llm
from utilities.paper_access import get_text
from utilities.content_processor import check_existence_in_sentence, tokenise_text, lemmatise_text


MODULE ='m03'
STAGE = 2

CURRENT_DIR = Path(__file__).parent.resolve()
OLD_KG_PATH = CURRENT_DIR / f"kg_{STAGE-1}.json"
NEW_KG_PATH = CURRENT_DIR / f"kg_{STAGE}.json"
PROMPT_PATH = CURRENT_DIR / f"prompt_{STAGE}.md"
LOG_PATH = CURRENT_DIR / f"./logs/{MODULE}_log_{STAGE}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt"



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

    with open(PROMPT_PATH, "r") as file:
        prompt_template = file.read()

    # =============================================================================
    # Test familiarity
    for node in paper["nodes"]:
        prompt = prompt_template.format(term=node["label"])

        familiarity, log, original_response = call_llm_and_return_JSON(llm, prompt)

        if (familiarity == None 
            or "familiar" not in familiarity 
            or familiarity["familiar"] not in [True, False]):
            
            print(f"Warning: JSON parsing error. Try String Matching instead.")

            if '"familiar": true' in original_response:
                print("String Matching successful. Set familiarity to True.")
                node["LLM_familiarity"] = True
            elif '"familiar": false' in original_response:
                print("String Matching successful. Set familiarity to False.")
                node["LLM_familiarity"] = False
            else:
                print("Warning: String Matching failed. Set familiarity to False.")
                node["LLM_familiarity"] = False
        else:
            node["LLM_familiarity"] = familiarity["familiar"]

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