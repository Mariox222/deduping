import json
from pathlib import Path
import hashlib
from pprint import pprint
import webbrowser

def main():
    
    doc_dir = Path("documents")
    log_dir = Path("logs")
    gir = None
    lines_to_print = 10
    with open(log_dir / "good_interpretation_result.json", "r") as f:
        gir = json.load(f)
        
        for batch in gir:
            input("Press anything to open the next batch in browser")
            for filename, content in batch.items():
                url = content["url"]
                print(f"opening {filename} with url {url}")
                webbrowser.open(doc_dir / (filename + ".html"))

            flag = input(f"print first {lines_to_print} lines of each document? (y/n) (default: n) ")
            if flag == "y":
                for filename, content in batch.items():
                    print(f"filename: {filename}")
                    with open(doc_dir / (filename + ".html"), "r") as f2:
                        for i in range(lines_to_print):
                            try:
                                print("\\\\  ", end="")
                                print(f2.readline(), end="")
                            except:
                                break
                    print("\n\n")

            comment = input("Input your batch comment: ")
            batch["comment"] = comment

    with open(log_dir / "good_interpretation_result.json", "w") as f:
        json.dump(gir, f)
        print("updated good_interpretation_result.json")



            
    

if __name__ == "__main__":
    main()



