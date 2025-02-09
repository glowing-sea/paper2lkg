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
    
    predicates = {}

    # =============================================================================

    for i, edge in enumerate(paper["edges"] + paper["document_level_edges"] + paper["type_edges"][:10], 0):
        label = edge[1]
        description = edge[3]

        # Encode the label
        label_embedding = model.encode(label).tolist()

        # Encode the description
        description_embedding = model.encode(description).tolist()

        # Encode the label, types and description
        prompt = prompt_template_content.format(label=label, description=description)
        edge_embedding = model.encode(prompt).tolist()

        log = prompt_template_instruction + "\n" + prompt + "\n\n"


        edge.pop()
        predicates[i] = {
            "label": label,
            "description": description,
            "label_embedding": label_embedding,
            "description_embedding": description_embedding,
            "edge_embedding": edge_embedding
        }

        assert len(edge) == 3

        with open(LOG_PATH, "a") as file:
            file.write(log)
            file.write("\n\n\n\n")
            file.flush()

    assert len(predicates) == len(paper["edges"] + paper["document_level_edges"] + paper["type_edges"][:10])

    # =============================================================================

    related_predicates = []

    # # =============================================================================

    for predicate_id_1, predicate_1 in predicates.items():
        for predicate_id_2, predicate_2 in predicates.items():
            if predicate_id_1 < predicate_id_2:
                predicate_1_label_embedding = np.array(predicate_1["label_embedding"])
                predicate_1_description_embedding = np.array(predicate_1["description_embedding"])
                predicate_1_edge_embedding = np.array(predicate_1["edge_embedding"])

                predicate_2_label_embedding = np.array(predicate_2["label_embedding"])
                predicate_2_description_embedding = np.array(predicate_2["description_embedding"])
                predicate_2_edge_embedding = np.array(predicate_2["edge_embedding"])

                if (
                    sanitise_iri(predicate_1["label"]) == sanitise_iri(predicate_2["label"]) 
                    
                    or
                    
                    np.dot(predicate_1_label_embedding, predicate_2_label_embedding) > 0.99 and
                    np.dot(predicate_1_description_embedding, predicate_2_description_embedding) > 0.9 
                    
                    or

                    np.dot(predicate_1_edge_embedding, predicate_2_edge_embedding) > 0.95
                    
                    ):

                    print(f"Potential Coreference found between '{predicate_1['label']}' and '{predicate_2['label']}'")
                    related_predicates.append((predicate_id_1, predicate_id_2))

    for predicate in predicates.values():
        del predicate["label_embedding"]
        del predicate["description_embedding"]
        del predicate["edge_embedding"]

    
    paper["predicates"] = predicates
    paper["related_predicates"] = related_predicates

                # edge_1["matching_iris"].append(edge_2[0])

            # if (np.dot(type_node_embedding, node_embedding) > 0.9     
            #     or

            #     np.dot(type_node_label_embedding, node_label_embedding) > 0.9 and
            #     np.dot(type_node_description_embedding, node_description_embedding) > 0.8):

            #     verbose = f"Potential Coreference found between '{type_node['label']}' and '{node['label']}'"
                
            #     print(verbose)

                # type_node["matching_iris"].append(iri)


    # # =============================================================================
    # # Linking parent and child nodes

    # print()

    # type_edges = []

    # for node_iris, node in paper["nodes"].items():
    #     parent_iris = set()
    #     for parent in node["types"]:
    #         parent = " ".join(lemmatise_text(tokenise_text(parent)))
    #         parent_node = paper["type_nodes"][parent]
    #         for matching_iri in parent_node["matching_iris"]:
    #             parent_iris.add(matching_iri)


    #     for parent_iri in parent_iris:
    #         if parent_iri != node_iris:
    #             type_edges.append((
    #                 node_iris,
    #                 parent_iri
    #             ))
    #             print(f"Node {node_iris} has a broader term {parent_iri}")

    

    # paper["type_edges"] = new_edges
        

    # =============================================================================
    # Clean up embedding



    # for node in list(paper["nodes"].values()) + list(paper["type_nodes"].values()):
    #     del node["label_embedding"]
    #     del node["description_embedding"]
    #     del node["node_embedding"]

    #     if "matching iris" in node:
    #         node["matching_iris"] = list(dict.fromkeys(node["matching_iris"]))

    # del paper["type_nodes"]




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