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
from utilities.llm_response_handler_JSON_list import call_llm_and_return_a_list, initialise_llm
from utilities.paper_access import get_text
from utilities.content_processor import check_existence_in_sentence, tokenise_text, lemmatise_text


MODULE ='m02'
STAGE = 4

CURRENT_DIR = Path(__file__).parent.resolve()
OLD_KG_PATH = CURRENT_DIR / f"kg_{STAGE - 1}.json"
NEW_KG_PATH = CURRENT_DIR / f"kg_{STAGE}.json"


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


    # =============================================================================
    # Create a dictionary entry for each type of mentions in each sentence, paragraph, and section

    def merge_mentions(mention1, mention2):
        """
        Merge two mentions
        """
        return {
            "label": mention1["label"],
            "aliases": list(set(mention1["aliases"] + [mention2["label"]])),
            "types": list(set(mention1["types"] + mention2["types"]))
        }


    def create_mention_dict(text_chunk, mentions_dict, mention_type):
        """
        Create a mention dictionary
        """
        for mention in text_chunk[mention_type]:
            tokenised = tokenise_text(mention["label"])
            normalised = " ".join(lemmatise_text(tokenised, pos=None))
            if normalised not in mentions_dict:
                mentions_dict[normalised] = {
                    "label": mention["label"],
                    "aliases": [mention["label"]],
                    "types": mention["types"]
                }
            else:
                # Merging their types
                mentions_dict[normalised] = merge_mentions(mentions_dict[normalised], mention)
                if len(mentions_dict[normalised]["aliases"]) > 1:
                    print (f"Aliases: {mentions_dict[normalised]['aliases']}")


    for section in paper["sections"]:
        named_entities_dict = {}
        entities_dict = {}
        mentions_dict = {}

        create_mention_dict(section, named_entities_dict, "named_entities")
        create_mention_dict(section, entities_dict, "entities")
        create_mention_dict(section, mentions_dict, "mentions")

        section["named_entities"] = named_entities_dict
        section["entities"] = entities_dict
        section["mentions"] = mentions_dict

        for paragraph in section["paragraphs"]:
            named_entities_dict = {}
            entities_dict = {}
            mentions_dict = {}

            create_mention_dict(paragraph, named_entities_dict, "named_entities")
            create_mention_dict(paragraph, entities_dict, "entities")
            create_mention_dict(paragraph, mentions_dict, "mentions")

            paragraph["named_entities"] = named_entities_dict
            paragraph["entities"] = entities_dict
            paragraph["mentions"] = mentions_dict

            for sentence in paragraph["sentences"]:
                named_entities_dict = {}
                entities_dict = {}
                mentions_dict = {}

                create_mention_dict(sentence, named_entities_dict, "named_entities")
                create_mention_dict(sentence, entities_dict, "entities")
                create_mention_dict(sentence, mentions_dict, "mentions")

                sentence["named_entities"] = named_entities_dict
                sentence["entities"] = entities_dict
                sentence["mentions"] = mentions_dict



    # =============================================================================
    # Put mentions found at the section or paragraph level back to its original sentence level (all possible)
    # If such mentions are already in the sentence, merge them (including types)


    def put_mentions_back_to_sentence(sentence, normalised_mention, mention, mention_type):
        # A mention (named entity, entity, mention) 
        # is found at both the section level and the sentence level
        if normalised_mention in sentence[mention_type]:
            sentence[mention_type][normalised_mention] = merge_mentions(sentence[mention_type][normalised_mention], mention)
        
        # A named entity is found at the section level but not at the sentence level
        elif mention_type == "named_entities":
            if normalised_mention in sentence["entities"]:
                sentence["entities"][normalised_mention] = merge_mentions(sentence["entities"][normalised_mention], mention)
            else:
                sentence["entities"][normalised_mention] = mention
        
        # A entity is found at the section level but not at the sentence level
        elif mention_type == "entities" or mention_type == "mentions":
            if normalised_mention in sentence["entities"]:
                sentence["entities"][normalised_mention] = merge_mentions(sentence["entities"][normalised_mention], mention)
            else:
                sentence["entities"][normalised_mention] = mention
        
        # An mention is found at the section level but not at the sentence level
        elif mention_type == "mentions":
            if normalised_mention in sentence["mentions"]:
                sentence["mentions"][normalised_mention] = merge_mentions(sentence["mentions"][normalised_mention], mention)
            else:
                sentence["mentions"][normalised_mention] = mention
        
        else:
            raise ValueError("put_mentions_back_to_sentence: Invalid mention type")


    def put_mentions_from_section_back_to_sentence(section, mention_type):
        """
        Put mentions from the section back to the sentence
        """
        for normalised_mention, mention in section[mention_type].items():
            existence = False
            for paragraph in section["paragraphs"]:
                for sentence in paragraph["sentences"]:
                    if check_existence_in_sentence(sentence, normalised_mention):
                        put_mentions_back_to_sentence(sentence, normalised_mention, mention, mention_type)
                        existence = True
                        break

            if not existence:
                print(f"Mention not found in the section: {mention["label"]}")
                # print(f"Section text: {get_text(section)}")
        
        section.pop(mention_type, None)


    def put_mentions_from_paragraph_back_to_sentence(paragraph, mention_type):
        """
        Put mentions from the paragraph back to the sentence
        """
        for normalised_mention, mention in paragraph[mention_type].items():
            existence = False
            for sentence in paragraph["sentences"]:
                if check_existence_in_sentence(sentence, normalised_mention):
                    put_mentions_back_to_sentence(sentence, normalised_mention, mention, mention_type)
                    existence = True
                    break

            if not existence:
                print(f"Mention not found in the paragraph: {mention["label"]}")
                # print(f"Paragraph text: {get_text(paragraph)}")
        
        paragraph.pop(mention_type, None)



    for section in paper["sections"]:
        put_mentions_from_section_back_to_sentence(section, "named_entities")
        put_mentions_from_section_back_to_sentence(section, "entities")
        put_mentions_from_section_back_to_sentence(section, "mentions")
        for paragraph in section["paragraphs"]:
            put_mentions_from_paragraph_back_to_sentence(paragraph, "named_entities")
            put_mentions_from_paragraph_back_to_sentence(paragraph, "entities")
            put_mentions_from_paragraph_back_to_sentence(paragraph, "mentions")



    # # =============================================================================
    # # Check if the mentions exist in the sentence

    def check_mention_existence(sentence, mention_type):
        """
        Check if the mention exists in the sentence
        """
        keys_to_pop = []

        for mention_normalised, mention in sentence[mention_type].items():
            if not check_existence_in_sentence(sentence, mention_normalised):
                print(f"Mention '{mention["label"]}' not found in the sentence")
                print(f"{get_text(sentence)}\n")
                keys_to_pop.append(mention_normalised)
        
        for key in keys_to_pop:
            sentence[mention_type].pop(key)

    for section in paper["sections"]:
        for paragraph in section["paragraphs"]:
            for sentence in paragraph["sentences"]:
                check_mention_existence(sentence, "named_entities")
                check_mention_existence(sentence, "entities")
                check_mention_existence(sentence, "mentions")


    # =============================================================================
    # Classify the mentions through set subtraction

    for section in paper["sections"]:
        for paragraph in section["paragraphs"]:
            for sentence in paragraph["sentences"]:


                # General Terms = Entities - Named Entities
                key_to_pop = []
                for entity_normalised, entity in sentence["entities"].items():
                    if entity_normalised in sentence["named_entities"]:
                        key_to_pop.append(entity_normalised)
                        sentence["named_entities"][entity_normalised] = merge_mentions(
                            sentence["named_entities"][entity_normalised], entity)
                        
                for key in key_to_pop:
                    sentence["entities"].pop(key)


                # Others = Mentions - Named Entities - Entities
                key_to_pop = []
                for mention_normalised, mention in sentence["mentions"].items():
                    if mention_normalised in sentence["named_entities"]:
                        key_to_pop.append(mention_normalised)
                        sentence["named_entities"][mention_normalised] = merge_mentions(
                            sentence["named_entities"][mention_normalised], mention)
                    elif mention_normalised in sentence["entities"]:
                        key_to_pop.append(mention_normalised)
                        sentence["entities"][mention_normalised] = merge_mentions(
                            sentence["entities"][mention_normalised], mention)
                        
                for key in key_to_pop:
                    sentence["mentions"].pop(key)

                sentence["general_terms"] = sentence["entities"]
                sentence["others"] = sentence["mentions"]
                sentence.pop("entities")
                sentence.pop("mentions")
                        
    
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