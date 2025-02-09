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
from utilities.llm_response_handler_JSON import call_llm_and_return_JSON, initialise_llm, PROMPT_LIMIT
from utilities.paper_access import get_text_from_section, get_text_from_paragraph, get_text
from utilities.content_processor import tokenise_text


MODULE ='m05'
STAGE = 1

CURRENT_DIR = Path(__file__).parent.resolve()
OLD_KG_PATH = CURRENT_DIR / f"../m04_local_relation_extraction/kg_3.json"
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
        prompt_example = json.load(file)

    format_example = prompt_example["format_example"]

    file = open(LOG_PATH, "w")
    terminal = open(TERMINAL_PATH, "w")


    def prints(*args):
        print(*args, file=terminal)
        print(*args)

    # =============================================================================
    # Summarise the paper


    # https://chatgpt.com/c/6710989b-58c4-8010-86a0-532a030eade7
    def generate_section_order(num_sections):
        mid = num_sections // 2
        result = []
        
        for i in range(mid):
            result.append(mid + i + 1)
            result.append(mid - i)
        if num_sections % 2 != 0:
            result.append(mid + 1)
        
        return result
    
    # https://chatgpt.com/c/6710989b-58c4-8010-86a0-532a030eade7
    def section_order_generator(num_sections):
        order = generate_section_order(num_sections)
        while True:
            for section in order:
                yield section - 1


    def total_tokens(section_texts):
        return sum([len(tokenise_text(section_text)) for section_text in section_texts])
        
    


    gen = section_order_generator(len(paper["sections"]))
    target_tokens = PROMPT_LIMIT // 2
    prints(f"Target tokens: {target_tokens}")
    section_texts = []
    for section in paper["sections"]:
        section_texts.append(get_text(section))


    while total_tokens(section_texts) > target_tokens:

        section_index = next(gen)

        prints(f"Current tokens: {total_tokens(section_texts)}")
        prints(f"Summarising section {section_index + 1}")


        text = section_texts[section_index]

        # Get the summary
        prompt = prompt_template.format(
            input_text=text, 
            format_example=json.dumps(format_example, indent=2)
            )
        
        response, log, original_response = call_llm_and_return_JSON(llm, prompt)

        if response is not None and "summary" in response:
            summary = str(response["summary"])
            section_texts[section_index] = summary
        else:
            prints("Failed to get a summary. Maintaining the original text.")

        origianl_tokens_count = len(tokenise_text(text))
        new_tokens_count = len(tokenise_text(section_texts[section_index]))

        prints(f"Original tokens in section {section_index + 1}: {origianl_tokens_count}")
        prints(f"New tokens in section {section_index + 1}: {new_tokens_count}")
        prints(f"Tokens saved: {origianl_tokens_count - new_tokens_count}")

        file.write(log)
        file.write("\n\n\n\n")
        file.flush()

    prints("Summarisation Finished. Total tokens:", total_tokens(section_texts))
    paper["summary"] = "\n\n".join(section_texts)



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