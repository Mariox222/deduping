from pathlib import Path

def main():
    print("Clearing logs...")

    # iterate logs folder
    logs = Path("logs")
    for log in logs.iterdir():
        log.unlink()
    
    print("Logs cleared.")

if __name__ == "__main__":
    main()