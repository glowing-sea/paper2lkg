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
from utilities.content_processor import check_existence_in_sentence, tokenise_text, lemmatise_text


MODULE ='m06'
STAGE = 2

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

    for node in list(paper["nodes"].values()) + list(paper["type_nodes"].values()):

        description = node["description"]
        label = node["label"]

        # Encode the label
        label_embedding = model.encode(label)
        description_embedding = model.encode(description)


        # Encode the label, types and description
        prompt = prompt_template_content.format(label=label, description=description)
        node_embedding = model.encode(prompt)

        log = prompt_template_instruction + "\n" + prompt + "\n\n"


        node["description_embedding"] = description_embedding
        node["label_embedding"] = label_embedding
        node["node_embedding"] = node_embedding
        

        with open(LOG_PATH, "a") as file:
            file.write(log)
            file.write("\n\n\n\n")
            file.flush()

    # =============================================================================
    # Try to match as many type nodes as possible to the nodes
    for type_node in paper["type_nodes"].values():
        for iri, node in paper["nodes"].items():

            type_node_embedding = type_node["node_embedding"]
            node_embedding = node["node_embedding"]

            type_node_label_embedding = type_node["label_embedding"]
            node_label_embedding = node["label_embedding"]

            type_node_description_embedding = type_node["description_embedding"]
            node_description_embedding = node["description_embedding"]
            
            if (np.dot(type_node_embedding, node_embedding) > 0.9     
                or

                np.dot(type_node_label_embedding, node_label_embedding) > 0.9 and
                np.dot(type_node_description_embedding, node_description_embedding) > 0.8):

                verbose = f"Potential Coreference found between '{type_node['label']}' and '{node['label']}'"
                
                print(verbose)

                type_node["matching_iris"].append(iri)

    # =============================================================================
    # Linking parent and child nodes

    print()

    type_edges = []

    for node_iris, node in paper["nodes"].items():
        parent_iris = set()
        for parent in node["types"]:
            parent = " ".join(lemmatise_text(tokenise_text(parent)))
            parent_node = paper["type_nodes"][parent]
            for matching_iri in parent_node["matching_iris"]:
                parent_iris.add(matching_iri)


        for parent_iri in parent_iris:
            if parent_iri != node_iris:
                type_edges.append((
                    node_iris,
                    parent_iri
                ))
                print(f"Node {node_iris} has a broader term {parent_iri}")

    # =============================================================================
    # Cycle detection

    print(f"Number of type edges: {len(type_edges)}")
    type_edges = list(set(type_edges))
    print(f"Number of type edges after removing duplicates: {len(type_edges)}")

    type_nodes = set()

    for edge in type_edges:
        type_nodes.add(edge[0])
        type_nodes.add(edge[1])

    print(f"Number of type nodes: {len(type_nodes)}")


    # =============================================================================

    # DFS

    def find_neighbour(node, type_edges):
        """
        Given an entity, return the entities that are broader than the given entity
        """
        neighbours = []
        for edge in type_edges:
            if edge[0] == node:
                neighbours.append(edge[1])
        
        assert len(neighbours) == len(set(neighbours)), f"Duplicate neighbours found!"

        return neighbours


    # Source: https://www.geeksforgeeks.org/introduction-to-disjoint-set-data-structure-or-union-find-algorithm/
    def dfs(entity, type_rdf_graph, visited, recursion_stack, cycles):
        """
        Perform a depth-first search to find the broader relations of an entity
        """
        visited.add(entity)
        recursion_stack.add(entity)

        # Visit all neighbours of the entity
        for neighbour in find_neighbour(entity, type_rdf_graph):
            if neighbour not in visited:
                dfs(neighbour, type_rdf_graph, visited, recursion_stack, cycles)
            elif neighbour in recursion_stack:
                # Found a cycle
                cycles.append((entity, neighbour))
            
        recursion_stack.remove(entity)

    def detect_cycle(type_nodes, type_edges):
        """
        Detect and remove cycle in the type graph
        """
        visited = set()
        recursion_stack = set()
        cycles = []

        for node in type_nodes:
            if node not in visited:
                dfs(node, type_edges, visited, recursion_stack, cycles)
                assert len(recursion_stack) == 0, f"Recursion stack not empty!"
        
        return cycles


    def detect_and_remove_cycle(type_nodes, type_edges):
        """
        Detect and remove cycle in the type graph
        """
        cycles = detect_cycle(type_nodes, type_edges)

        for cycle in cycles:
            print(f"Cycle: {cycle}")
            type_edges.remove(cycle)

        new_nodes = set()
        for edge in type_edges:
            new_nodes.add(edge[0])
            new_nodes.add(edge[1])

        return new_nodes, type_edges
    
    type_nodes, type_edges = detect_and_remove_cycle(type_nodes, type_edges)

    print(f"Number of type edges after removing cycles: {len(type_edges)}")

    new_edges = []
    for edge in type_edges:
        new_edges.append((
            edge[0],
            "has a broader term",
            edge[1]
        ))

    paper["type_edges"] = new_edges
        

    # =============================================================================
    # Clean up embedding

    for node in list(paper["nodes"].values()) + list(paper["type_nodes"].values()):
        del node["label_embedding"]
        del node["description_embedding"]
        del node["node_embedding"]

        if "matching iris" in node:
            node["matching_iris"] = list(dict.fromkeys(node["matching_iris"]))

    del paper["type_nodes"]




    # paper["type_edges"] = type_edges

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