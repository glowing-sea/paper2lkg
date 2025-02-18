# Named entity extraction

# Packages
from pathlib import Path
import sys
import os
import json
import time
from datetime import datetime

# Add packages to sys.path
UTILITIES_RELATIVE_PATH = '../'
UTILITIES_ABSOLUTE_PATH = str((Path(__file__).parent / UTILITIES_RELATIVE_PATH).resolve())
if UTILITIES_ABSOLUTE_PATH not in sys.path:
    sys.path.append(UTILITIES_ABSOLUTE_PATH)

# Custom packages
from utilities.paper_access import get_text_from_section, get_text_from_paragraph, get_text



def run(DATASET, INDEX, LLM_MODEL):


    CURRENT_DIR = Path(__file__).parent.resolve()
    OLD_KG_PATH = CURRENT_DIR / f"../../data/input/kg_{DATASET}_{INDEX}_{LLM_MODEL}.json"
    PROMPT_PATH = CURRENT_DIR / f"prompt_1_template.md"
 
    # =============================================================================
    # Prepare the named entity extraction module

    """
    Run the named entity extraction module
    """

    # Open the paper
    with open(OLD_KG_PATH, "r") as f:
        paper = json.load(f)


    # Open the prompt template
    with open(PROMPT_PATH, "r") as file:
        prompt_template = file.read()

    # =============================================================================

    paper_text = []

    for section in paper['sections']:
        paper_text.append(section["subtitle"] + "\n" + get_text(section))

    prompt = prompt_template.format(content = '\n\n'.join(paper_text))

    print(prompt)


if __name__ == "__main__":
    DATASET = "ASKG"
    LLM_MODEL = "l"
    INDEX = 10

    run(DATASET, INDEX, LLM_MODEL)