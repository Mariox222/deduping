from myminhash import MinHash, LSH
import os
from pprint import pprint
from pathlib import Path
import time
import json

def logRealJaccard(realJaccardLogPath, shingle_sets, html_content_dict):
    # log the real jaccard
    d = {}
    if realJaccardLogPath:
        d = MinHash.realJaccard(shingle_sets, html_content_dict)

        with open(realJaccardLogPath, "w") as file:
            json.dump(d, file, indent=4)
    
    return d

def get_html_content_dict(folder_path):
    # Iterate through the files and store their contents in the dictionary
    html_content_dict = {}
    file_list = os.listdir(folder_path)
    for file_name in file_list:
        if file_name.endswith(".html"):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r') as file:
                html_content = file.read()
            if file_name.endswith(".html"):
                file_name = file_name[:-5]
            html_content_dict[file_name] = html_content
    return html_content_dict

def generateSignatures(html_content_dict):
    # Generate MinHash signatures.
    minhash = MinHash(html_content_dict.values(), n_gram=9, permutations=100, hash_bits=64, seed=3)
    lsh = LSH(no_of_bands=50)
    lsh.update(minhash, html_content_dict.keys())
    shingle_sets = list(minhash.get_shingles())

    return shingle_sets, minhash, lsh

def logAdjacencyList(adjacencyListLogPath, lsh, lshLogPath, min_jaccard=0.8):
    # save the adjacency list in json

    if adjacencyListLogPath:
        adjacency_list, estimates = lsh.adjacency_list(min_jaccard=min_jaccard, logPath=lshLogPath)
        with open(adjacencyListLogPath, "w") as file:
            json.dump(adjacency_list, file, indent=4)
        with open(lshLogPath, "w") as file:
            json.dump(estimates, file, indent=4)

def realVsEstimateCompare(comparisonLogPath, realJaccardLogPath=None, lshLogPath=None):
    if realJaccardLogPath and lshLogPath:
        realJaccard = None
        lshLog = None
        r = []
        with open(realJaccardLogPath, "r") as file:
            realJaccard = json.load(file)
        with open(lshLogPath, "r") as file:
            lshLog = json.load(file)
        for lshLogEntry in lshLog:
            label1 = lshLogEntry["label1"]
            label2 = lshLogEntry["label2"]
            estimate = lshLogEntry["estimate"]
            real = None
            for realJaccardEntry in realJaccard:
                if realJaccardEntry["name1"] == label1 and realJaccardEntry["name2"] == label2:
                    real = realJaccardEntry["real_jaccard"]
                    break
                if realJaccardEntry["name1"] == label2 and realJaccardEntry["name2"] == label1:
                    real = realJaccardEntry["real_jaccard"]
                    break
            if real:
                r.append({
                    "label1": label1,
                    "label2": label2,
                    "real": real,
                    "estimate": estimate,
                    "difference": abs(real - estimate),
                })
        
        with open(comparisonLogPath, "w") as file:
            json.dump(r, file, indent=4)
        
        print(f"Average difference: {sum([x['difference'] for x in r]) / len(r)} in {len(r)} comparisons")

        return


def main():
    print("Log real Jaccard? (y/n) default yes")
    logRealJaccardInput = input()
    if logRealJaccardInput.lower() == "y" or logRealJaccardInput == "":
        logRealJaccardInput = True
    else:
        logRealJaccardInput = False

    lshLogPath = Path("logs") / "lshLogs.json"
    # lshLogPath = None
    realJaccardLogPath = Path("logs") / "realJaccardLogs.json"
    # realJaccardLogPath = None
    adjacencyListLogPath = Path("logs") / "resultAdjacencyList.json"
    # adjacencyListLogPath = None
    comparisonLogPath = Path("logs") / "comparison.json"
    # comparisonLogPath = None
    folder_path = "documents"
    min_jaccard = 0.8

    print("Start")
    start_time = time.time()
    
    # Get the html content of the documents
    html_content_dict = get_html_content_dict(folder_path)
    print("[{:.2f}s] got html content".format(time.time() - start_time))

    # Generate MinHash signatures.
    shingle_sets, minhash, lsh = generateSignatures(html_content_dict)
    print("[{:.2f}s] generated signatures".format(time.time() - start_time))

    if logRealJaccardInput:
        # log real jaccard
        logRealJaccard(realJaccardLogPath, shingle_sets, html_content_dict)
        print("[{:.2f}s] logged real jaccard".format(time.time() - start_time))

    # save the adjacency list in json
    logAdjacencyList(adjacencyListLogPath, lsh, lshLogPath, min_jaccard)
    print("[{:.2f}s] logged adjacency list".format(time.time() - start_time))

    if logRealJaccardInput:
        # compare real jaccard and estimate jaccard
        realVsEstimateCompare(comparisonLogPath, realJaccardLogPath, lshLogPath)
        print("[{:.2f}s] compared real jaccard and estimate jaccard".format(time.time() - start_time))

    end_time = time.time()
    print(f"Done in: {end_time - start_time} seconds")

if __name__ == "__main__":
    main()