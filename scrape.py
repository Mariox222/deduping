import requests
from pathlib import Path

import json
# List of URLs to scrape
urls = [
    "https://www.index.hr/vijesti/clanak/za-novu-godinu-cak-44-grada-i-opcine-bez-vatrometa/2519428.aspx?index_ref=naslovnica_vijesti_prva_d",
    "https://www.index.hr/vijesti/clanak/kod-paskog-mosta-prevrnula-se-brodica-s-4-prijatelja-3-spasena-za-jednim-se-traga/2519441.aspx?index_ref=naslovnica_vijesti_ostalo_d",
    "https://www.index.hr/vijesti/clanak/diljem-hrvatske-pada-snijeg-i-u-zagrebu/2519435.aspx?index_ref=naslovnica_vijesti_ostalo_d",
    "https://www.index.hr/vijesti/clanak/ako-se-nastavi-zagrijavanje-mediteran-ce-biti-jedna-od-pogodjenijih-regija-na-svijetu/2519254.aspx?index_ref=naslovnica_vijesti_ostalo_d",
    "https://www.index.hr/vijesti/clanak/mnoge-curice-nemaju-za-uloske-pa-izostaju-s-nastave-ili-koriste-krpe-i-gaze/2519426.aspx?index_ref=naslovnica_vijesti_ostalo_d"

]

fileNameUrl = {}

logFileNameUrl = Path("logs") / "fileNameUrl.json"
# logFileNameUrl = None

# Function to scrape HTML content
def scrape_html(url, html_dir, version=None):
    global fileNameUrl

    filename = f"{url.split('//')[-1]}.html"
    # remove url parameters if present
    if "?" in filename:
        filename = filename.split("?")[0]
    if version:
        filename = f"{filename}_{version}.html"

    # replace windows filename ilegal characters with _
    if "\\" in filename:
        filename = filename.replace("\\", "_")
    if ":" in filename:
        filename = filename.replace(":", "_")
    if "*" in filename:
        filename = filename.replace("*", "_")
    if "?" in filename:
        filename = filename.replace("?", "_")
    if "\"" in filename:
        filename = filename.replace("\"", "_")
    if "<" in filename:
        filename = filename.replace("<", "_")
    if ">" in filename:
        filename = filename.replace(">", "_")
    if "|" in filename:
        filename = filename.replace("|", "_")

    # replace / with -
    if "/" in filename:
        filename = filename.replace("/", "-")
    
    print(f"Scraping {url}...")
    
    # Fetch HTML content using requests
    response = requests.get(url)
    
    # Save HTML content to a file
    with open(html_dir/filename, "w", encoding="utf-8") as file:
        file.write(response.text)
    
    print(f"HTML content saved to {html_dir/filename}")

    fileNameUrl[filename] = url


html_dir = Path("documents2")
html_dir.mkdir(exist_ok=True)

for url in urls:
    scrape_html(url, html_dir, version="v1")
    scrape_html(url, html_dir, version="v2")
    scrape_html(url, html_dir, version="v3")


if logFileNameUrl:
    with open(logFileNameUrl, "w") as file:
        json.dump(fileNameUrl, file, indent=4)