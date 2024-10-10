import requests
import random
import heapq
from collections import defaultdict

# ConceptNet API base URL
CONCEPTNET_API_URL = "http://api.conceptnet.io/c/en/"

# Function to query ConceptNet API for related concepts


def query_conceptnet(concept, lang='en'):
    """
    Query ConceptNet to find related concepts to the given concept.
    Returns a list of related concepts and their weights.
    """
    url = f"{CONCEPTNET_API_URL}{concept.lower()}?offset=0&limit=1000"
    response = requests.get(url).json()

    related_concepts = []

    if 'edges' in response:
        for edge in response['edges']:
            # We are interested in the /r/RelatedTo, /r/Synonym, /r/IsA, etc.
            if edge['rel']['label'] in ['RelatedTo', 'Synonym', 'IsA', 'PartOf', 'HasA']:
                # Extract the concept and weight from the edge
                related_concept = edge['end']['label'] if edge['start']['label'] == concept else edge['start']['label']
                weight = edge['weight']
                related_concepts.append((related_concept, weight))

    return related_concepts

# Function to rank board concepts based on their relatedness to the query


def rank_board_concepts(board, query_concept, n):
    """
    Given a board (list of 25 concepts) and a query concept, find the top-n related concepts.
    """
    related_concepts = query_conceptnet(query_concept)

    # Dictionary to store the scores of board concepts
    board_scores = defaultdict(float)

    # For each related concept, if it's on the board, add its weight to the score
    for related_concept, weight in related_concepts:
        for board_concept in board:
            if board_concept.lower() == related_concept.lower():
                board_scores[board_concept] += weight

    # Get the top-n concepts from the board based on the scores
    top_n_concepts = heapq.nlargest(n, board_scores, key=board_scores.get)

    return top_n_concepts

# Function to create a training instance


def create_training_instance(board, query_concept, n):
    """
    Creates a training instance for a CodeNames-like task.
    Input: A board (5x5 grid of concepts) and a query (concept and number n).
    Output: n board concepts semantically related to the query concept.
    """
    # Find the top-n related concepts from the board
    top_n_related_concepts = rank_board_concepts(board, query_concept, n)

    # Format the training instance
    input_instance = {
        "board": board,
        "query": (query_concept, n)
    }
    output_instance = top_n_related_concepts

    return input_instance, output_instance

# Function to automatically generate a random board of concepts from ConceptNet


def generate_random_board(board_size=25):
    """
    Generate a random list of concepts to act as the board.
    Fetch random concepts from ConceptNet and return them as a list.
    """
    # Use ConceptNet's random endpoint to fetch random concepts
    url = f"{CONCEPTNET_API_URL}random?limit={board_size}"
    response = requests.get(url).json()

    board = []

    if 'edges' in response:
        for edge in response['edges']:
            # Extract the concept and ensure we don't repeat concepts on the board
            concept = edge['start']['label']
            if concept not in board:
                board.append(concept)

    # In case we didn't fetch enough distinct concepts, fill randomly from the pool
    while len(board) < board_size:
        board.append(random.choice(board))  # Ensure the board size is correct

    return board[:board_size]

# Generate training instances automatically


def generate_training_instances(num_instances=5, board_size=25):
    """
    Generate multiple training instances automatically.
    Each instance includes:
    - A random 5x5 board of concepts.
    - A randomly selected query concept from the board.
    - A randomly chosen number n (between 1 and 5).
    """
    training_data = []

    for _ in range(num_instances):
        # Generate a random board
        board = generate_random_board(board_size)

        # Randomly pick a query concept from the board
        query_concept = random.choice(board)

        # Randomly pick a number n (between 1 and 5)
        n = random.randint(1, 5)

        # Create a training instance
        input_instance, output_instance = create_training_instance(
            board, query_concept, n)
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
