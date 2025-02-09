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
from utilities.llm_response_handler_JSON import call_llm_and_return_JSON, initialise_llm
from utilities.paper_access import get_text, get_sentence_from_iri, get_section_from_sentence
from utilities.content_processor import check_existence_in_sentence, tokenise_text, lemmatise_text


MODULE ='m03'
STAGE = 3

CURRENT_DIR = Path(__file__).parent.resolve()
OLD_KG_PATH = CURRENT_DIR / f"kg_{STAGE-1}.json"
NEW_KG_PATH = CURRENT_DIR / f"kg_{STAGE}.json"
PROMPT_PATH_SPECIFIC = CURRENT_DIR / f"prompt_{STAGE}_specific.md"
PROMPT_PATH_GENERAL = CURRENT_DIR / f"prompt_{STAGE}_general.md"
PROMPT_PATH_DETAILED = CURRENT_DIR / f"prompt_{STAGE}_detailed.md"
LOG_PATH = CURRENT_DIR / f"./logs/{MODULE}_log_{STAGE}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt"



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

    with open(PROMPT_PATH_SPECIFIC, "r") as file:
        prompt_template_specific = file.read()

    with open(PROMPT_PATH_GENERAL, "r") as file:
        prompt_template_general = file.read()

    with open(PROMPT_PATH_DETAILED, "r") as file:
        prompt_template_detailed = file.read()

    # =============================================================================
    # Test familiarity
    for node in paper["nodes"]:
        if node["LLM_familiarity"] == False or node["node_type"] == "other":
            label = node["label"]
            types = str(node["types"])
            title = paper["title"]
            authors = str(paper["authors"])
            keywords = str(paper["keywords"])
            paper_level_context = get_text(paper["sections"][0])

            sentence_iri = node["mentions"][0]["reference"]
            sentence = get_sentence_from_iri(sentence_iri, paper)
            section = get_section_from_sentence(sentence, paper)

            sentence_level_context = get_text(sentence)
            section_level_context = get_text(section)

            if node["node_type"] == "other":
                prompt_template = prompt_template_detailed
            else:
                prompt_template = prompt_template_specific

            prompt = prompt_template.format(
                label=label,
                types=types,
                title=title,
                authors=authors,
                keywords=keywords,
                paper_level_context=paper_level_context,
                sentence_level_context=sentence_level_context,
                section_level_context=section_level_context
            )

        elif node["LLM_familiarity"] == True and node["node_type"] != "other":
            label = node["label"]
            types = str(node["types"])

            sentence_iri = node["mentions"][0]["reference"]
            sentence = get_sentence_from_iri(sentence_iri, paper)
            sentence_level_context = get_text(sentence)

            prompt = prompt_template_general.format(
                label=label,
                types=types,
                sentence_level_context=sentence_level_context,
            )
        else:
            raise ValueError(f"Node {node['label']} has no familiarity information")
        
        description, log, _ = call_llm_and_return_JSON(llm, prompt)

        if description == None or "description" not in description:
            description = ""
            print(f"Warning: description of '{node['label']}' not found. Assume empty.")
        else:
            description = str(description["description"])

        node["description"] = description


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