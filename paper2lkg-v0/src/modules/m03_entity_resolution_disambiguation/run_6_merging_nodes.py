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
from utilities.content_processor import check_existence_in_sentence, tokenise_text, lemmatise_text


MODULE ='m03'
STAGE = 6

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


    print("Total nodes before merging:", len(paper["nodes"]))
    print("Total matching node pairs:", len(paper["matching_node_pairs"]))

    mentions = []
    for node in paper["nodes"].values():
        mentions += node["mentions"]
    print("Total mentions before merging:", len(mentions))


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
            
            # Remove nodes of the largest clique from the graph
            G.remove_nodes_from(max_cliques[0])

        return disjoint_max_cliques
    

    # Create a graph from the matching node pairs
    G = nx.Graph()
    G.add_edges_from(paper["matching_node_pairs"])



    # Find all disjoint max cliques
    disjoint_cliques = find_max_disjoint_cliques(G)
    disjoint_cliques_greater_than_1 = [sorted(clique) for clique in disjoint_cliques if len(clique) > 1]
    print("Disjoint Maximal Cliques greater than 1:", disjoint_cliques_greater_than_1)


    # Node Count Checking
    node_count = 0
    for clique in disjoint_cliques_greater_than_1:
        node_count += len(clique)
    print("Total nodes in disjoint cliques:", node_count)


    # Expected number of nodes reduce
    expected_number_of_nodes_reduce = sum([len(clique) - 1 for clique in disjoint_cliques_greater_than_1])
    print("Expected number of nodes reduce:", expected_number_of_nodes_reduce)


    # =============================================================================

    def merge_nodes(node1, node2):
        node1["label"] = node1["label"] # same

        node1["aliases"] = list(set(node1["aliases"] + node2["aliases"]))
        node1["types"] = list(set(node1["types"] + node2["types"]))

        if "named entity" in node1["node_type"] or "named entity" in node2["node_type"]:
            node1["node_type"] = "named entity"
        elif "general term" in node1["node_type"] or "general term" in node2["node_type"]:
            node1["node_type"] = "general term"
        elif "other" in node1["node_type"] or "other" in node2["node_type"]:
            node1["node_type"] = "other"
        else:
            raise ValueError("Node types are not matching")
        
        node1["normalised_label"] = node1["normalised_label"] # same
        
        node1["mentions"] = node1["mentions"] + node2["mentions"]

        node1["LLM_familiarity"] = node1["LLM_familiarity"] or node2["LLM_familiarity"]

        node1["description"] = node1["description"] # same


    # Merging nodes based on the disjoint cliques

    for clique in disjoint_cliques_greater_than_1:
        parent_id = str(clique[0])
        for node_id in clique[1:]:
            node_id = str(node_id)
            parent = paper["nodes"][parent_id]
            node = paper["nodes"][node_id]
            merge_nodes(parent, node)
            del paper["nodes"][node_id]


    # Number of mentions after merging
    mentions = []
    for node in paper["nodes"].values():
        mentions += node["mentions"]
    print("Total mentions after merging:", len(mentions))

    # Total nodes after merging
    print("Total nodes after merging:", len(paper["nodes"]))

    # Clean up
    for node in paper["nodes"].values():
        del node["node_embedding"]
        del node["label_embedding"]
        del node["description_embedding"]

    del paper["matching_node_pairs"]





    # =============================================================================

    # cliques = list(nx.find_cliques(G))

    # max_cliques = []
    # max_cliques_size = 0

    # for clique in cliques:
    #     if len(clique) > max_cliques_size:
    #         max_cliques = [clique]
    #         max_cliques_size = len(clique)
    #     elif len(clique) == max_cliques_size:
    #         max_cliques.append(clique)
    #     else:
    #         pass

    # print("Maximal Cliques:", max_cliques)

    # print("All Maximal Cliques:", cliques)

    # print(G.edges)





    # # =============================================================================
    # # Execute Union Find Algorithm

    # # Initialise the parent of each node to itself
    # for node_id, node in paper["nodes"].items():
    #     node["parent"] = node_id


    # # https://www.geeksforgeeks.org/introduction-to-disjoint-set-data-structure-or-union-find-algorithm/
    # def find(nodes, node_id): 
    #     # If i is the parent of itself 
    #     if nodes[node_id]["parent"] == node_id:
    #         return node_id
    #     else:
    #         # Recursively find the parent of the entity
    #         nodes[node_id]["parent"] = find(nodes, nodes[node_id]["parent"])
    #         return nodes[node_id]["parent"]
    
        
    # def union(nodes, node_1_id, node_2_id):
    #     root_id_1 = find(nodes, node_1_id)
    #     root_id_2 = find(nodes, node_2_id)

    #     # Making id of the parent as small as possible
    #     if int(root_id_1) < int(root_id_2):
    #         nodes[root_id_2]["parent"] = root_id_1
    #     elif int(root_id_1) > int(root_id_2):
    #         nodes[root_id_1]["parent"] = root_id_2
    #     else:
    #         pass
    


    # for pair in paper["matching_node_pairs"]:
    #     union(paper["nodes"], str(pair[0]), str(pair[1]))

    # # Path compression
    # for node_id, node in paper["nodes"].items():
    #     node["parent"] = find(paper["nodes"], node_id)


    # # =============================================================================
    # # Verbose

    # parent_ids = []

    # for node_id, node in paper["nodes"].items():
    #     parent_id = node["parent"]
    #     parent_ids.append(parent_id)

    # # print(parent_ids)
    # parent_ids = list(dict.fromkeys(parent_ids))

    # print("Total parents:", len(parent_ids))

    # for parent_id in parent_ids:
    #     assert parent_id == paper["nodes"][parent_id]["parent"]


    # # =============================================================================
    # # Merging nodes based on the parent

    # node_to_delete = []


    # for node_id, node in paper["nodes"].items():
    #     parent_id = node["parent"]
    #     if parent_id != node_id:
    #         parent = paper["nodes"][parent_id]
    #         parent["mentions"] += node["mentions"]
    #         # paper["nodes"][parent_id] = node
    #         node_to_delete.append(node_id)

    # for node_id in node_to_delete:
    #     del paper["nodes"][node_id]


    # # =============================================================================
    # # Verbose

    # print("Total nodes after merging:", len(paper["nodes"]))

    # mentions = []
    # for node in paper["nodes"].values():
    #     mentions += node["mentions"]
    # print("Total mentions after merging:", len(mentions))


    # # =============================================================================
    # # Clean up
    # del paper["matching_node_pairs"]
    # for node_id, node in paper["nodes"].items():
    #     assert node_id == node["parent"]
    #     del node["parent"]






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