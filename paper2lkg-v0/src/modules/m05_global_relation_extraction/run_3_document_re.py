# Named entity extraction

# Packages
from pathlib import Path
import sys
import os
import json
import time
import math
from datetime import datetime

# Add packages to sys.path
UTILITIES_RELATIVE_PATH = '../../'
UTILITIES_ABSOLUTE_PATH = str((Path(__file__).parent / UTILITIES_RELATIVE_PATH).resolve())
if UTILITIES_ABSOLUTE_PATH not in sys.path:
    sys.path.append(UTILITIES_ABSOLUTE_PATH)

# Custom packages
from utilities.llm_response_handler_JSON_list import call_llm_and_return_a_list, initialise_llm, PROMPT_LIMIT
from utilities.paper_access import get_text_from_section, get_text_from_paragraph, get_text
from utilities.content_processor import tokenise_text


MODULE ='m05'
STAGE = 3

CURRENT_DIR = Path(__file__).parent.resolve()
OLD_KG_PATH = CURRENT_DIR / f"kg_{STAGE - 1}.json"
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
        prompt_example = json.load(file)

    format_example = prompt_example["format_example"]

    file = open(LOG_PATH, "w")
    terminal = open(TERMINAL_PATH, "w")


    def prints(*args):
        print(*args, file=terminal)
        print(*args)

    # =============================================================================

    # Top 0.1 most relevant nodes

    node_count = len(paper["nodes"])
    prints(f"Total nodes: {node_count}")
    top_node_index = min(int(node_count * 0.1), 20)
    prints(f"Top 10% of nodes: {top_node_index}")
    prints(f"Number of comparisons: {math.comb(top_node_index, 2)}")


    top_nodes = dict(list(paper["nodes"].items())[:top_node_index])

    # for id, node in top_nodes.items():
    #     prints(f"Node {id}: {node['label']}")

    edges = []

    for top_node_id_1, top_node_1 in top_nodes.items():
        for top_node_id_2, top_node_2 in top_nodes.items():
            if top_node_id_1 < top_node_id_2:
                term_1 = top_node_1["label"]
                term_2 = top_node_2["label"]
                types_1 = top_node_1["types"]
                types_2 = top_node_2["types"]
                description_1 = top_node_1["description"]
                description_2 = top_node_2["description"]

                title = paper["title"]
                keywords = paper["keywords"]
                authors = paper["authors"]
                content = paper["summary"]

                prompt = prompt_template.format(
                    format_example=json.dumps(format_example, indent=2),

                    term_1=term_1,
                    term_2=term_2,
                    types_1=types_1,
                    types_2=types_2,
                    description_1=description_1,
                    description_2=description_2,

                    title=title,
                    keywords=keywords,
                    authors=authors,
                    content=content
                )

                response, log = call_llm_and_return_a_list(llm, prompt, greedy=True)

                # if response and isinstance(response, list):

                #     for pred in response:
                #         if pred != "":
                #             edges.append(
                #                 (
                #                     top_node_id_1,
                #                     pred,
                #                     top_node_id_2,
                #                 )
                #             )

                if response:

                    for pred in response:
                        if pred != "":

                            edges.append(
                                (
                                    top_node_id_1,
                                    str(pred),
                                    top_node_id_2,
                                )
                            )
                else:
                    prints("Warning: JSON parsing error")


                file.write(log)
                file.write("\n\n\n\n")
                file.flush()


    paper["document_level_edges"] = edges


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