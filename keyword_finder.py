import re
from collections import Counter
import string
import os

# Load common English words to ignore
def load_common_words(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return set(word.strip().lower() for word in file.readlines())

# Process and extract keywords from the job description
def extract_keywords(text, common_words):
    # Clean text by removing punctuation and converting to lowercase
    text = text.translate(str.maketrans('', '', string.punctuation)).lower()
    
    # Split text into words
    words = text.split()
    
    # Filter out common words
    keywords = [word for word in words if word not in common_words]
    
    # Count the frequency of each keyword
    keyword_counts = Counter(keywords)
    
    return keyword_counts

# Load existing keywords from file
def load_existing_keywords(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        # Extract keyword counts from file
        existing_counts = Counter()
        for line in lines[1:]:
            keyword, count = line.strip().split(': ')
            existing_counts[keyword] = int(count)
        return existing_counts
    else:
        return Counter()

# Write the updated keywords to a text file
def write_keywords_to_file(filename, keyword_counts):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write("Keywords extracted from the job description:\n")
        for keyword, count in keyword_counts.items():
            file.write(f"{keyword}: {count}\n")

def main():
    # File paths
    common_words_path = 'static/top_1000_english_words.txt'  # Path to the file with common English words
    job_description_path = input("Enter the path to the job description text file: ")
    output_file = 'keywords_extracted.txt'
    
    # Load common words
    common_words = load_common_words(common_words_path)
    
    # Read job description
    with open(job_description_path, 'r', encoding='utf-8') as file:
        job_description = file.read()
    
    # Extract keywords
    new_keyword_counts = extract_keywords(job_description, common_words)
    
    # Load existing keywords
    existing_keyword_counts = load_existing_keywords(output_file)
    
    # Update keyword counts with new keywords
    existing_keyword_counts.update(new_keyword_counts)
    
    # Write updated keywords to file
    write_keywords_to_file(output_file, existing_keyword_counts)
    
    print(f"Keywords have been updated and saved to {output_file}.")

if __name__ == "__main__":
    main()
