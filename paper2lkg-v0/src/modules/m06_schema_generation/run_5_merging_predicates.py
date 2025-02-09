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
import numpy as np

# Add packages to sys.path
UTILITIES_RELATIVE_PATH = '../../'
UTILITIES_ABSOLUTE_PATH = str((Path(__file__).parent / UTILITIES_RELATIVE_PATH).resolve())
if UTILITIES_ABSOLUTE_PATH not in sys.path:
    sys.path.append(UTILITIES_ABSOLUTE_PATH)

# Custom packages
from utilities.paper_access import get_text, get_sentence_from_iri, get_section_from_sentence
from utilities.content_processor import check_existence_in_sentence, tokenise_text, lemmatise_text, sanitise_iri


MODULE ='m06'
STAGE = 5

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
    # Verbose


    print("Total predicates before merging:", len(paper["predicates"]))
    print("Total matching predicate pairs:", len(paper["related_predicates"]))


    # =============================================================================
    # Finding the maximal cliques
    import networkx as nx


    # https://chatgpt.com/c/670f5e8f-c708-8010-b4e1-b2155c621be2
    def find_max_disjoint_cliques(G):
        disjoint_max_cliques = []
        
        # Keep iterating until no more cliques are found
        while True:
            cliques = list(nx.find_cliques(G))

            # Find the largest clique(s)
            max_cliques = []
            max_clique_size = 0

            for clique in cliques:
                if len(clique) > max_clique_size:
                    max_cliques = [clique]
                    max_clique_size = len(clique)
                elif len(clique) == max_clique_size:
                    max_cliques.append(clique)
            
            # If no cliques found, break the loop
            if not max_cliques:
                break
            
            # Add the largest cliques found to the list of disjoint cliques
            disjoint_max_cliques.append(max_cliques[0])  # Take the first largest clique
            
            # Remove predicates of the largest clique from the graph
            G.remove_nodes_from(max_cliques[0])

        return disjoint_max_cliques
    

    # Create a graph from the matching node pairs
    G = nx.Graph()
    G.add_edges_from(paper["related_predicates"])



    # Find all disjoint max cliques
    disjoint_cliques = find_max_disjoint_cliques(G)
    disjoint_cliques_greater_than_1 = [sorted(clique) for clique in disjoint_cliques if len(clique) > 1]
    print("Disjoint Maximal Cliques greater than 1:", disjoint_cliques_greater_than_1)



    # Expected number of nodes reduce
    expected_number_of_predicate_reduce = sum([len(clique) - 1 for clique in disjoint_cliques_greater_than_1])
    print("Expected number of predicates reduce:", expected_number_of_predicate_reduce)



    for predicate_id, predicate in paper["predicates"].items():
        # Assign parent to itself
        predicate["parent"] = predicate_id

    

    for clique in disjoint_cliques_greater_than_1:
        parent = clique[0]
        for predicate_id in clique[1:]:
            paper["predicates"][str(predicate_id)]["parent"] = parent


    # =============================================================================

    actual_number_of_predicate_reduce = 0

    for predicate_id, predicate in paper["predicates"].items():
        parent_id = predicate["parent"]

        if parent_id != predicate_id:
            parent = paper["predicates"][str(parent_id)]["label"]
            me = predicate["label"]

            print(f"Predicate '{me}' is merged into '{parent}'")
            actual_number_of_predicate_reduce += 1

    print("Actual number of predicates reduce:", actual_number_of_predicate_reduce)


    # =============================================================================

    # Create a dictionary of parent predicates

    parent_predicates = {}

    for predicate_id, predicate in paper["predicates"].items():
        parent_id = predicate["parent"]
        if str(parent_id) not in parent_predicates:
            parent_label = paper["predicates"][str(parent_id)]["label"]
            parent_description = paper["predicates"][str(parent_id)]["description"]
            parent_predicates[parent_id] = {
                "label": parent_label,
                "description": parent_description
            }

    print("Actual number of predicates reduce:", len(paper["predicates"]) - len(parent_predicates))
    print("Total predicates after merging:", len(parent_predicates))

    paper["parent_predicates"] = parent_predicates


    last_key = list(paper["predicates"].keys())[-1]
    parent_value = paper["predicates"][last_key]["parent"]
    skosbroader = paper["predicates"][str(parent_value)]

    print("SKOS broader predicate ID:", str(parent_value))
    print("SKOS broader predicate:", skosbroader["label"])


    # =============================================================================

    # Assign Node IDs

    distinct_ids = set()
    disambiguated_ids = set()

    for node_id, node in paper["parent_predicates"].items():
        
        candidate_id = sanitise_iri(node["label"])

        if str(parent_value) == str(node_id):
            candidate_id = "skos:broader"

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


    for predicate_id, node in paper["parent_predicates"].items():

        if str(parent_value) == str(predicate_id):
            node["predicate_iri"] = "skos:broader"
        else:
            prefix = "Predicate"
            node_iri = f"{prefix}-{node['node_id']}"
            node["predicate_iri"] = node_iri

    # =============================================================================

    assert len (paper["edges"] + paper["document_level_edges"] + paper["type_edges"][:10]) == len(paper["predicates"])

    for i, edge in enumerate(paper["edges"] + paper["document_level_edges"] + paper["type_edges"][:10], 0):
        parent_index = str(paper["predicates"][str(i)]["parent"])
        print(f"Original: {edge[1]} Now: {parent_predicates[parent_index]['predicate_iri']}")
        edge[1] = parent_predicates[parent_index]["predicate_iri"]

    for edge in paper["type_edges"]:
        edge[1] = parent_predicates[str(parent_value)]["predicate_iri"]

    # =============================================================================

    # Rebuild Predicate Index

    new_predicates = {}

    for new_predicate in paper["parent_predicates"].values():
        iri = new_predicate["predicate_iri"]
        label = new_predicate["label"]
        description = new_predicate["description"]
        disambiguation_index = new_predicate["disambiguation_index"]

        new_pred_dict = {
            "label": label,
            "description": description,
            "disambiguation_index": disambiguation_index
        }

        if iri in new_predicates:
            raise ValueError(f"Predicate IRI '{iri}' already exists")
        else:
            new_predicates[iri] = new_pred_dict

    # =============================================================================
    # Clean up

    new_edges = paper["edges"] + paper["document_level_edges"] + paper["type_edges"]
    # Convert to triple
    new_edges = [(edge[0], edge[1], edge[2]) for edge in new_edges]
    print("Before removing duplicates:", len(new_edges))
    new_edges = list(dict.fromkeys(new_edges))
    print("After removing duplicates:", len(new_edges))

    new_general_edges = []
    new_type_edges = []

    for edge in new_edges:
        if edge[1] == "skos:broader":
            new_type_edges.append(edge)
        else:
            new_general_edges.append(edge)

    assert len(new_general_edges) + len(new_type_edges) == len(new_edges)


    del paper["parent_predicates"]
    del paper["related_predicates"]
    del paper["predicates"]
    del paper["edges"]
    del paper["document_level_edges"]
    del paper["type_edges"]
    

    paper["triples"] = new_general_edges
    paper["triples_typing"] = new_type_edges
    paper["predicates"] = new_predicates


    for node in paper["nodes"].values():
        del node["normalised_label"]
        del node["aliases_normalised"]

    # =============================================================================
    # Tidy up and save the KG


    finish_time = time.time() - start_time
    print(f"Finished in {finish_time} seconds")
    if "times" not in paper:
        paper["times"] = []
    paper["times"].append(finish_time)

    print("Total time taken:", sum(paper["times"]) / 60, "minutes")

    # Save the KG
    with open(NEW_KG_PATH, "w") as f:
        json.dump(paper, f, indent=2)


if __name__ == "__main__":
    run()