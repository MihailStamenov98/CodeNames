import requests
import random

# ConceptNet API base URL
CONCEPTNET_API_URL = "http://api.conceptnet.io/c/"


# Function to query ConceptNet API for related concepts
def query_conceptnet(concept, lang="en"):
    """
    Query ConceptNet to find related concepts to the given concept.
    Returns a list of related concepts and their weights, filtered by language.
    """
    url = f"{CONCEPTNET_API_URL}{lang}/{concept.lower()}?offset=0&limit=1000"
    response = requests.get(url).json()

    related_concepts = []

    if "edges" in response:
        for edge in response["edges"]:
            # We are interested in the /r/RelatedTo, /r/Synonym, /r/IsA, etc.
            if edge["rel"]["label"] in [
                "RelatedTo",
                "Synonym",
                "IsA",
                "PartOf",
                "HasA",
            ]:
                # Ensure the concept is in English
                start_concept = edge["start"]
                end_concept = edge["end"]

                if (
                    start_concept["language"] == lang
                    and end_concept["language"] == lang
                ):
                    # Extract the concept and weight from the edge
                    related_concept = (
                        end_concept["label"]
                        if start_concept["label"].lower() == concept.lower()
                        else start_concept["label"]
                    )
                    weight = edge["weight"]
                    related_concepts.append((related_concept, weight))

    return related_concepts


# Function to get random unrelated concepts from ConceptNet
def get_random_concepts(n, lang="en"):
    """
    Fetch random unrelated concepts from ConceptNet.
    Returns a list of random English concepts.
    """
    random_concepts = []
    url = f"{CONCEPTNET_API_URL}{lang}/random?limit=100"

    while len(random_concepts) < n:
        response = requests.get(url).json()

        if "edges" in response:
            for edge in response["edges"]:
                start_concept = edge["start"]
                end_concept = edge["end"]

                # Ensure the concept is in English and not already in the list
                if (
                    start_concept["language"] == lang
                    and start_concept["label"] not in random_concepts
                ):
                    random_concepts.append(start_concept["label"])

                if (
                    end_concept["language"] == lang
                    and end_concept["label"] not in random_concepts
                ):
                    random_concepts.append(end_concept["label"])

                if len(random_concepts) >= n:
                    break

    return random_concepts[:n]


# Function to generate a board that includes exactly n related concepts and random unrelated concepts
def generate_board_with_related_concepts(query_concept, n, board_size=25):
    """
    Generate a board that includes the query concept and exactly n related concepts,
    and the rest of the board is filled with random unrelated English concepts from ConceptNet.
    """
    # Query ConceptNet for related concepts to the query concept
    related_concepts = query_conceptnet(query_concept)

    # Sort related concepts by their weight (highest relevance first)
    sorted_related_concepts = [
        concept
        for concept, _ in sorted(related_concepts, key=lambda x: x[1], reverse=True)
    ]

    # Select the top-n related concepts
    top_n_related_concepts = sorted_related_concepts[:n]
    # Start the board with the query concept and related concepts
    board = top_n_related_concepts.copy()

    # Get random unrelated concepts to fill the board (excluding related ones)
    random_unrelated_concepts = get_random_concepts(board_size - n)

    # Combine the related and random unrelated concepts
    board += random_unrelated_concepts

    # Shuffle the board to randomize placement of the related and unrelated concepts
    random.shuffle(board)

    return board, top_n_related_concepts


# Function to create a training instance
def create_training_instance(query_concept, n, board_size=25):
    """
    Creates a training instance where the board contains exactly n related concepts to the query concept.
    The rest of the board is filled with random unrelated concepts.
    Input: A query concept and a number n.
    Output: The board with exactly n related concepts included in the output.
    """
    # Generate the board with the query concept and n related concepts
    board, top_n_related_concepts = generate_board_with_related_concepts(
        query_concept, n, board_size
    )
    # Format the training instance
    input_instance = {"board": board, "query": (query_concept, n)}
    output_instance = top_n_related_concepts

    return input_instance, output_instance


# Function to automatically generate multiple training instances
def generate_training_instances(num_instances=5, board_size=25):
    """
    Generate multiple training instances.
    Each instance includes:
    - A random 5x5 board of concepts (with a query and n related concepts).
    - A query concept from the board.
    - A chosen number n (between 1 and 5).
    """
    training_data = []

    for _ in range(num_instances):
        # Choose a random query concept (you can hardcode or select from a list of English words)
        query_concept = random.choice(
            [
                "dog",
                "apple",
                "car",
                "tree",
                "water",
                "computer",
                "city",
                "music",
                "book",
            ]
        )

        # Randomly pick a number n (between 1 and 5)
        n = random.randint(1, 5)

        # Create a training instance
        input_instance, output_instance = create_training_instance(
            query_concept, n, board_size
        )
        training_data.append((input_instance, output_instance))

    return training_data


def get_concept_edges(concept, lang="en"):
    url = f"http://api.conceptnet.io/c/{lang}/{concept}"
    response = requests.get(url)
    return response.json()


def extract_n_ary_relations(concept_list):
    edges_list = [get_concept_edges(concept)["edges"] for concept in concept_list]
    # Find relationships from concept1 to concept2 and concept2 to concept3
    rel_list = [
        [
            edge
            for edge in edges_list[i]
            if (concept_list[i + 1] in edge["end"]["label"])
            or (concept_list[i + 1] in edge["start"]["label"])
        ]
        for i in range(len(concept_list) - 1)
    ]
    are_connected = True
    # Aggregate as n-ary relation
    for i in range(len(concept_list) - 1):
        are_connected = are_connected and rel_list[i]
    if are_connected:
        message = f""
        for i in range(len(concept_list) - 1):
            message = message + f"{rel_list[i][0]['surfaceText']} and "
        return message
    else:
        return "No n-ary relationship found"
