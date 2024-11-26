import requests
from enums import Relations
from concept import Concept
import random
import spacy
import nltk
from nltk.corpus import stopwords
from typing import List
import time


CONCEPTNET_API_URL = "http://api.conceptnet.io/"
MAX_NUMBER_OF_EDGES = 10000

# Load Spacy's English model for POS tagging
nlp = spacy.load("en_core_web_sm")
# Download the stopwords list from NLTK
nltk.download("stopwords")
stop_words = set(stopwords.words("english"))


def build_complex_query_string(
    concept: Concept,
    is_it_start: bool = None,
    second_concept: Concept = None,
    relation: Relations = None,
    sources: str = None,
    offset=0,
    limit=20,
):
    """
    Build complex query URL to be able to find edges filtered by, start node, end node(or both), relation and source.
    Paggination is posible by offset and limit.
    Returns string representing the URL.
    """
    url = CONCEPTNET_API_URL + "query?"
    if is_it_start is None:
        url += f"node={concept.get_uri()}"
        if second_concept:
            url += f"&other={second_concept.get_uri()}"
    elif is_it_start:
        url += f"start={concept.get_uri()}"
        if second_concept:
            url += f"&end={second_concept.get_uri()}"
    else:
        url += f"end={concept.get_uri()}"
        if second_concept:
            url += f"&start={second_concept.get_uri()}"
    if relation:
        url += f"&rel={relation.value}"
    if sources:
        url += f"&sources={sources}"
    url += f"&offset={offset}"
    url += f"&limit={limit}"
    return url


# Function to add new concept in random_concepts if suitable
def add_new_concept(
    concept_json, concepts, lang, different_from_concepts: List[str] = None
):
    """
    Add new concept_json's label in concepts if suitable.
    """
    concept_label = concept_json["label"]
    if (
        concept_json["language"] == lang
        and concept_label not in concepts
        and is_valid_concept(concept_label)
    ):
        if different_from_concepts and (concept_label not in different_from_concepts):
            concepts.append(concept_label)
        elif different_from_concepts is None:
            concepts.append(concept_label)


# Function to get random unrelated concepts from ConceptNet
def get_random_concepts(n, different_from_concepts: List[str] = None, lang="en"):
    """
    Fetch random unrelated concepts from ConceptNet.
    Returns a list of random English concepts.
    """
    random_concepts = []
    concepts_for_lang = Concept(lang=lang)

    while len(random_concepts) < n:
        # Generate a random integer between 0 and 100
        random_integer = random.randint(0, 100)
        url = build_complex_query_string(
            concept=concepts_for_lang,
            offset=random_integer,
            limit=100,
        )
        start_time = time.time()
        response = requests.get(url).json()
        # End time
        end_time = time.time()
        # Calculate elapsed time
        elapsed_time = end_time - start_time
        print(
            f"Elapsed time for fetching random concepts: {elapsed_time:.2f} seconds ({url})"
        )
        if "edges" in response:
            for edge_json in response["edges"]:
                start_concept_json = edge_json["start"]
                end_concept_json = edge_json["end"]
                add_new_concept(
                    start_concept_json, random_concepts, lang, different_from_concepts
                )
                add_new_concept(
                    end_concept_json, random_concepts, lang, different_from_concepts
                )
                if len(random_concepts) >= n:
                    break
    return random_concepts[:n]


# Function to query ConceptNet API for related concepts
def query_conceptnet(
    concept: Concept,
    lang="en",
    relation_list: List[Relations] = [
        Relations.RelatedTo,
        Relations.Synonym,
        Relations.IsA,
        Relations.PartOf,
        Relations.HasA,
    ],
    limit_per_relation=20,
):
    """
    Query ConceptNet to find related concepts to the given concept.
    Returns a list of related concepts and their weights, filtered by language.
    """
    related_concepts = []
    print(concept.get_uri())
    for rel in relation_list:
        url = build_complex_query_string(
            concept=concept,
            second_concept=Concept(lang=lang),
            limit=limit_per_relation,
            relation=rel,
        )
        start_time = time.time()
        response_json = requests.get(url).json()
        # End time
        end_time = time.time()
        # Calculate elapsed time
        elapsed_time = end_time - start_time
        print(
            f"Elapsed time for fetching relation {rel.value}: {elapsed_time:.2f} seconds ({url})"
        )
        if "edges" in response_json:
            for edge_json in response_json["edges"]:
                start_concept_json = edge_json["start"]
                end_concept_json = edge_json["end"]
                related_concept_label = (
                    end_concept_json["label"]
                    if start_concept_json["label"].lower() == concept.label.lower()
                    else start_concept_json["label"]
                )
                weight = edge_json["weight"]
                # Check if related concept is a noun and not a stopword
                if is_valid_concept(related_concept_label):
                    related_concepts.append((related_concept_label, weight))
    return related_concepts


# Function to filter valid concepts based on POS and stopwords
def is_valid_concept(word):
    if word:
        doc = nlp(word)
        if len(doc) == 1:
            for token in doc:
                if token.text.lower() in stop_words:
                    return False
                if token.pos_ == "NOUN" and not token.is_stop:
                    return True
    return False
