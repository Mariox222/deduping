import json
from pathlib import Path
import hashlib

def main():
    adjacency_list = None
    logs_dir = Path("logs")
    alPath = Path("./logs") / "resultAdjacencyList.json"

    with open(alPath, 'r') as f:
        adjacency_list = json.load(f)

    already_seen = set()
    final_r = []
    good_results = []
    short_files = set()
    for key, values in adjacency_list.items():
        if key in already_seen:
            continue
        else:
            already_seen.add(key)

        for v in values:
            if v in already_seen:
                continue
            else:
                already_seen.add(v)
        
        if len(values) == 0:
            continue
        
        has_301 = False
        has_bad_url = False

        filenames = []
        filenames.append(key)
        for v in values:
            filenames.append(v)

        name_content = {}
        docs_dir = Path("documents")
        for filename in filenames:
            with open(docs_dir / (filename + ".html"), 'r') as f:
                name_content[filename] = f.read()

        name_hashes = {}
        for filename in filenames:
            h = hashlib.sha256()
            h.update(name_content[filename].encode())
            name_hashes[filename] = h.hexdigest()
        
        # 301 status code check
        names_301 = []
        for filename in filenames:
            # check if the third line is <title>301 Moved Permanently</title>
            
            try:
                if name_content[filename].split('\n')[2] == "<title>301 Moved Permanently</title>":
                    names_301.append(filename)
                    has_301 = True
            except IndexError:
                print(f"IndexError: {filename}, probably a very short file")
                short_files.add(filename)


        name_url = {}
        for filename in filenames:
            with open(logs_dir / "random_hashes.json", 'r') as f:
                random_hashes = json.load(f)
                for entry in random_hashes:
                    if entry['hash'] == name_hashes[filename]:
                        name_url[filename] = entry['url']
                        break
                    name_url[filename] = "url not found"
        
        hash_collision_percent = 0
        unique_hashes = set(name_hashes.values())
        if len(unique_hashes) != len(name_hashes):
            hash_collision_percent = (len(name_hashes) - len(unique_hashes)) / len(name_hashes) * 100

        result_d = {}
        for filename in filenames:
            result_d[filename] = {
                "hash": name_hashes[filename],
                "url": name_url[filename],
            }
            if filename in names_301:
                result_d[filename]["301"] = "!!!!! 301 STATUS CODE !!!!!"
            else:
                pass
        
        if hash_collision_percent > 0:
            result_d["hash_collision_percent"] = hash_collision_percent
        
        final_r.append(result_d)

        if hash_collision_percent == 0 and not has_301 and not has_bad_url:
            good_results.append(result_d)
    
    with open(logs_dir / "interpretation_result.json", 'w') as f:
        json.dump(final_r, f, indent=4)
        print("interpretation result written")

    with open(logs_dir / "short_files.json", 'w') as f:
        json.dump(list(short_files), f, indent=4)
        print("short files written")
    
    with open(logs_dir / "good_interpretation_result.json", 'w') as f:
        json.dump(good_results, f, indent=4)
        print("good interpretation result written")
        


if __name__ == "__main__":
    main()