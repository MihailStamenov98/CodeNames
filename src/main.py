import random
from enums import Part_of_Speech
from query_conceptnet import (
    get_random_concepts,
    query_conceptnet,
    Concept,
)

import time


# Function to generate a board that includes exactly n related concepts and random unrelated concepts
def generate_board_with_related_concepts(
    query_concept_label, n, lang="en", board_size=25
):
    """
    Generate a board that includes the query concept and exactly n related concepts,
    and the rest of the board is filled with random unrelated English concepts from ConceptNet.
    """
    query_concept = Concept(
        lang=lang, label=query_concept_label, type=Part_of_Speech.NOUN
    )
    # Query ConceptNet for related concepts to the query concept
    start_time = time.time()
    related_concepts = query_conceptnet(concept=query_concept, lang=lang)
    end_time = time.time()
    # Calculate elapsed time
    elapsed_time = end_time - start_time
    print(f"Related concepts took: {elapsed_time:.2f} seconds")
    print(f"Related concepts: {related_concepts}")
    print("------------Related concepts ENDED-----------------")
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
    start_time = time.time()
    random_unrelated_concepts = get_random_concepts(
        n=board_size - n,
        different_from_concepts=board + [query_concept.label],
        lang=lang,
    )
    end_time = time.time()
    # Calculate elapsed time
    elapsed_time = end_time - start_time
    print(
        f"Get random concepts took: {elapsed_time:.2f} seconds for {board_size - n} concepts"
    )

    # Combine the related and random unrelated concepts
    board += random_unrelated_concepts

    # Shuffle the board to randomize placement of the related and unrelated concepts
    random.shuffle(board)

    return board, top_n_related_concepts


# Function to create a training instance
def create_training_instance(query_concept_label, n, lang="en", board_size=25):
    """
    Creates a training instance where the board contains exactly n related concepts to the query concept.
    The rest of the board is filled with random unrelated concepts.
    Input: A query concept and a number n.
    Output: The board with exactly n related concepts included in the output.
    """
    # Generate the board with the query concept and n related concepts
    board, top_n_related_concepts = generate_board_with_related_concepts(
        query_concept_label=query_concept_label, n=n, board_size=board_size, lang=lang
    )
    # Format the training instance
    input_instance = {"board": board, "query": (query_concept_label, n)}
    output_instance = top_n_related_concepts

    return input_instance, output_instance


# Function to automatically generate multiple training instances
def generate_training_instances(num_instances=5, board_size=25, lang="en"):
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
        query_concept_label = random.choice(
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

        # Randomly pick a number n (between 1 and board_size // 2)
        n = random.randint(1, board_size // 2)

        # Create a training instance
        input_instance, output_instance = create_training_instance(
            query_concept_label=query_concept_label,
            n=n,
            board_size=board_size,
            lang=lang,
        )
        training_data.append((input_instance, output_instance))

    return training_data
