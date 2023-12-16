from pathlib import Path

def main():
    print("Clearing docs...")

    docs = Path("documents3")
    for doc in docs.iterdir():
        # remove only directories
        if doc.is_dir():
            for file in doc.iterdir():
                file.unlink()
            doc.rmdir()

    
    print("docs cleared.")

if __name__ == "__main__":
    main()