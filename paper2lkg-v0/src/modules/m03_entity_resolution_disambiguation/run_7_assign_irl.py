# put paragraph and section-level mentions back to its original sentence level
# classifying the mentions through set subtraction

# Packages
from pathlib import Path
import sys
import os
import json
import time
from datetime import datetime
import numpy as np

# Add packages to sys.path
UTILITIES_RELATIVE_PATH = '../../'
UTILITIES_ABSOLUTE_PATH = str((Path(__file__).parent / UTILITIES_RELATIVE_PATH).resolve())
if UTILITIES_ABSOLUTE_PATH not in sys.path:
    sys.path.append(UTILITIES_ABSOLUTE_PATH)

# Custom packages
from utilities.paper_access import get_text, get_sentence_from_iri, get_section_from_sentence
from utilities.content_processor import check_existence_in_sentence, tokenise_text, lemmatise_text, sanitise_iri


MODULE ='m03'
STAGE = 7

CURRENT_DIR = Path(__file__).parent.resolve()
OLD_KG_PATH = CURRENT_DIR / f"kg_{STAGE-1}.json"
NEW_KG_PATH = CURRENT_DIR / f"kg_{STAGE}.json"
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

    # =============================================================================

    # Assign Node IDs

    distinct_ids = set()
    disambiguated_ids = set()

    for node in paper["nodes"].values():
        candidate_id = sanitise_iri(node["normalised_label"])

        disambiguation_index = 0

        if candidate_id in distinct_ids:
            print(f"Node ID '{candidate_id}' already exists. Disambiguating...")
            disambiguation_index = 1
            while f"{candidate_id}_{disambiguation_index}" in disambiguated_ids:
                disambiguation_index += 1
            disambiguated_ids.add(f"{candidate_id}_{disambiguation_index}")
            candidate_id = f"{candidate_id}_({disambiguation_index})"
            print(f"    Disambiguated to '{candidate_id}'")
            assert disambiguation_index > 0
        else:
            distinct_ids.add(candidate_id)
            assert disambiguation_index == 0
                
        node["node_id"] = candidate_id
        node["disambiguation_index"] = disambiguation_index

    # =============================================================================
    # Assign IRL

    new_node_dict = {}

    for node in paper["nodes"].values():
        prefix = "Entity"
        node_iri = f"{prefix}-{node['node_id']}"
        new_node_dict[node_iri] = {

            "node_id": node["node_id"],
            "disambiguation_index": node["disambiguation_index"],

            "label": node["label"],
            "normalised_label": node["normalised_label"],
            "aliases": node["aliases"],
            "types": node["types"],
            "node_type": node["node_type"],
            'LLM_familiarity': node['LLM_familiarity'],
            "description": node["description"],
            "mentions": node["mentions"],
        }

    paper["nodes"] = new_node_dict

    # =============================================================================
    # Assign IRL to each mention

    for node_iri, node in paper["nodes"].items():
        for i, mention in enumerate(node["mentions"], 1):
            mention["iri"] = node_iri + f"-Mention-{i}"

    # =============================================================================
    # Put entities back to sentence level

    for section in paper["sections"]:
        for paragraph in section["paragraphs"]:
            for sentence in paragraph["sentences"]:
                sentence["mentions"] = []


    for node_iri, node in paper["nodes"].items():
        for mention in node["mentions"]:
            sentence_iri = mention["reference"]
            sentence = get_sentence_from_iri(sentence_iri, paper)
            sentence_mention = {}
            sentence_mention["mention_iri"] = mention["iri"]
            sentence_mention["node_iri"] = node_iri
            sentence_mention["local_name"] = mention["local_name"]
            sentence_mention["global_name"] = node["label"]
            sentence_mention["disambiguation_index"] = node["disambiguation_index"]
            
            sentence["mentions"].append(sentence_mention)





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