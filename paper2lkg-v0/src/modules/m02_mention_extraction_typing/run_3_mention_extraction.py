# mention extraction

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


MODULE ='m02'
STAGE = 3

CURRENT_DIR = Path(__file__).parent.resolve()
OLD_KG_PATH = CURRENT_DIR / f"kg_{STAGE - 1}.json"
NEW_KG_PATH = CURRENT_DIR / f"kg_{STAGE}.json"
PROMPT_PATH = CURRENT_DIR / f"prompt_{STAGE}_template.md"
PROMPT_EXAMPLE_PATH = CURRENT_DIR / f"prompt_{STAGE}_examples.json"
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


    # Open the prompt template
    with open(PROMPT_PATH, "r") as file:
        prompt_template = file.read()

    # Open the prompt example
    with open(PROMPT_EXAMPLE_PATH, "r") as file:
        prompt_examples = json.load(file)


    format_example = prompt_examples["format_examples"]
    input_output_pairs = prompt_examples["input_output_pairs"]
    trivial_sentence = prompt_examples["trivial_sentence"]
    trivial_responses = prompt_examples["trivial_responses"]


    # =============================================================================
    # Extract mentions


    def ner(chunk, text):
        # Get named entities

        prompt = prompt_template.format(
            format_example=json.dumps(format_example, indent=2),
            input_example_1=input_output_pairs[0]["input"],
            output_example_1=json.dumps(input_output_pairs[0]["output"], indent=2),
            input_example_2=input_output_pairs[1]["input"],
            output_example_2=json.dumps(input_output_pairs[1]["output"], indent=2),
            input_example_3=input_output_pairs[2]["input"],
            output_example_3=json.dumps(input_output_pairs[2]["output"], indent=2),
            text=text
        )

        mentions, log = call_llm_and_return_a_list(llm, prompt)

        if not mentions:
            mentions = []
        new_mentions = []

        # Result Checking
        def result_checking(mention, label_fields, type_field):
            
            # 1. Has "mention" and "type" keys
            if not label_fields in mention or not type_field in mention:
                return False
            
            # 2. "mention" is an non-empty string
            label = str(mention[label_fields]).strip()
            if not label:
                return False
            
            # 3. "type" is a list of string containing at least one element
            types = mention[type_field]
            if not isinstance(types, list) or not types or not all(isinstance(i, str) and i for i in types):
                return False
            
            return {
                "label": label,
                "types": types
            }
        

        # Remove trivial responses
        for mention in mentions:
            result = result_checking(mention, "mention", "types")
            if not result:
                print(f"Syntactic Error:")
                print(json.dumps(mention, indent=2))
                log += f"Syntactic Error:\n{json.dumps(mention, indent=2)}\n"
                continue

            new_mentions.append(result)

        chunk["mentions"] = new_mentions
        

        with open(LOG_PATH, "a") as file:
            file.write(log)
            file.write("\n\n\n\n")
            file.flush()
    

    # Extract sentence-level named entities
    for section in paper["sections"]:
        for paragraph in section["paragraphs"]:
            for sentence in paragraph["sentences"]:
                text = get_text(sentence) + trivial_sentence
                ner(sentence, text)
            
            text = get_text(paragraph)
            ner(paragraph, text)

        text = get_text(section)
        ner(section, text)
    

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