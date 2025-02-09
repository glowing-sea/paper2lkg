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


MODULE ='m03'
STAGE = 3

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
    # Checking

    number_of_paragraph_section_triples = 0
    
    for section in paper["sections"]:
        for paragraph in section["paragraphs"]:
            number_of_paragraph_section_triples += len(paragraph["triples"])
        number_of_paragraph_section_triples += len(section["triples"])

    print(f"Total number of triples at the section or paragraph level: {number_of_paragraph_section_triples}")


    number_of_sentence_triples = 0
    for section in paper["sections"]:
        for paragraph in section["paragraphs"]:
            for sentence in paragraph["sentences"]:
                number_of_sentence_triples += len(sentence["triples"])

    print(f"Total number of triples at the sentence level: {number_of_sentence_triples}")

    total_invalid_triples = 0
    total_triples = number_of_paragraph_section_triples + number_of_sentence_triples

    print (f"Total number of triples: {total_triples}")


    # =============================================================================
    # Triple Existence Check


    for section in paper["sections"]:
        text = get_text(section)
        new_triples = []   

        for triple in section["triples"]: 

            subject = triple["subject"]
            predicate = triple["predicate"]
            object = triple["object"]
            locations_found = []

            for paragraph in section["paragraphs"]:
                for sentence in paragraph["sentences"]:
                    sentence_text = get_text(sentence)
                    if check_existence_in_sentence(sentence_text, subject) and check_existence_in_sentence(sentence_text, object):
                        locations_found.append(sentence)


            if len(locations_found) == 0:
                if check_existence_in_sentence(text, subject) and check_existence_in_sentence(text, object):
                    new_triples.append((subject, predicate, object))
                    print(f"Info: Triple found at the section level: {subject} - {predicate} - {object}")
                else:
                    print(f"Warning: Triple not found at the section level: {subject} - {predicate} - {object}")
                    total_invalid_triples += 1
            elif len(locations_found) == 1:
                locations_found[0]["triples"].append((subject, predicate, object))
                print(f"Info: Triple found at the sentence level: {subject} - {predicate} - {object}")
            elif len(locations_found) > 1:
                locations_found[0]["triples"].append((subject, predicate, object))
                print(f"Warning: Multiple locations found for the triple: {subject} - {predicate} - {object}")
            else:
                raise ValueError("Triple Existence Check: Invalid number of locations found")


        section["triples"] = new_triples



        for paragraph in section["paragraphs"]:
            paragraph_text = get_text(paragraph)
            new_triples_paragraph = []

            for triple in paragraph["triples"]:

                subject = triple["subject"]
                predicate = triple["predicate"]
                object = triple["object"]
                locations_found = []

                for sentence in paragraph["sentences"]:
                    sentence_text = get_text(sentence)
                    if check_existence_in_sentence(sentence_text, subject) and check_existence_in_sentence(sentence_text, object):
                        locations_found.append(sentence)
                
                if len(locations_found) == 0:
                    if check_existence_in_sentence(paragraph_text, subject) and check_existence_in_sentence(paragraph_text, object):
                        new_triples_paragraph.append((subject, predicate, object))
                        print(f"Info: Triple found at the paragraph level: {subject} - {predicate} - {object}")
                    else:
                        print(f"Warning: Triple not found at the paragraph level: {subject} - {predicate} - {object}")
                        total_invalid_triples += 1
                elif len(locations_found) == 1:
                    locations_found[0]["triples"].append((subject, predicate, object))
                    print(f"Info: Triple found at the sentence level: {subject} - {predicate} - {object}")
                elif len(locations_found) > 1:
                    locations_found[0]["triples"].append((subject, predicate, object))
                    print(f"Warning: Multiple locations found for the triple: {subject} - {predicate} - {object}")
                else:
                    raise ValueError("Triple Existence Check: Invalid number of locations found")
            
                paragraph["triples"] = new_triples_paragraph



            for sentence in paragraph["sentences"]:
                sentence_text = get_text(sentence)
                new_triples = []

                for triple in sentence["triples"]:

                    if isinstance(triple, tuple):
                        subject = triple[0]
                        object = triple[2]
                        predicate = triple[1]
                    else:
                        subject = triple["subject"]
                        object = triple["object"]
                        predicate = triple["predicate"]

                    if check_existence_in_sentence(sentence_text, subject) and check_existence_in_sentence(sentence_text, object):
                        new_triples.append((subject, predicate, object))
                    else:
                        print(f"Warning: Triple not found at the sentence level: {subject} - {predicate} - {object}")
                        total_invalid_triples += 1

                sentence["triples"] = new_triples

                        

    # =============================================================================
    # Checking

    number_of_paragraph_section_triples = 0
    
    for section in paper["sections"]:
        for paragraph in section["paragraphs"]:
            number_of_paragraph_section_triples += len(paragraph["triples"])
        number_of_paragraph_section_triples += len(section["triples"])

    print(f"Total number of triples at the section or paragraph level: {number_of_paragraph_section_triples}")


    number_of_sentence_triples = 0
    for section in paper["sections"]:
        for paragraph in section["paragraphs"]:
            for sentence in paragraph["sentences"]:
                number_of_sentence_triples += len(sentence["triples"])

    print(f"Total number of triples at the sentence level: {number_of_sentence_triples}")

    print(f"Total number of invalid triples: {total_invalid_triples}")

    total_triples = number_of_paragraph_section_triples + number_of_sentence_triples + total_invalid_triples
    print (f"Total number of triples: {total_triples}")

    # =============================================================================

    # Duplicated Triple Elimination

    total_triples = 0

    for section in paper["sections"]:
        for paragraph in section["paragraphs"]:
            for sentence in paragraph["sentences"]:
                sentence["triples"] = list(dict.fromkeys(sentence["triples"]))
                total_triples += len(sentence["triples"])

            paragraph["triples"] = list(dict.fromkeys(paragraph["triples"]))
            total_triples += len(paragraph["triples"])

        section["triples"] = list(dict.fromkeys(section["triples"]))
        total_triples += len(section["triples"])

    print(f"Total number of triples after duplicated triple elimination: {total_triples}")
    

    # =============================================================================
    # Retrieve IRI

    for section in paper["sections"]:
        for paragraph in section["paragraphs"]:
            for sentence in paragraph["sentences"]:

                new_triples = []

                for triple in sentence["triples"]:
                    subject = triple[0]
                    object = triple[2]

                    subject_iri = None
                    object_iri = None

                    if subject in sentence["local_name_to_iri"]:
                        subject_iri = sentence["local_name_to_iri"][subject]
                    elif subject in paragraph["local_name_to_iri"]:
                        subject_iri = paragraph["local_name_to_iri"][subject]
                    elif subject in section["local_name_to_iri"]:
                        subject_iri = section["local_name_to_iri"][subject]
                    else:
                        pass

                    if object in sentence["local_name_to_iri"]:
                        object_iri = sentence["local_name_to_iri"][object]
                    elif object in paragraph["local_name_to_iri"]:
                        object_iri = paragraph["local_name_to_iri"][object]
                    elif object in section["local_name_to_iri"]:
                        object_iri = section["local_name_to_iri"][object]
                    else:
                        pass

                    if subject_iri and object_iri:
                        new_triples.append((subject_iri[0], triple[1], object_iri[0]))
                    else:
                        print(f"Warning (Sentence): Triple Consisting of New Mentions: {subject} - {triple[1]} - {object}")

                sentence["triples"] = new_triples

            # =============================================================================
            
            new_triples = []

            for triple in paragraph["triples"]:
                subject = triple[0]
                object = triple[2]

                subject_iri = None
                object_iri = None

                if subject in paragraph["local_name_to_iri"]:
                    subject_iri = paragraph["local_name_to_iri"][subject]
                elif subject in section["local_name_to_iri"]:
                    subject_iri = section["local_name_to_iri"][subject]
                else:
                    pass

                if object in paragraph["local_name_to_iri"]:
                    object_iri = paragraph["local_name_to_iri"][object]
                elif object in section["local_name_to_iri"]:
                    object_iri = section["local_name_to_iri"][object]
                else:
                    pass

                if subject_iri and object_iri:
                    new_triples.append((subject_iri[0], triple[1], object_iri[0]))
                else:
                    print(f"Warning (Paragraph): Triple Consisting of New Mentions: {subject} - {triple[1]} - {object}")

            paragraph["triples"] = new_triples

        # =============================================================================

        new_triples = []

        for triple in section["triples"]:
            subject = triple[0]
            object = triple[2]

            subject_iri = None
            object_iri = None

            if subject in section["local_name_to_iri"]:
                subject_iri = section["local_name_to_iri"][subject]
            else:
                pass

            if object in section["local_name_to_iri"]:
                object_iri = section["local_name_to_iri"][object]
            else:
                pass

            if subject_iri and object_iri:
                new_triples.append((subject_iri[0], triple[1], object_iri[0]))
            else:
                print(f"Warning (Section): Triple Consisting of New Mentions: {subject} - {triple[1]} - {object}")

        section["triples"] = new_triples

                        
    # =============================================================================


    total_triples = 0

    for section in paper["sections"]:
        for paragraph in section["paragraphs"]:
            for sentence in paragraph["sentences"]:
                total_triples += len(sentence["triples"])

            total_triples += len(paragraph["triples"])

        total_triples += len(section["triples"])

    print(f"Total number of triples after IRI retrieval: {total_triples}")


    # =============================================================================
    # Put triple into the paper level

    edges = []

    for section in paper["sections"]:
        for paragraph in section["paragraphs"]:
            for sentence in paragraph["sentences"]:
                edges.extend(sentence["triples"])
                del sentence["triples"]
                del sentence["local_name_to_iri"]
                del sentence["mentions"]

            edges.extend(paragraph["triples"])
            del paragraph["triples"]
            del paragraph["local_name_to_iri"]

        edges.extend(section["triples"])
        del section["triples"]
        del section["local_name_to_iri"]

    paper["edges"] = edges

    print(f"Total number of triples at the paper level: {len(edges)}")

    paper["edges"] = list(dict.fromkeys(paper["edges"]))

    print(f"Total number of triples at the paper level after duplicated triple elimination: {len(paper['edges'])}")
                        
    
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