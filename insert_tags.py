"""
This script transfers tags from tag_dict.json
to the scraped_tags table.
"""

import json
import sqlite3
from pathlib import Path

connection = sqlite3.connect('database.db')
cursor = connection.cursor()
cursor.execute('CREATE TABLE scraped_tags(tag text PRIMARY KEY, url text, max_page integer, finished_page integer);')
connection.commit()

path_file = Path("tag_dict.json")
tag_dict = json.loads(path_file.read_text(encoding = "utf8"))
for tag in tag_dict:
    to_insert = (tag, tag_dict[tag]["url"], tag_dict[tag]["max_page"], 0)
    cursor.execute('INSERT INTO scraped_tags(tag,url,max_page,finished_page) VALUES(?,?,?,?,?)', to_insert)

connection.commit()
