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
from utilities.llm_response_handler_JSON import call_llm_and_return_JSON, initialise_llm, PROMPT_LIMIT
from utilities.paper_access import get_text, get_sentence_from_iri, get_section_from_sentence, get_paragraph_from_sentence
from utilities.content_processor import check_existence_in_sentence, tokenise_text, lemmatise_text


MODULE ='m03'
STAGE = 5

CURRENT_DIR = Path(__file__).parent.resolve()
OLD_KG_PATH = CURRENT_DIR / f"kg_{STAGE-1}.json"
NEW_KG_PATH = CURRENT_DIR / f"kg_{STAGE}.json"
TIME = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
LOG_PATH = CURRENT_DIR / f"./logs/{MODULE}_log_{STAGE}_{TIME}.txt"
TERMINAL_PATH = CURRENT_DIR / f"./logs/{MODULE}_terminal_{STAGE}_{TIME}.txt"

PROMPT_PATH_SECTION = CURRENT_DIR / f"prompt_{STAGE}_section.md"
PROMPT_PATH_PARAGRAPH = CURRENT_DIR / f"prompt_{STAGE}_paragraph.md"



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

    with open(PROMPT_PATH_SECTION, "r") as file:
        prompt_template_section = file.read()

    with open(PROMPT_PATH_PARAGRAPH, "r") as file:
        prompt_template_paragraph = file.read()

    llm = initialise_llm()

    terminal_file = open(TERMINAL_PATH, "w")
    log_file = open(LOG_PATH, "w")


    # =============================================================================
    # Finding matching node pairs + LLM double checking
    
    count = 0

    nodes_dict = {}
        
    for node in paper["nodes"]:
        nodes_dict[count] = node
        count += 1

    paper["matching_node_pairs"] = []

    for id_1, node_1 in nodes_dict.items():
        for id_2, node_2 in nodes_dict.items():
            if id_1 < id_2:

                # =============================================================================
                # Compare the embeddings

                node_embedding_1 = np.array(node_1["node_embedding"])
                node_embedding_2 = np.array(node_2["node_embedding"])

                label_embedding_1 = np.array(node_1["label_embedding"])
                label_embedding_2 = np.array(node_2["label_embedding"])

                description_embedding_1 = np.array(node_1["description_embedding"])
                description_embedding_2 = np.array(node_2["description_embedding"])

                if (np.dot(node_embedding_1, node_embedding_2) > 0.95
                    
                    or

                    np.dot(label_embedding_1, label_embedding_2) > 0.95 and
                    np.dot(description_embedding_1, description_embedding_2) > 0.9):

                    verbose = f"Potential Coreference found between '{node_1['label']}' and '{node_2['label']}'"
                    print(verbose)
                    terminal_file.write(verbose + "\n")

                    # =============================================================================
                    # Call the LLM for double checking

                    # title = paper["title"]
                    # authors = paper["authors"]
                    # keywords = paper["keywords"]
                    # paper_level_context = get_text(paper["sections"][0])

                    # label_1 = node_1["label"]
                    # types_1 = node_1["types"]
                    # description_1 = node_1["description"]
                    # sentence_iri_1 = node_1["mentions"][0]["reference"]
                    # sentence_1 = get_sentence_from_iri(sentence_iri_1, paper)
                    # paragraph_1 = get_paragraph_from_sentence(sentence_1, paper)
                    # section_1 = get_section_from_sentence(sentence_1, paper)
                    # sentence_level_context_1 = get_text(sentence_1)
                    # paragraph_level_context_1 = get_text(paragraph_1)
                    # section_level_context_1 = get_text(section_1)

                    # label_2 = node_2["label"]
                    # types_2 = node_2["types"]
                    # description_2 = node_2["description"]
                    # sentence_iri_2 = node_2["mentions"][0]["reference"]
                    # sentence_2 = get_sentence_from_iri(sentence_iri_2, paper)
                    # paragraph_2 = get_paragraph_from_sentence(sentence_2, paper)
                    # section_2 = get_section_from_sentence(sentence_2, paper)
                    # sentence_level_context_2 = get_text(sentence_2)
                    # paragraph_level_context_2 = get_text(paragraph_2)
                    # section_level_context_2 = get_text(section_2)


                    # prompt_paragraph = prompt_template_paragraph.format(
                    #     title=title,
                    #     authors=authors,
                    #     keywords=keywords,
                    #     paper_level_context=paper_level_context,
                    #     label_1=label_1,
                    #     types_1=types_1,
                    #     description_1=description_1,
                    #     sentence_level_context_1=sentence_level_context_1,
                    #     paragraph_level_context_1=paragraph_level_context_1,
                    #     label_2=label_2,
                    #     types_2=types_2,
                    #     description_2=description_2,
                    #     sentence_level_context_2=sentence_level_context_2,
                    #     paragraph_level_context_2=paragraph_level_context_2,
                    # )


                    # prompt_section = prompt_template_section.format(
                    #     title=title,
                    #     authors=authors,
                    #     keywords=keywords,
                    #     paper_level_context=paper_level_context,
                    #     label_1=label_1,
                    #     types_1=types_1,
                    #     description_1=description_1,
                    #     sentence_level_context_1=sentence_level_context_1,
                    #     section_level_context_1=section_level_context_1,
                    #     label_2=label_2,
                    #     types_2=types_2,
                    #     description_2=description_2,
                    #     sentence_level_context_2=sentence_level_context_2,
                    #     section_level_context_2=section_level_context_2,
                    # )
    

                    # # Check input limit
                    # prompt_paragraph_tokenised = tokenise_text(prompt_paragraph)
                    # prompt_section_tokenised = tokenise_text(prompt_section)


                    # if len(prompt_section_tokenised) < PROMPT_LIMIT:
                    #     prompt = prompt_section
                    # elif len(prompt_paragraph_tokenised) < PROMPT_LIMIT:
                    #     print("Warning: Prompt too long. Using paragraph level prompt instead.")
                    #     prompt = prompt_paragraph
                    # else:
                    #     raise ValueError("Prompt too long")

                    # # prompt = prompt_paragraph

                    # # Call the LLM
                    # response, log, original_response = call_llm_and_return_JSON(llm, prompt)

                    # if (response == None 
                    #     or "answer" not in response
                    #     or (not response["answer"] == True and not response["answer"] == False)):

                    #     verbose = f"Warning: JSON parsing error. Try String Matching."
                    #     print(verbose)
                    #     terminal_file.write(verbose + "\n")

                    #     if '"answer": false' in original_response:
                    #         response = {"answer": False}
                    #         verbose = f"Response Found!\nLLM Said: No"
                    #         print(verbose)
                    #         terminal_file.write(verbose + "\n")
                    #     elif '"answer": true' in original_response:
                    #         response = {"answer": True}
                    #         verbose = f"Response Found!\nLLM Said: Yes"
                    #         print(verbose)
                    #         terminal_file.write(verbose + "\n")
                    #         paper["matching_node_pairs"].append((id_1, id_2)) # !!!!!!!!!!!!
                    #     else:
                    #         verbose = f"Warning: LLM response not found. Assume not coreferent."
                    #         print(verbose)
                    #         terminal_file.write(verbose + "\n")

                    # else:
                    #     if response["answer"] == True:


                    verbose = f"LLM Said: Yes"
                    print(verbose)
                    terminal_file.write(verbose + "\n")
                    paper["matching_node_pairs"].append((id_1, id_2)) # !!!!!!!!!!!!


                    
                        # else:
                        #     verbose = f"LLM Said: No"
                        #     print(verbose)
                        #     terminal_file.write(verbose + "\n")

                    # log_file.write(log)
                    log_file.write("\n\n\n\n")
                    
                    
                    log_file.flush()
                    terminal_file.flush()

    terminal_file.close()
    log_file.close()


    # Remove nodes embeddings
    # for node in nodes_dict.values():
    #     del node["node_embedding"]
    #     del node["label_embedding"]
    #     del node["description_embedding"]

    paper["nodes"] = nodes_dict

    print(f"Total coreferences found: {len(paper['matching_node_pairs'])}")


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