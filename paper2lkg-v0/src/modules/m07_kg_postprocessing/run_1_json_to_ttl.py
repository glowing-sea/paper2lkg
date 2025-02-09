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
# from utilities.llm_response_handler_JSON_list import call_llm_and_return_a_list, initialise_llm
# from utilities.paper_access import get_text_from_section, get_text_from_paragraph, get_text


MODULE ='m07'
STAGE = 1

CURRENT_DIR = Path(__file__).parent.resolve()
# PROMPT_PATH = CURRENT_DIR / f"prompt_{STAGE}_template.md"
# PROMPT_EXAMPLE_PATH = CURRENT_DIR / f"prompt_{STAGE}_examples.json"
# LOG_PATH = CURRENT_DIR / f"./logs/{MODULE}_log_{STAGE}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt"

# Ensure logs folder exists
LOGS_DIR = CURRENT_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Define log path
LOG_PATH = LOGS_DIR / f"{MODULE}_log_{STAGE}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt"


def run(dataset, paper_index, model_name):

    OLD_KG_PATH = CURRENT_DIR / f"../m06_schema_generation/kg_5.json"
    NEW_KG_PATH = CURRENT_DIR / f"../../../data/output/kg_{dataset}_{paper_index}_{model_name}.json"
    NEW_KG_TTL_PATH = CURRENT_DIR / f"../../../data/output/kg_{dataset}_{paper_index}_{model_name}.ttl"

    OUTPUT_FOLDER = CURRENT_DIR / f"../../../data/output/"

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"Folder '{OUTPUT_FOLDER}' created.")
    else:
        print(f"Folder '{OUTPUT_FOLDER}' already exists.")


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



    from rdflib import Graph, Namespace, Literal, RDF, RDFS, URIRef
    from rdflib.namespace import DC, OWL, XSD, SKOS

    # Define namespaces
    ASKG_DATA = Namespace("https://www.anu.edu.au/data/scholarly/")
    ASKG_ONTO = Namespace("https://www.anu.edu.au/onto/scholarly#")
    # WD = Namespace("http://www.wikidata.org/entity/")
    # DOMO = Namespace("https://www.anu.edu.au/onto/domo#")
    SCHEMA = Namespace("http://schema.org/")

    # Create a new RDF graph
    g = Graph()

    # Bind namespaces to prefixes
    g.bind("askg-data", ASKG_DATA)
    g.bind("askg-onto", ASKG_ONTO)
    g.bind("dc", DC)
    g.bind("owl", OWL)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    # g.bind("wd", WD) # wd:entity
    # g.bind("domo", DOMO) # domo:keyword
    g.bind("skos", SKOS) # skos:broader
    g.bind("xsd", XSD) # ^^xsd:string
    g.bind("schema", SCHEMA) # schema:text


    # Paper
    paper_iri = ASKG_DATA[paper["iri"]]
    # paper_iri = ASKG_DATA["Paper-1"]


    def get_iri(local_iri):
        return paper_iri + "-" + local_iri



    g.add((paper_iri, RDF.type, ASKG_ONTO.Paper))
    g.add((paper_iri, DC.title, Literal(paper["title"], lang="en")))

    for author in paper["authors"]:
        g.add((paper_iri, ASKG_ONTO.hasAuthor, Literal(author, lang="en")))
    for keyword in paper["keywords"]:
        g.add((paper_iri, ASKG_ONTO.hasKeyword, Literal(keyword, lang="en")))

    for section in paper["sections"]:
        section_iri = get_iri(section["iri"])
        g.add((section_iri, RDF.type, ASKG_ONTO.Section))
        g.add((section_iri, DC.title, Literal(section["subtitle"], lang="en"))) 

        for paragraph in section["paragraphs"]:
            paragraph_iri = get_iri(paragraph["iri"])
            g.add((paragraph_iri, RDF.type, ASKG_ONTO.Paragraph))

            for sentence in paragraph["sentences"]:
                sentence_iri = get_iri(sentence["iri"])
                g.add((sentence_iri, RDF.type, ASKG_ONTO.Sentence))
                g.add((sentence_iri, ASKG_ONTO.hasText, Literal(sentence["text"], lang="en")))

                g.add((paragraph_iri, ASKG_ONTO.hasSentence, sentence_iri))

            g.add((section_iri, ASKG_ONTO.hasParagraph, paragraph_iri))
        
        g.add((paper_iri, ASKG_ONTO.hasSection, section_iri))


    g.add((ASKG_ONTO.NamedEntity, RDFS.subClassOf, ASKG_ONTO.Entity))
    g.add((ASKG_ONTO.GeneralTerm, RDFS.subClassOf, ASKG_ONTO.Entity))
    g.add((ASKG_ONTO.OtherEntity, RDFS.subClassOf, ASKG_ONTO.Entity))



    # Entities
    for entity_iri, entity in paper["nodes"].items():
        entity_iri = get_iri(entity_iri)
        
        g.add((entity_iri, RDFS.label, Literal(entity["label"], lang="en")))

        for types in entity["types"]:
            g.add((entity_iri, ASKG_ONTO.hasTypeLabel, Literal(types, lang="en")))
        for alias in entity["aliases"]:
            g.add((entity_iri, SKOS.altLabel, Literal(alias, lang="en")))

        g.add((entity_iri, SCHEMA.description, Literal(entity["description"], lang="en")))

        if entity["node_type"] == "named entity":
            g.add((entity_iri, RDF.type, ASKG_ONTO.NamedEntity))
        elif entity["node_type"] == "general term":
            g.add((entity_iri, RDF.type, ASKG_ONTO.GeneralTerm))
        elif entity["node_type"] == "other":
            g.add((entity_iri, RDF.type, ASKG_ONTO.OtherEntity))
        else:
            raise ValueError("Unknown entity type")
        
        g.add((entity_iri, ASKG_ONTO.hasRelevanceScore, Literal(entity["relevance"], datatype=XSD.float)))

        for mention in entity["mentions"]:
            mention_iri = get_iri(mention["iri"])
            g.add((mention_iri, RDF.type, ASKG_ONTO.Mention))
            g.add((mention_iri, RDFS.label, Literal(mention["local_name"], lang="en")))
            sentence_mentioned_in = paper_iri + "-" + mention["reference"]
            g.add((mention_iri, ASKG_ONTO.mentionedIn, sentence_mentioned_in))
            g.add((entity_iri, ASKG_ONTO.hasMention, mention_iri))



    # Predicates
    for predicate_iri, predicate in paper["predicates"].items():
        predicate_iri = get_iri(predicate_iri)
        g.add((predicate_iri, RDF.type, ASKG_ONTO.Predicate))
        g.add((predicate_iri, RDFS.label, Literal(predicate["label"], lang="en")))
        g.add((predicate_iri, SCHEMA.description, Literal(predicate["description"], lang="en")))


    # Relations

    for triple in paper["triples"]:
        subject_iri = paper_iri + "-" + triple[0]
        predicate_iri = paper_iri + "-" + triple[1]
        object_iri = paper_iri + "-" + triple[2]

        g.add((subject_iri, predicate_iri, object_iri))


    for triple in paper["triples_typing"]:
        subject_iri = paper_iri + "-" + triple[0]
        predicate_iri = SKOS.broader
        object_iri = paper_iri + "-" + triple[2]

        g.add((subject_iri, predicate_iri, object_iri))



    with open(NEW_KG_TTL_PATH, 'wb') as f:
        f.write(g.serialize(format='turtle').encode("utf-8"))


    # =============================================================================
    # Tidy up and save the KG


    finish_time = time.time() - start_time
    print(f"Finished in {finish_time} seconds")
    if "times" not in paper:
        paper["times"] = []
    paper["times"].append(finish_time)

    print(f"Total time: {sum(paper['times']) / 60} minutes")


    # Save the KG
    with open(NEW_KG_PATH, "w") as f:
        json.dump(paper, f, indent=2)


if __name__ == "__main__":
    dataset = "test"
    model_name = "g"
    paper_index =1
    run(dataset, paper_index, model_name)