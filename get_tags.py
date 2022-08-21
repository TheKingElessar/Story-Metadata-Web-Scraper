"""
This script scrapes the tags page, then, for each tag
from there, scrapes that tag's page to get the max page
number. The results are written to tag_dict.json.
"""

import json
import random
import time
from pathlib import Path

import requests as requests
from bs4 import BeautifulSoup

from misc import tag_stem

base_page = tag_stem

headers = {
    'User-agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582'
}

first_tags_dict = {}  # Of the form tag name: tag url
html_doc = requests.get(url = base_page, headers = headers)
soup = BeautifulSoup(html_doc.text, 'html.parser')
first_tags = soup.find_all("a", attrs = {"property": "itemListElement"})
for tag_element in first_tags:
    url = tag_element.get("href")
    first_tags_dict[tag_element.get_text()] = url

random.seed()
print(f"Found {len(first_tags_dict)} tags")
for tag in first_tags_dict:
    tag_href = first_tags_dict[tag]
    page_number = 1
    base_page = f"{tag_stem}{tag_href}?page={page_number}&sort_by=views"
    html_doc = requests.get(url = base_page, headers = headers)
    tag_pages = BeautifulSoup(html_doc.text, 'html.parser')

    pages = tag_pages.find_all("a", attrs = {"class": "l_bJ"})
    max = 0
    for page in pages:
        if len(page["class"]) > 1:
            continue
        if int(page.get_text()) > max:
            max = int(page.get_text())

    first_tags_dict[tag] = {}
    first_tags_dict[tag]["url"] = f"{tag_stem}{tag_href}"
    first_tags_dict[tag]["max_page"] = max
    print(f"Finished {tag}")
    time.sleep(random.randint(1, 20) / 10)

output_dict_file = Path("tag_dict.json")
output_dict_file.write_text(json.dumps(first_tags_dict, indent = 4), encoding = 'utf8')
