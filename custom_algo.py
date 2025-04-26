from rapidfuzz import process

def get_best_matches_from_file(input_letters, file_path, output_file_path, top_k=10, max_word_length=8):
    """
    Suggest best word matches based on mistyped letters using a file as the dataset and
    write results to an output file. Clears the output file each time it's run.

    Parameters:
    - input_letters (list of str): Mistyped letters by the user.
    - file_path (str): Path to the file containing a list of valid words (one per line).
    - output_file_path (str): Path to the output file where matches will be written.
    - top_k (int): Number of best matches to return. Default is 10.
    - max_word_length (int): Maximum allowed length of words to consider. Default is 8.

    Returns:
    - list of tuples: [(word, similarity_score), ...]
    """
    try:
        with open(file_path, 'r') as f:
            words = [line.strip().lower() for line in f if line.strip().isalpha()]
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return []

    # ✅ Only keep real words with length >= 2
    filtered_words = [word for word in words if 2 <= len(word) <= max_word_length]

    input_str = ''.join(input_letters)

    matches = process.extract(input_str, filtered_words, limit=top_k)

    # Write results to output file (clears file first)
    with open(output_file_path, 'w') as out_file:
        for word, score, _ in matches:
            out_file.write(f"{word},{score:.2f}\n")

    return matches
