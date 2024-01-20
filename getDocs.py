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
    
    def connect(self):
        self.client = pymongo.MongoClient(self.conn_str)
        self.db = self.client.websecradar
        print("connected")
    
    def getHashPairs(self, hash_pairs_n=10, sleepInterval=5, batch_size=10,
     filename='hash_pairs.json', docs_from=0, docs_to=None):
        print("getting pairs")
        url_col = self.db.crawled_data_urls_v0

        hash_pairs = []
        skipped = 0
        total_document_count = 0
        req_count = batch_size

        count = 1956352 # hardkodirano jer dinamičko određivanje predugo traje
        print("document count is: {}".format(count))

        assert (count >= docs_from)
        if docs_to:
            assert (count >= docs_to)
        else:
            docs_to = count
        
        for document in url_col.find(batch_size=batch_size)[docs_from:docs_to]:
            
            total_document_count += 1

            to_append = dict()

            last_hash = ""
            second_last_hash = ""
            for check in reversed(document['checks']):
                if check['timestamp'] == document['last_check']:
                    last_hash = check['hash']
                if check['hash'] != last_hash and last_hash != "" and check['hash'] != None:
                    second_last_hash = check['hash']
                    break
            
            if (second_last_hash == ""):
                skipped += 1
            else:
                if last_hash == None:
                    print("one site's last check doesn't have a hash")
                else:
                    to_append['second_last_hash'] = second_last_hash
                    to_append['last_hash'] = last_hash
                    to_append['url'] = document['url']
                    # skip hashes that are equal to dc1d54dab6ec8c00f70137927504e4f222c8395f10760b6beecfcfa94e08249f
                    bad_hashes = [
                        "dc1d54dab6ec8c00f70137927504e4f222c8395f10760b6beecfcfa94e08249f",
                        "9e17cb15dd75bbbd5dbb984eda674863c3b10ab72613cf8a39a00c3e11a8492a"
                    ]
                    if second_last_hash not in bad_hashes and last_hash not in bad_hashes:
                        hash_pairs.append(to_append)
                    else:
                        skipped += 1

            req_count = req_count - 1

            if req_count <= 0:
                req_count = batch_size
                if hash_pairs_n:
                    if len(hash_pairs) >= hash_pairs_n:
                        break
                    
                print (" --- skipped {} documents".format(skipped))
                print ("hash_pairs: {}".format(len(hash_pairs)))
                print ("total documents viewed: " + str(total_document_count))
                print("sleep {} seconds\n".format(sleepInterval))
                time.sleep(sleepInterval)

                skipped = 0
                continue
        
        print("Got {} hash pairs".format(len(hash_pairs)))
        print ("writing hash pairs to '{}'".format(filename))
        pprint (hash_pairs)

        old_pairs = list()
        if os.path.isfile(filename):
            with open(filename, 'r')as f:
                old_pairs = json.loads(f.read())
                
        for pair in old_pairs:
            if pair not in hash_pairs:
                hash_pairs.append(pair)

        written = 0
        with open(filename, 'w') as f:
            json.dump(hash_pairs, f)
            print(" --- writing complete")
            written = 1
        
        if not written:
            print("write failed")

    def getDocs(self, directory_name, hash_filename):
        print("getting docs")
        doc_col = self.db.crawled_data_pages_v0

        extra_backSlash = "/" if directory_name[-1] != "/" else ""
        directory = Path("./" + directory_name + extra_backSlash)

        if not directory.exists():
            raise "directory doesn't exist"
        

        count = 0
        stats = dict()
        with open(hash_filename, "r") as h:
            data_str = h.read()
            data = json.loads(data_str)
            for pair in data:
                print (" --- " + str(count) + " / " + str(len(data)))
                
                print("sleeping 1 sec")
                time.sleep(1)

                old_doc_doc = doc_col.find_one({"hash": pair['second_last_hash']})
                new_doc_doc = doc_col.find_one({"hash": pair['last_hash']})
                
                if not old_doc_doc or not new_doc_doc:
                    print("couldn't get documents")
                    count += 1
                    continue
                
                old_doc = old_doc_doc['page']
                new_doc = new_doc_doc['page']

                

                old_doc_path = Path("documents3") / (str(count) + "_old.html")
                with old_doc_path.open(mode="w", encoding="utf-8") as f:
                    f.write(old_doc)
                    print("old document written")
                
                new_doc_path = Path("documents3") / (str(count) + "_new.html")
                with new_doc_path.open(mode="w", encoding="utf-8") as f:
                    f.write(new_doc)
                    print("new document written")

                pair['name_of_download'] = str(count)
                stats[str(count)] = pair

                count += 1
            
        stats_path = Path("logs") / "docName_url.json"
        with stats_path.open(mode="w", encoding="utf-8") as f:
            json.dump(stats, f)
            print("stats written")
    
        


def main():

    config = load_dotenv('.env')
    conn_string = os.getenv('DB_CONNECTION_STRING')

    client = DBclient(conn_string)

    batch_size = 10
    sleepInterval = 3
    num_of_hash_pairs_to_get = None # ako je None, broj dokumenata je jednak docs_to - docs_from
    docs_from = 0 # od koje pozicije pocinje dohvacati linkove
    docs_to = 200 # do koje pozicije pocinje dohvacati, ako je None, trazi se do kraja kolekcije

    hash_filename = Path("logs") / "hash_pairs.json"
    directory_name = "documents3"

    client.getHashPairs(hash_pairs_n=num_of_hash_pairs_to_get, sleepInterval=sleepInterval, batch_size=batch_size,
        filename=hash_filename, docs_from=docs_from, docs_to=docs_to)
    client.getDocs(directory_name, hash_filename)



if __name__ == "__main__":
    main()

