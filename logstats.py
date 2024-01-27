import json

from pathlib import Path


def main():
    logsDir = Path("logs")

    dict = {}
    for logFile in logsDir.iterdir():
        if logFile.suffix == ".json":
            with open(logFile, "r") as file:
                log = json.load(file)
                dict[logFile.stem] = len(log)
                print(f"{logFile.stem}: {len(log)}")
    
    print(f"total combinations in filename_url.json: {dict['filename_url'] * dict['filename_url'] // 2}")





if __name__ == "__main__":
    main()