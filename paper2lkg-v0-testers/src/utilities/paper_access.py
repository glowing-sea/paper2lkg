# Packages
from pathlib import Path
import sys
import numpy as np
import random


# # Add packages to sys.path
# UTILITIES_RELATIVE_PATH = '../'
# UTILITIES_ABSOLUTE_PATH = str((Path(__file__).parent / UTILITIES_RELATIVE_PATH).resolve())
# if UTILITIES_ABSOLUTE_PATH not in sys.path:
#     sys.path.append(UTILITIES_ABSOLUTE_PATH)

# Assisted by ChatGPT
def relevant_sentences(query_embedding, k, kg):
    # Flatten the KG
    sentences = []
    sentences_embedding = []
    
    for paper in kg["papers"]:
        for section in paper["sections"]:
            for paragraph in section["paragraphs"]:
                for sentence in paragraph["sentences"]:
                    sentences.append(sentence)
                    sentences_embedding.append(sentence["embedding"])

    # Convert to numpy arrays
    sentences_embedding = np.array(sentences_embedding)
    query_embedding = np.array(query_embedding)

    # Calculate cosine similarity using @ for matrix multiplication (dot product)
    similarities = sentences_embedding @ query_embedding

    # Sort sentences based on similarity in descending order
    sorted_indices = np.argsort(similarities)[::-1]

    # Reorder sentences list based on the similarity scores
    sorted_sentences = [sentences[i] for i in sorted_indices]

    # Return top-k most relevant sentences
    return sorted_sentences[:k]


# Assisted by ChatGPT
def relevant_sections(query_embedding, k, kg):
    # Flatten the KG
    sentences = []
    sentences_embedding = []
    
    for paper in kg["papers"]:
        for section in paper["sections"]:
            sentences.append(section)
            sentences_embedding.append(section["embedding"])

    # Convert to numpy arrays
    sentences_embedding = np.array(sentences_embedding)
    query_embedding = np.array(query_embedding)

    # Calculate cosine similarity using @ for matrix multiplication (dot product)
    similarities = sentences_embedding @ query_embedding

    # Sort sentences based on similarity in descending order
    sorted_indices = np.argsort(similarities)[::-1]

    # Reorder sentences list based on the similarity scores
    sorted_sentences = [sentences[i] for i in sorted_indices]

    # Return top-k most relevant sentences
    return sorted_sentences[:k]


def random_sentences(k, kg):
    """
    Get k random sentences from the KG
    """
    sentences = []
    for paper in kg["papers"]:
        for section in paper["sections"]:
            for paragraph in section["paragraphs"]:
                for sentence in paragraph["sentences"]:
                    sentences.append(sentence)
    return random.sample(sentences, k)


def count_sentences(context):
    """
    Count the number of sentences in a paper.
    """
    if "text" in context:
        return 1
    elif "sentences" in context:
        return len(context["sentences"])
    elif "paragraphs" in context:
        return sum([len(paragraph["sentences"]) for paragraph in context["paragraphs"]])
    elif "sections" in context:
        return sum([len(paragraph["sentences"]) for section in context["sections"] for paragraph in section["paragraphs"]])
    else:
        raise ValueError("Context does not have text attribute")


