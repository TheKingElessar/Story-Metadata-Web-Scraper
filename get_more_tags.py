"""
This script loops through all unique tags from unique_tags.json,
scraping their page and inserting them into the scraped_tags table,
saving the max page number.
"""

import json
import sqlite3
import time
from pathlib import Path
from urllib.parse import quote

import requests as requests
from bs4 import BeautifulSoup

import logging
from misc import get_base_page, tag_stem

Path("logging").mkdir(exist_ok = True)
logging.basicConfig(filename = f'logging/{time.time()}.log', encoding = 'utf-8', level = logging.INFO)

headers = {
    'User-agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582'
}

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

unique_tags = json.loads(Path("unique_tags.json").read_text(encoding = "utf8"))
last_finished_tag = cursor.execute('SELECT * FROM scraped_tags ORDER BY ROWID DESC LIMIT 1;').fetchone()[0]
first_skip = True
for tag in unique_tags:
    if first_skip:
        if tag != last_finished_tag:
            continue
        else:
            first_skip = False
            continue

    matching = cursor.execute('SELECT tag FROM scraped_tags WHERE tag = ?', (tag,)).fetchall()
    if len(matching) > 0:
        logging.info(f"Skipping {tag}")
        print(f"Skipping {tag}")
        continue

    page_number = 1
    tag_href = quote(tag, safe = '')
    tag_href = f"/{tag_href}/"
    base_page = get_base_page(tag_href, page_number)
    while True:
        try:
            html_doc = requests.get(url = base_page, headers = headers)
            break
        except:
            logging.error(f"Error getting page {base_page}")
            continue

    tag_pages = BeautifulSoup(html_doc.text, 'html.parser')

    pages = tag_pages.find_all("a", attrs = {"class": "l_bJ"})
    max_page = 1
    for page in pages:
        if len(page["class"]) > 1:
            continue
        if int(page.get_text()) > max_page:
            max_page = int(page.get_text())

    tag_href = f"{tag_stem}{tag_href}"
    to_insert = (tag, tag_href, max_page, 0)
    cursor.execute('INSERT INTO scraped_tags(tag,url,max_page,finished_page) VALUES(?,?,?,?)', to_insert)
    connection.commit()
    logging.info(f"Added {tag_href}")
    print(f"Added {tag_href}")
