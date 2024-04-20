import json
from pathlib import Path
import hashlib
from pprint import pprint

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
        
        name_url = {}
        for filename in filenames:
            with open(logs_dir / "random_hashes.json", 'r') as f:
                random_hashes = json.load(f)
                for entry in random_hashes:
                    if entry['hash'] == name_hashes[filename]:
                        name_url[filename] = entry['url']
                        break
                    name_url[filename] = "url not found"
        
        has_bad_url = False

        # bad websites filtering
        has_30X = False
        has_cloudflare_error = False
        has_wix_error = False
        has_blogspot_moved_error = False
        names_30X = []
        names_cloudflare_error = []
        names_wix_error = []
        names_blogspot_moved_error = []
        for filename in filenames:
            url_without_port = ""
            if name_url[filename] != "url not found":
                if name_url[filename].split(":")[0] == "http" or name_url[filename].split(":")[0] == "https":
                    try:
                        url_without_port = name_url[filename].split(":")[1][2:]
                    except IndexError:
                        url_without_port = name_url[filename]
                else:
                    url_without_port = name_url[filename]
            
            """ if filename == "1117":
                print(url_without_port)
                print(name_content[filename].split('\n')[8])
                print(f"<title>{url_without_port} | 521: Web server is down</title>") """
            # check if the third line is <title>301 Moved Permanently</title>
            
            try:
                if name_content[filename].split('\n')[2].lower() == "<title>301 Moved Permanently</title>".lower():
                    names_30X.append(filename)
                    has_30X = True
                # also check 302
                elif name_content[filename].split('\n')[2].lower() == "<title>302 Found</title>".lower():
                    names_30X.append(filename)
                    has_30X = True
                
                # check for cloudflare error by checking if the 9th line is <title>[url without port] | 521: Web server is down</title>
                elif name_content[filename].split('\n')[8].lower() == f"<title>{url_without_port} | 521: Web server is down</title>".lower() or \
                     name_content[filename].split('\n')[8].lower() == f"<title>{url_without_port} | 522: Connection timed out</title>".lower():
                    names_cloudflare_error.append(filename)
                    has_cloudflare_error = True
                
                # check for wix error by checking if the 6th line is <html ng-app="wixErrorPagesApp">
                elif name_content[filename].split('\n')[5].lower() == "<html ng-app=\"wixErrorPagesApp\">".lower():
                    names_wix_error.append(filename)
                    has_wix_error = True
                
                # check for blogspot moved by checking if the 3rd line is <TITLE>Moved Temporarily</TITLE> or <title>Moved Permanently</title>
                elif name_content[filename].split('\n')[2].lower() == "<title>Moved Temporarily</title>".lower() or \
                     name_content[filename].split('\n')[2].lower() == "<title>Moved Permanently</title>".lower():
                    names_blogspot_moved_error.append(filename)
                    has_blogspot_moved_error = True
            except IndexError:
                print(f"IndexError: {filename}, probably a very short file")
                short_files.add(filename)


        
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
            if name_url[filename] == "url not found":
                has_bad_url = True
            if filename in names_30X:
                result_d[filename]["30X"] = "!!!!! 30X STATUS CODE !!!!!"
            elif filename in names_cloudflare_error:
                result_d[filename]["cloudflare_error"] = "!!!!! CLOUDFLARE ERROR !!!!!"
            elif filename in names_wix_error:
                result_d[filename]["wix_error"] = "!!!!! WIX ERROR !!!!!"
            elif filename in names_blogspot_moved_error:
                result_d[filename]["blogspot_moved_error"] = "!!!!! BLOGSPOT MOVED ERROR !!!!!"
            else:
                pass
        
        if hash_collision_percent > 0:
            result_d["hash_collision_percent"] = hash_collision_percent
        
        final_r.append(result_d)

        if hash_collision_percent == 0 and not has_30X and not has_bad_url and not has_cloudflare_error \
            and not has_wix_error and not has_blogspot_moved_error:
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