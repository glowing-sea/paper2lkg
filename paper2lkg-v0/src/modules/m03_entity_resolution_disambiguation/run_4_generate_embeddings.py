# put paragraph and section-level mentions back to its original sentence level
# classifying the mentions through set subtraction

# Packages
from pathlib import Path
import sys
import os
import json
import time
from datetime import datetime
from FlagEmbedding import FlagModel

# Add packages to sys.path
UTILITIES_RELATIVE_PATH = '../../'
UTILITIES_ABSOLUTE_PATH = str((Path(__file__).parent / UTILITIES_RELATIVE_PATH).resolve())
if UTILITIES_ABSOLUTE_PATH not in sys.path:
    sys.path.append(UTILITIES_ABSOLUTE_PATH)

# Custom packages
from utilities.paper_access import get_text, get_sentence_from_iri, get_section_from_sentence
from utilities.content_processor import check_existence_in_sentence, tokenise_text, lemmatise_text


MODULE ='m03'
STAGE = 4

CURRENT_DIR = Path(__file__).parent.resolve()
OLD_KG_PATH = CURRENT_DIR / f"kg_{STAGE-1}.json"
NEW_KG_PATH = CURRENT_DIR / f"kg_{STAGE}.json"
PROMPT_PATH_CONTENT = CURRENT_DIR / f"prompt_{STAGE}_content.md"
PROMPT_PATH_INSTRUCTION = CURRENT_DIR / f"prompt_{STAGE}_instruction.md"
LOG_PATH = CURRENT_DIR / f"./logs/{MODULE}_log_{STAGE}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt"



def run():


    # =============================================================================
    # Prepare the named entity extraction module

    """
    Run the named entity extraction module
    """

    start_time = time.time()

    # Open the paper
    with open(OLD_KG_PATH, "r") as f:
        paper = json.load(f)

    with open(PROMPT_PATH_CONTENT, "r") as file:
        prompt_template_content = file.read()

    with open(PROMPT_PATH_INSTRUCTION, "r") as file:
        prompt_template_instruction = file.read()

    model = FlagModel('BAAI/bge-base-en-v1.5',
            query_instruction_for_retrieval=prompt_template_instruction,
            use_fp16=True)

    # =============================================================================
    # Test familiarity
    for node in paper["nodes"]:
        description = node["description"]
        types = str(node["types"])
        label = node["label"]

        # Encode the label
        label_embedding = model.encode(label)
        label_embedding = [float(x) for x in label_embedding]

        # Encode the description
        description_embedding = model.encode(description)
        description_embedding = [float(x) for x in description_embedding]

        # Encode the label, types and description
        prompt = prompt_template_content.format(label=label, types=types, description=description)
        node_embedding = model.encode(prompt)
        node_embedding = [float(x) for x in node_embedding]

        log = prompt_template_instruction + "\n" + prompt + "\n\n"

        node["label_embedding"] = label_embedding
        node["description_embedding"] = description_embedding
        node["node_embedding"] = node_embedding
        
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