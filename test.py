from nltk.corpus import words
import nltk
nltk.download('words')

# Get the word list and filter only alphabetic words (no punctuation/numbers)
word_list = [word.lower() for word in words.words() if word.isalpha()]

# Optional: Deduplicate and sort
word_list = sorted(set(word_list))

# Save to file
with open("large_word_list.txt", "w") as f:
    for word in word_list:
        f.write(f"{word}\n")

print(f"Saved {len(word_list)} words to 'large_word_list.txt'")
