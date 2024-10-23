import requests
import random
import heapq
from collections import defaultdict

# ConceptNet API base URL
CONCEPTNET_API_URL = "http://api.conceptnet.io/c/"


# Function to query ConceptNet API for related concepts
def query_conceptnet(
    concept,
    lang="en",
    allowed_relation_type=[
        "RelatedTo",
        "Synonym",
        "IsA",
        "PartOf",
        "HasA",
    ],
):
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
            if edge["rel"]["label"] in allowed_relation_type:
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


# Function to generate a board that includes n related concepts
def generate_board_with_related_concepts(query_concept, n, board_size=25):
    """
    Generate a board that includes the query concept and exactly n related concepts.
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

    # Add the query concept and related concepts to the board
    board = [query_concept] + top_n_related_concepts

    # Fill the remaining slots on the board with random unrelated concepts (ensuring no duplicates)
    while len(board) < board_size:
        random_concept = random.choice(related_concepts)[0]
        if random_concept not in board:
            board.append(random_concept)

    # Shuffle the board to randomize the placement of concepts
    random.shuffle(board)

    return board, top_n_related_concepts


# Function to create a training instance
def create_training_instance(query_concept, n, board_size=25):
    """
    Creates a training instance where the board contains the query concept and n related concepts.
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


# Generate and print some example training instances
if __name__ == "__main__":
    training_instances = generate_training_instances(3)

    for idx, (input_instance, output_instance) in enumerate(training_instances):
        print(f"Training Instance {idx + 1}:")
        print("Input:", input_instance)
        print("Output:", output_instance)
        print("\n")
