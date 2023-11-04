from akin import MinHash, LSH

import os

from pprint import pprint

# Define the folder path where your HTML documents are located
folder_path = "documents"

# Initialize an empty dictionary to store the content
html_content_dict = {}

# List all files in the folder
file_list = os.listdir(folder_path)

# Iterate through the files and store their contents in the dictionary
for file_name in file_list:
    if file_name.endswith(".html"):
        file_path = os.path.join(folder_path, file_name)
        
        with open(file_path, 'r') as file:
            html_content = file.read()
        
        # Store the content in the dictionary with the file name as the key
        html_content_dict[file_name] = html_content

print(html_content_dict.keys())

# Generate MinHash signatures.
minhash = MinHash(html_content_dict.values(), n_gram=9, permutations=100, hash_bits=64, seed=3)

# Create LSH model.
lsh = LSH(no_of_bands=50)
lsh.update(minhash, html_content_dict.keys())

# Return adjacency list for all similar texts.
for min_jaccard in [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]:
    print(f"min_jaccard = {min_jaccard}")
    adjacency_list = lsh.adjacency_list(min_jaccard=min_jaccard)
    pprint(adjacency_list)
    print("")

"""
ISPIS:
min_jaccard = 0.5
{'article1_v1.html': ['article1_v2.html'],
 'article1_v2.html': ['article1_v1.html'],
 'article2_v1.html': []}

min_jaccard = 0.6
{'article1_v1.html': ['article1_v2.html'],
 'article1_v2.html': ['article1_v1.html'],
 'article2_v1.html': []}

min_jaccard = 0.7
{'article1_v1.html': ['article1_v2.html'],
 'article1_v2.html': ['article1_v1.html'],
 'article2_v1.html': []}

min_jaccard = 0.8
{'article1_v1.html': ['article1_v2.html'],
 'article1_v2.html': ['article1_v1.html'],
 'article2_v1.html': []}

min_jaccard = 0.9
{'article1_v1.html': [], 'article1_v2.html': [], 'article2_v1.html': []}

min_jaccard = 0.95
{'article1_v1.html': [], 'article1_v2.html': [], 'article2_v1.html': []}
"""