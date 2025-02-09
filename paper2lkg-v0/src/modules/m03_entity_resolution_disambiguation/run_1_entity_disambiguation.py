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


MODULE ='m03'
STAGE = 1

CURRENT_DIR = Path(__file__).parent.resolve()
OLD_KG_PATH = CURRENT_DIR / f"../m02_mention_extraction_typing/kg_5.json"
NEW_KG_PATH = CURRENT_DIR / f"kg_{STAGE}.json"



# Ensure logs folder exists
LOGS_DIR = CURRENT_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Define log path
LOG_PATH = LOGS_DIR / f"{MODULE}_log_{STAGE}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt"


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
    # Merge named entities and general terms if they have the same normalised label

    named_entity_nodes = []
    general_term_nodes = []
    other_nodes = []

    for entity in paper["nodes"]:
        if entity["node_type"] == "named entity":
            named_entity_nodes.append(entity)
        elif entity["node_type"] == "general term":
            general_term_nodes.append(entity)
        elif entity["node_type"] == "other":
            other_nodes.append(entity)
        else:
            raise ValueError(f"Unknown node type: {entity['node_type']}")
    

    print("Number of nodes before merging:", len(paper["nodes"]))


    entity_nodes_dict = {}

    def merge_nodes(existing_node, new_node):
        merged_node = {}
        merged_node["label"] = existing_node["label"]
        merged_node["aliases"] = list(set(existing_node["aliases"] + new_node["aliases"]))
        merged_node["types"] = list(set(existing_node["types"] + new_node["types"]))

        merged_node["node_type"] = existing_node["node_type"]
        if existing_node["node_type"] != new_node["node_type"]:
            print(f"Warning: a named entity node is merging with a general term node: {existing_node['label']}")
            merged_node["node_type"] = "named entity"
        
        merged_node["normalised_label"] = existing_node["normalised_label"]
        merged_node["mentions"] = existing_node["mentions"] + new_node["mentions"]
        return merged_node


    for entity_node in named_entity_nodes + general_term_nodes:

        if entity_node["normalised_label"] not in entity_nodes_dict:
            entity_nodes_dict[entity_node["normalised_label"]] = entity_node
        else:
            existing_node = entity_nodes_dict[entity_node["normalised_label"]]
            merged_node = merge_nodes(existing_node, entity_node)
            entity_nodes_dict[entity_node["normalised_label"]] = merged_node

    paper["nodes"] = list(entity_nodes_dict.values()) + other_nodes

    # Check integrity
    for node in paper["nodes"]:
        assert node.keys() == {"label", "aliases", "types", "node_type", "normalised_label", "mentions"}

    print("Number of nodes after merging:", len(paper["nodes"]))


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