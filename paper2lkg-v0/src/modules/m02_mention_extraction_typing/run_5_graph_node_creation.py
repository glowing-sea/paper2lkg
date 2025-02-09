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
from utilities.llm_response_handler_JSON_list import call_llm_and_return_a_list, initialise_llm
from utilities.paper_access import get_text
from utilities.content_processor import check_existence_in_sentence, tokenise_text, lemmatise_text


MODULE ='m02'
STAGE = 5

CURRENT_DIR = Path(__file__).parent.resolve()
OLD_KG_PATH = CURRENT_DIR / f"kg_{STAGE - 1}.json"
NEW_KG_PATH = CURRENT_DIR / f"kg_{STAGE}.json"


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


    # =============================================================================
    # Record the classification information into the mention nodes themselves

    for section in paper["sections"]:
        for paragraph in section["paragraphs"]:
            for sentence in paragraph["sentences"]:
                for named_entity in sentence["named_entities"].values():
                    named_entity["node_type"] = "named entity"
                for general_term in sentence["general_terms"].values():
                    general_term["node_type"] = "general term"
                for other in sentence["others"].values():
                    other["node_type"] = "other"

    # =============================================================================
    # Put entities from their original sentences to the paper level, while maintaining the references

    def create_node(node, sentence, normalised_label):
        node["normalised_label"] = normalised_label
        node["mentions"] = []
        mention = {
            "reference": sentence["iri"],
            "local_name": node["label"],
            "local_types" : node["types"],
        }
        node["mentions"].append(mention)
        return node


    paper["nodes"] = []

    for section in paper["sections"]:
        for paragraph in section["paragraphs"]:
            for sentence in paragraph["sentences"]:
                for normalised, named_entity in sentence["named_entities"].items():
                    node = create_node(named_entity, sentence, normalised)
                    paper["nodes"].append(node)
                for normalised, general_term in sentence["general_terms"].items():
                    node = create_node(general_term, sentence, normalised)
                    paper["nodes"].append(node)
                for normalised, other in sentence["others"].items():
                    node = create_node(other, sentence, normalised)
                    paper["nodes"].append(node)
                sentence.pop("named_entities")
                sentence.pop("general_terms")
                sentence.pop("others")


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