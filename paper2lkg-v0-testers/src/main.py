from multiprocessing import Process
import os
import time
import sys
from pathlib import Path

# Add the current directory to sys.path
CURRENT_DIR = Path(__file__).parent.resolve()
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

MODULES = CURRENT_DIR / "modules"

sys.path.append(str(MODULES))

def m01(dataset, paper_index):
    from modules.m01_kg_preprocessing.run_1_kg_preprocessing import run as run_1
    run_1(dataset, paper_index)
    print("module 01 run 1 done")

def m02():
    from modules.m02_mention_extraction_typing.run_1_named_entity_extraction import run as run_1
    from modules.m02_mention_extraction_typing.run_2_entity_extraction import run as run_2
    from modules.m02_mention_extraction_typing.run_3_mention_extraction import run as run_3
    from modules.m02_mention_extraction_typing.run_4_mention_checking_classification import run as run_4
    from modules.m02_mention_extraction_typing.run_5_graph_node_creation import run as run_5

    run_1()
    print("module 02 run 1 done")
    run_2()
    print("module 02 run 2 done")
    run_3()
    print("module 02 run 3 done")
    run_4()
    print("module 02 run 4 done")
    run_5()
    print("module 02 run 5 done")

def m03():
    from modules.m03_entity_resolution_disambiguation.run_1_entity_disambiguation import run as run_1_entity_disambiguation
    from modules.m03_entity_resolution_disambiguation.run_2_familiarity_checking import run as run_2_familiarity_checking
    from modules.m03_entity_resolution_disambiguation.run_3_description_generation import run as run_3_description_generation
    from modules.m03_entity_resolution_disambiguation.run_4_generate_embeddings import run as run_4_generate_embeddings
    from modules.m03_entity_resolution_disambiguation.run_5_similarity_matching import run as run_5_similarity_matching
    from modules.m03_entity_resolution_disambiguation.run_6_merging_nodes import run as run_6_merging_nodes
    from modules.m03_entity_resolution_disambiguation.run_7_assign_irl import run as run_7_assign_irl

    run_1_entity_disambiguation()
    print("module 03 run 1 done")
    run_2_familiarity_checking()
    print("module 03 run 2 done")
    run_3_description_generation()
    print("module 03 run 3 done")
    run_4_generate_embeddings()
    print("module 03 run 4 done")
    run_5_similarity_matching()
    print("module 03 run 5 done")
    run_6_merging_nodes()
    print("module 03 run 6 done")
    run_7_assign_irl()
    print("module 03 run 7 done")

def m04():
    from modules.m04_local_relation_extraction.run_1_triple_extraction import run as run_1_triple_extraction
    from modules.m04_local_relation_extraction.run_2_triple_refinement import run as run_2_triple_refinement
    from modules.m04_local_relation_extraction.run_3_triple_existence_check import run as run_3_triple_existence_check

    run_1_triple_extraction()
    print("module 04 run 1 done")
    run_2_triple_refinement()
    print("module 04 run 2 done")
    run_3_triple_existence_check()
    print("module 04 run 3 done")

def m05():
    from modules.m05_global_relation_extraction.run_1_paper_summary import run as run_1_paper_summary
    from modules.m05_global_relation_extraction.run_2_relevant_entities import run as run_2_relevant_entities
    from modules.m05_global_relation_extraction.run_3_document_re import run as run_3_document_re
    from modules.m05_global_relation_extraction.run_4_subject_identification import run as run_4_subject_identification

    run_1_paper_summary()
    print("module 05 run 1 done")
    run_2_relevant_entities()
    print("module 05 run 2 done")
    run_3_document_re()
    print("module 05 run 3 done")
    run_4_subject_identification()
    print("module 05 run 4 done")

def m06():
    from modules.m06_schema_generation.run_1_type_description_gen import run as run_1_type_description_gen
    from modules.m06_schema_generation.run_2_ontology_creation import run as run_2_ontology_creation
    from modules.m06_schema_generation.run_3_predicate_description_gen import run as run_3_predicate_description_gen
    from modules.m06_schema_generation.run_4_predicate_normalisation import run as run_4_predicate_normalisation
    from modules.m06_schema_generation.run_5_merging_predicates import run as run_5_merging_predicates

    run_1_type_description_gen()
    print("module 06 run 1 done")
    run_2_ontology_creation()
    print("module 06 run 2 done")
    run_3_predicate_description_gen()
    print("module 06 run 3 done")
    run_4_predicate_normalisation()
    print("module 06 run 4 done")
    run_5_merging_predicates()

def m07(dataset, paper_index):
    from modules.m07_kg_postprocessing.run_1_json_to_ttl import run as run_1_json_to_ttl

    run_1_json_to_ttl(dataset, paper_index)
    print("module 07 run 1 done")


if __name__ == '__main__':

    DATASET = "test"
    PAPER_INDEX = 3

    m01(DATASET, PAPER_INDEX)
    m02()
    m03()
    m04()
    m05()
    m06()
    m07(DATASET, PAPER_INDEX)


