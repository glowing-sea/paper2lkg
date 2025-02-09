# Named entity extraction

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
from utilities.paper_access import get_text_from_section, get_text_from_paragraph, get_text


MODULE ='m04'
STAGE = 1

CURRENT_DIR = Path(__file__).parent.resolve()
OLD_KG_PATH = CURRENT_DIR / "../m03_entity_resolution_disambiguation/kg_7.json"
NEW_KG_PATH = CURRENT_DIR / f"kg_{STAGE}.json"
PROMPT_PATH = CURRENT_DIR / f"prompt_{STAGE}_template.md"
PROMPT_EXAMPLE_PATH = CURRENT_DIR / f"prompt_{STAGE}_examples.json"

TIME = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')


# Ensure logs folder exists
LOGS_DIR = CURRENT_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Define log path
LOG_PATH = LOGS_DIR / f"{MODULE}_log_{STAGE}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt"


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
        prompt_examples = json.load(file)

    file = open(LOG_PATH, "w")
    terminal = open(TERMINAL_PATH, "w")


    format_example = prompt_examples["format_examples"]
    input_output_pairs = prompt_examples["input_output_pairs"]

    def prints(*args):
        print(*args, file=terminal)
        print(*args)

    # =============================================================================
    # Extract named entities


    def lre(chunk, text, mentions):

        local_name_to_iri = {}


        for mention in mentions:
            local_name = mention["local_name"]
            iri = mention["node_iri"]

            if local_name in local_name_to_iri:
                if iri not in local_name_to_iri[local_name]:
                    local_name_to_iri[local_name].append(iri)
            else:
                local_name_to_iri[local_name] = [iri]

        for local_name, iris in local_name_to_iri.items():
            if len(iris) > 1:
                prints("Warning: Multiple IRLs for the same local name")
                prints(f"Local Name: {local_name}")
                prints(f"IRLs: {iris}")


        input_actual = {
            "text": text,
            "terms": str(list(local_name_to_iri.keys()))
        }

        prompt = prompt_template.format(
            format_example=json.dumps(format_example, indent=2),

            input_example_1=json.dumps(input_output_pairs[0]["input"], indent=2),
            output_example_1=json.dumps(input_output_pairs[0]["output"], indent=2),
            input_example_2=json.dumps(input_output_pairs[1]["input"], indent=2),
            output_example_2=json.dumps(input_output_pairs[1]["output"], indent=2),
            input_example_3=json.dumps(input_output_pairs[2]["input"], indent=2),
            output_example_3=json.dumps(input_output_pairs[2]["output"], indent=2),


            input_actual = json.dumps(input_actual, indent=2)
        )


        triples, log = call_llm_and_return_a_list(llm, prompt)
        if not triples:
            triples = []
        new_triples = []

        for triple in triples:
            if ("subject" in triple and "predicate" in triple
                and triple["subject"] and triple["predicate"]):

                # Not object field, empty string, or None
                if "object" not in triple or not triple["object"]:
                    prints("Warning: Missing object")
                    obj = ""
                else:
                    obj = str(triple["object"])

                new_triple = {
                    "subject": str(triple["subject"]),
                    "predicate": str(triple["predicate"]),
                    "object": obj
                }
                new_triples.append(new_triple)
            else:
                prints(f"Syntactic Error: {json.dumps(triple, indent=2)}")

        chunk["triples"] = new_triples
        chunk["local_name_to_iri"] = local_name_to_iri


        # Result Checking
        # def result_checking(mention, label_fields, type_field):
            
        #     # 1. Has "entity" and "type" keys
        #     if not label_fields in mention or not type_field in mention:
        #         return False
            
        #     # 2. "entity" is an non-empty string
        #     label = str(mention[label_fields]).strip()
        #     if not label:
        #         return False
            
        #     # 3. "type" is a list of string containing at least one element
        #     types = mention[type_field]
        #     if not isinstance(types, list) or not types or not all(isinstance(i, str) and i for i in types):
        #         return False
            
        #     return {
        #         "label": label,
        #         "types": types
        #     }


        # # Remove trivial responses
        # for entity in named_entities:
        #     result = result_checking(entity, "entity", "types")
        #     if not result:
        #         prints(f"Syntactic Error:")
        #         prints(json.dumps(entity, indent=2))
        #         log += f"Syntactic Error:\n{json.dumps(entity, indent=2)}\n"
        #         continue

        #     if result["label"] in trivial_responses:
        #         continue

        #     new_named_entities.append(result)

        # chunk["triples"] = new_named_entities

        file.write(log)
        file.write("\n\n\n\n")
        file.flush()
    

    # Extract sentence-level named entities
    for section in paper["sections"]:
        for paragraph in section["paragraphs"]:
            for sentence in paragraph["sentences"]:
                text = get_text(sentence)
                lre(sentence, text, sentence["mentions"])
            
            text = get_text(paragraph)
            mentions = [mention for sentence in paragraph["sentences"] for mention in sentence["mentions"]]
            lre(paragraph, text, mentions)

        text = get_text(section)
        mentions = [mention for paragraph in section["paragraphs"] for sentence in paragraph["sentences"] for mention in sentence["mentions"]]
        lre(section, text, mentions)
    

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