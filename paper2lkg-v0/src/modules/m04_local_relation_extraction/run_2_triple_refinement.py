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
from utilities.paper_access import get_text_from_section, get_text_from_paragraph, get_text


MODULE ='m04'
STAGE = 2

CURRENT_DIR = Path(__file__).parent.resolve()
OLD_KG_PATH = CURRENT_DIR / f"kg_{STAGE-1}.json"
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
        prompt_examples = json.load(file)

    file = open(LOG_PATH, "w")
    terminal = open(TERMINAL_PATH, "w")


    input_output_pairs = prompt_examples["input_output_pairs"]

    def prints(*args):
        print(*args, file=terminal)
        print(*args)

    # =============================================================================
    # Extract named entities


    def lre(chunk, triples):

        new_triples = []

        for triple in triples:
            if triple["object"] == "" or triple["object"] == "None":
                prints("Found a triple with an empty object")
                prints(json.dumps(triple, indent=2))

                input_actual = {
                    "S": triple["subject"],
                    "VO": triple["predicate"]
                }

                prompt = prompt_template.format(
                    input_example_1 = json.dumps(input_output_pairs[0]["input"], indent=2),
                    output_example_1 = json.dumps(input_output_pairs[0]["output"], indent=2),
                    input_example_2 = json.dumps(input_output_pairs[1]["input"], indent=2),
                    output_example_2 = json.dumps(input_output_pairs[1]["output"], indent=2),
                    input_example_3 = json.dumps(input_output_pairs[2]["input"], indent=2),
                    output_example_3 = json.dumps(input_output_pairs[2]["output"], indent=2),
                    input_actual = json.dumps(input_actual, indent=2)
                    )
                
                response, log, original_response = call_llm_and_return_JSON(llm, prompt)

                if response:
                    if ("S" in response and 
                        "V" in response and 
                        "O" in response and 
                        response["S"] and
                        response["V"] and
                        response["O"]):
                        
                        triple["subject"] = str(response["S"])
                        triple["predicate"] = str(response["V"])
                        triple["object"] = str(response["O"])
                        new_triples.append(triple)

                        prints("Decomposed the triple successfully")
                        prints(json.dumps(triple, indent=2))
                    else:
                        prints("Failed to decompose the triple")
                else:
                    prints("Failed to decompose the triple")

                
                file.write(log)
                file.write("\n\n\n\n")
                file.flush()
            
            else:
                new_triples.append(triple)

        chunk["triples"] = new_triples


    

    # Extract sentence-level named entities
    for section in paper["sections"]:
        for paragraph in section["paragraphs"]:
            for sentence in paragraph["sentences"]:
                lre(sentence, sentence["triples"])

            lre(paragraph, paragraph["triples"])

        lre(section, section["triples"])
    

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