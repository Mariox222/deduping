from myminhash import MinHash, LSH
import os
from pprint import pprint
from pathlib import Path
import time
import json

# parameters
lshLogPath = Path("logs") / "lshLogs.txt"
# lshLogPath = None
realJaccardLogPath = Path("logs") / "realJaccardLogs.txt"
# realJaccardLogPath = None
adjacencyListLogPath = Path("logs") / "adjacencyListLogs.json"
# adjacencyListLogPath = None
min_jaccard = 0.8


start_time = time.time()

# Iterate through the files and store their contents in the dictionary
folder_path = "documents2"
html_content_dict = {}
file_list = os.listdir(folder_path)
for file_name in file_list:
    if file_name.endswith(".html"):
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r') as file:
            html_content = file.read()
        # check if filename ends with .html
        if file_name.endswith(".html"):
            # remove .html from filename
            file_name = file_name[:-5]
        html_content_dict[file_name] = html_content

# Generate MinHash signatures.
minhash = MinHash(html_content_dict.values(), n_gram=9, permutations=100, hash_bits=64, seed=3)
lsh = LSH(no_of_bands=50)
lsh.update(minhash, html_content_dict.keys())
shingle_sets = list(minhash.get_shingles())

# log the real jaccard
if realJaccardLogPath:
    MinHash.logRealJaccard(shingle_sets, html_content_dict, logPath=realJaccardLogPath)


# log the adjacency list
if adjacencyListLogPath:
    with open(adjacencyListLogPath, "w") as file:
        adjacency_list = lsh.adjacency_list(min_jaccard=min_jaccard, logPath=lshLogPath)
        json.dump(adjacency_list, file, indent=4)



end_time = time.time()
print(f"Done in: {end_time - start_time} seconds")