from dotenv import load_dotenv
import pymongo
import os
import time
import json
from pathlib import Path
from pprint import pprint


class DBclient:
    def __init__(self, conn_str):
        self.conn_str = conn_str
        self.connect()
        self.url_count = 3200000 # hardkodirano jer dinamičko određivanje predugo traje
        self.bad_hashes = [
            "dc1d54dab6ec8c00f70137927504e4f222c8395f10760b6beecfcfa94e08249f",
            "9e17cb15dd75bbbd5dbb984eda674863c3b10ab72613cf8a39a00c3e11a8492a",
            "368daab67b1a5b2b2802edbbac79a2aa4ba992a2ebf9c67b98ad784d8004018c",
            "622bde5d9ebba9fe02bfce13c32e5b2f60e281996f61d8d68bee9de28e156555",
            "7341eb3081bb2056eac9c793f7d0e58ff496d39a9210b7d753ae6621663a7608",
            "44fe477964cfcaf5a9d2d48ec699c0d1beb862a77a113fe85f0479822e0ee04e",
            "80c3fe2ae1062abf56456f52518bd670f9ec3917b7f85e152b347ac6b6faf880"
        ]
        self.bad_url_endings = [
            ".json",
            ".xml",
            ".js",
            ".css",
            "wp-json/",
            "1.0/embed"
        ]
        self.to_sleep = 1
    
    def connect(self):
        self.client = pymongo.MongoClient(self.conn_str)
        self.db = self.client.websecradar
        print("connected")

    def getRandomHashes(self, number_of_hashes=100, filename='random_hashes.json'):
        print("getting random hashes")
        url_col = self.db.crawled_data_urls_v0

        url_hash = []
        added_urls = []
        while len(url_hash) < number_of_hashes:
            print(f"got {len(url_hash)} hashes, sleeping")
            time.sleep(self.to_sleep)

            for document in url_col.aggregate([{"$sample": {"size": 50}}]):
                continue_flag = False
                url = document['url']
                for ending in self.bad_url_endings:
                    if url.endswith(ending):
                        continue_flag = True
                        break
                if url in added_urls:
                    continue_flag = True
                    
                if continue_flag:
                    continue
                added_urls.append(url)

                last_hash = ""
                for check in reversed(document['checks']):
                    if check['timestamp'] == document['last_check']:
                        last_hash = check['hash']
                        break
                
                if (last_hash == ""):
                    continue
                elif last_hash in self.bad_hashes:
                    continue
                else:
                    url_hash.append({'url': url, 'hash': last_hash})

        print("Got {} hashes".format(len(url_hash)))
        print ("writing url-hash pairs to '{}'".format(filename))

        with open(filename, 'w') as f:
            json.dump(url_hash, f)
            print(" --- writing complete")
        
        return url_hash
 
    def getRandomDocs(self, hash_filename, write_to_dir, result_log_filename, start_doc_name=0):
        print("getting random docs")

        doc_col = self.db.crawled_data_pages_v0

        # check if directory exists
        if not os.path.isdir(write_to_dir):
            raise FilenotFoundError("Directory '{}' doesn't exist".format(write_to_dir))
        
        # check if hash_filename exists
        if not os.path.isfile(hash_filename):
            raise FilenotFoundError("File '{}' doesn't exist".format(hash_filename))
        
        
        filename_url = []
        with open(hash_filename, "r") as f:
            data_str = f.read()
            data = json.loads(data_str)

            count = start_doc_name - 1
            for hash_url in data:
                count += 1
                print("sleeping")
                time.sleep(self.to_sleep)
                doc_doc = doc_col.find_one({"hash": hash_url['hash']})
                if not doc_doc:
                    print("couldn't get document")
                    continue
                doc = doc_doc['page']

                if len(doc) < 15:
                    print("document too short")
                    continue

                filename_without_dir = (str(count) + ".html")
                doc_path = Path(write_to_dir) / filename_without_dir
                with doc_path.open(mode="w", encoding="utf-8") as f:
                    f.write(doc)
                    filename_url.append({
                        "filename": filename_without_dir,
                        "url": hash_url['url']
                    })
                    print(f"document written {doc_path}")
        
        existing_result_log = []
        try:
            with open(result_log_filename, "r") as f:
                existing_result_log = json.load(f)
        except FileNotFoundError:
            print("result log not found, creating new one")

        for entry in filename_url:
            if entry not in existing_result_log:
                existing_result_log.append(entry)
        
        with open(result_log_filename, "w") as f:
            json.dump(existing_result_log, f)
            print("result log written")
        
def getNrandomHashes(N=100):
    config = load_dotenv('.env')
    conn_string = os.getenv('DB_CONNECTION_STRING')
    
    client = DBclient(conn_string)

    num_of_hashes = N
    filename = Path("logs") / "random_hashes.json"
    client.getRandomHashes(num_of_hashes, filename)

def getRandomDocs(hash_filename, write_to_dir, result_log_filename, start_doc_name=0):
    config = load_dotenv('.env')
    conn_string = os.getenv('DB_CONNECTION_STRING')

    client = DBclient(conn_string)

    client.getRandomDocs(hash_filename, write_to_dir, result_log_filename, start_doc_name=start_doc_name)

def main():
    # measure time
    start_time = time.time()

    default_documents_dir = Path("documents")
    default_hash_filename = Path("logs") / "random_hashes.json"
    default_getdoc_result_log_filename = Path("logs") / "filename_url.json"

    print(f"defualt documents dir: {default_documents_dir}")
    print(f"default hash filename: {default_hash_filename}")
    print(f"default getdoc result log filename: {default_getdoc_result_log_filename}")

    print("[{:.2f}] Get hashes? (y/n)".format(time.time() - start_time))
    get_hashes = input()
    if get_hashes.lower() == 'y':
        print("How many hashes? > ")
        N = int(input())
        
        getNrandomHashes(N=N)
    
    print("[{:.2f}] Get docs? (y/n)".format(time.time() - start_time))
    get_docs = input()
    if get_docs.lower() == 'y':
        print("start document name? (blank for 0) > ")
        start = input()
        if start == '':
            start = 0
        else:
            start = int(start)
        getRandomDocs(default_hash_filename, default_documents_dir, 
        default_getdoc_result_log_filename, start_doc_name=start)
    else:
        print("Exiting")
    
    print("Time elapsed: {:.2f} seconds".format(time.time() - start_time))

if __name__ == "__main__":
    main()

