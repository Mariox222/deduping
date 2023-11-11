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

# print(html_content_dict.keys())

# Generate MinHash signatures.
minhash = MinHash(html_content_dict.values(), n_gram=9, permutations=100, hash_bits=64, seed=3)

lsh = LSH(no_of_bands=50)
lsh.update(minhash, html_content_dict.keys())

shingle_sets = list(minhash.get_shingles())

for i, list_i in enumerate(shingle_sets):
    set_i = set(list_i)
    for j, list_j in enumerate(shingle_sets[i:]):
        set_j = set(list_j)
        real_jaccard = len(set_i.intersection(set_j)) / len(set_i.union(set_j))
        labels = list(html_content_dict.keys())
        print(f"{labels[i]} vs {labels[i + j]}")
        print(f"real_jaccard = {real_jaccard}")
        print("")

my_range = list(range(int(0.5 * 100), int(1.05 * 100), int(0.05 * 100)))
my_range = [x / 100 for x in my_range]
for min_jaccard in my_range:
    print(f"min_jaccard for estimation = {min_jaccard}")
    adjacency_list = lsh.adjacency_list(min_jaccard=min_jaccard)
    pprint(adjacency_list)
    print("")

print("")
# print(shingle_sets[0][0:10])
# print(html_content_dict.keys())

        
