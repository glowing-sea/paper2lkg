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


import voyageai
CURRENT_DIR = Path(__file__).parent.resolve()
API_KEY_PATH = CURRENT_DIR / "./api_key.json"
with open(API_KEY_PATH, "r") as f:
    my_api_key= json.load(f)["api_key"]


# Add packages to sys.path
UTILITIES_RELATIVE_PATH = '../'
UTILITIES_ABSOLUTE_PATH = str((Path(__file__).parent / UTILITIES_RELATIVE_PATH).resolve())
if UTILITIES_ABSOLUTE_PATH not in sys.path:
    sys.path.append(UTILITIES_ABSOLUTE_PATH)

# Custom packages
from utilities.paper_access import get_text, get_sentence_from_iri, get_section_from_sentence
from utilities.content_processor import check_existence_in_sentence, tokenise_text, lemmatise_text



CURRENT_DIR = Path(__file__).parent.resolve()

TOKEN_LIMIT = 32000

def run(DATASET, INDEX, LLM_MODEL):

    OLD_KG_PATH = CURRENT_DIR / f"../../data/output//kg_{DATASET}_{INDEX}_{LLM_MODEL}.json"


    # =============================================================================
    # Prepare the named entity extraction module

    """
    Run the named entity extraction module
    """

    # Open the paper
    with open(OLD_KG_PATH, "r") as f:
        paper = json.load(f)

    vo = voyageai.Client(api_key=my_api_key)

    
    paper_text = []
    for section in paper['sections']:
        paper_text.append(get_text(section))
    paper_text = '\n\n'.join(paper_text)
    paper_text_tokens_count = len(tokenise_text(paper_text))

    print(f"Paper text tokens count: {paper_text_tokens_count}")
    generated_text = '\n\n'.join(paper['kg2text'][:len(paper['kg2text'])])
    generated_text_tokens_count = len(tokenise_text(generated_text))
    print(f"Generated text tokens count: {generated_text_tokens_count}")


    for i in range(len(paper['kg2text'])):
        generated_text = '\n\n'.join(paper['kg2text'][:len(paper['kg2text'])-i])
        generated_text_tokens_count = len(tokenise_text(generated_text))
        if generated_text_tokens_count < TOKEN_LIMIT:
            if i == 0:
                print("No truncate occurs")
                break
            else:
                print("The text is truncate!!")
                break

    print(f"(New) Generated text tokens count: {generated_text_tokens_count}")


    paper_text_embedding = vo.embed(paper_text, model="voyage-3").embeddings[0]
    print(len(paper_text_embedding))
    generated_text_embedding = vo.embed(generated_text, model="voyage-3").embeddings[0]
    print(len(generated_text_embedding))

    similarity = np.dot(paper_text_embedding, generated_text_embedding) / (np.linalg.norm(paper_text_embedding) * np.linalg.norm(generated_text_embedding))
    # similarity = 1

    # =============================================================================

    # print(paper_text)

    # print("\n\n\n====================\n\n\n")

    # print(generated_text)


    print(f"Similarity: {similarity}")


    
    return float(similarity)

    # =============================================================================
    

if __name__ == "__main__":
    DATASET = "SciERC"
    LLM_MODEL = "l"
    PAPER_INDICES = range(1,101)


    RESULT = CURRENT_DIR / f"../../data/raw_results/re_{DATASET}_{LLM_MODEL}.json"
    similarities = []
    result = {}
    for INDEX in PAPER_INDICES:
        similarities.append(run(DATASET, INDEX, LLM_MODEL))

    result["similarities"] = similarities
    result["mean_similarity"] = float(np.mean(similarities))
    result["std_similarity"] = float(np.std(similarities))

    with open(RESULT, "w") as f:
        json.dump(result, f, indent=2)