def get_text_from_paragraph(paragraph, truncate_level=0):
    """
    Get the text of a paragraph by concatenating the text of its sentences.
    """
    paragraph_length = len(paragraph["sentences"])
    updated_length = max(paragraph_length // 2 ** truncate_level, 1)
    sentences = paragraph["sentences"][:updated_length]
    paragraph_text = " ".join([sentence["text"] for sentence in sentences]) # inspired by Copilot
    return paragraph_text


def get_text_from_section(section, truncate_level=0):
    """
    Get the text of a section by concatenating the text of its paragraphs.
    """
    section_length = len(section["paragraphs"])
    updated_length = section_length


    while truncate_level > 0:
        updated_length = updated_length // 2
        truncate_level -= 1
        if updated_length == 0 or updated_length == 1:
            break
    
    if updated_length == 0:
        section_text = get_text_from_paragraph(section["paragraphs"][0], truncate_level - 1)
    elif updated_length == 1:
        section_text = get_text_from_paragraph(section["paragraphs"][0], truncate_level)
    else:
        paragraphs = section["paragraphs"][:updated_length]
        section_text = "\n\n".join([get_text_from_paragraph(paragraph) for paragraph in paragraphs])

    return section_text

def get_text(context, truncate_level=0):
    """
    Get the text of a context.
    """
    if "text" in context:
        return context["text"]
    elif "sentences" in context:
        return get_text_from_paragraph(context, truncate_level)
    elif "paragraphs" in context:
        return get_text_from_section(context, truncate_level)
    else:
        raise ValueError("Context does not have text attribute")

def get_predicate_from_iri(iri: str, kg: dict) -> dict:
    """
    IRL -> predicate
    """
    for predicate in kg["predicates"]:
        if predicate["iri"] == iri:
            return predicate
    raise ValueError(f"Predicate with IRL {iri} not found in the KG")

def get_entity_from_iri(iri: str, paper: dict) -> dict:
    """
    IRL -> entity
    """
    for entity in paper["entities"]:
        if entity["iri"] == iri:
            return entity
    raise ValueError(f"Entity with IRL {iri} not found in the KG")

def get_sentence_from_iri(iri: str, paper: dict) -> dict:
    """
    IRL -> sentence
    """
    for section in paper["sections"]:
        for paragraph in section["paragraphs"]:
            for sentence in paragraph["sentences"]:
                if sentence["iri"] == iri:
                    return sentence
    raise ValueError(f"Sentence with IRL {iri} not found in the KG")


def get_paragraph_from_iri(iri, paper):
    """
    IRL -> paragraph
    """
    for section in paper["sections"]:
        for paragraph in section["paragraphs"]:
            if paragraph["iri"] == iri:
                return paragraph
    assert False, f"Paragraph with IRL {iri} not found in the KG"


def get_section_from_iri(iri, paper):
    """
    IRL -> section
    """
    for section in paper["sections"]:
        if section["iri"] == iri:
            return section
    assert False, f"Section with IRL {iri} not found in the KG"


def get_index_from_sentence(sen, paper):
    """
    sentence -> section index, paragraph index, sentence index
    """
    sen_iri = sen["iri"]
    for i, section in enumerate(paper["sections"]):
        for j, paragraph in enumerate(section["paragraphs"]):
            for k, sentence in enumerate(paragraph["sentences"]):
                if sentence["iri"] == sen_iri:
                    return i, j, k
    else:
        raise ValueError(f"Sentence with IRL {sen_iri} not found in the KG")
    
def get_index_from_paragraph(par, paper):
    """
    paragraph -> section index, paragraph index
    """
    par_iri = par["iri"]
    for i, section in enumerate(paper["sections"]):
        for j, paragraph in enumerate(section["paragraphs"]):
            if paragraph["iri"] == par_iri:
                return i, j
    else:
        raise ValueError(f"Paragraph with IRL {par_iri} not found in the KG")
    
def get_index_from_section(sec, paper):
    """
    section -> section index
    """
    sec_iri = sec["iri"]
    for i, section in enumerate(paper["sections"]):
        if section["iri"] == sec_iri:
            return i
    else:
        raise ValueError(f"Section with IRL {sec_iri} not found in the KG")
    

def get_paragraph_from_sentence(sen, paper):
    """
    sentence -> paragraph
    """
    i, j, _ = get_index_from_sentence(sen, paper)
    return paper["sections"][i]["paragraphs"][j]

def get_section_from_sentence(sen, paper):
    """
    sentence -> section
    """
    i, _, _ = get_index_from_sentence(sen, paper)
    return paper["sections"][i]


if __name__ == "__main__":
    pass

