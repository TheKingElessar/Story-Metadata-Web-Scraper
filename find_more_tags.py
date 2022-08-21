"""
This script loops through every story in the stories table, converts every
numerical tag to a string tag (in json representation), and then outputs a
list of unique tags to unique_tags.json.
"""

import json
import sqlite3
from pathlib import Path


def main():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    tags = set()
    stories = cursor.execute('SELECT tags, url FROM stories;').fetchall()
    update_count = 0
    for story in stories:
        tags_json = json.loads(story[0])
        url = story[1]

        to_update = False
        for i in range(len(tags_json)):
            tag = tags_json[i]
            if type(tag) != str:
                to_update = True
                tags_json[i] = str(tag)
                # print(f"Tag is not string. URL: {url}")
            tags.add(str(tag))

        if to_update:
            tags_str = json.dumps(tags_json)
            cursor.execute('UPDATE stories SET tags = ? WHERE url = ?;', (tags_str, url))
            update_count += 1

    connection.commit()
    print(f"Updated entries: {update_count}")
    print(f"Length of tags set: {len(tags)}")
    output_file = Path("unique_tags.json")
    output_file.write_text(json.dumps(list(tags), indent = 4), encoding = "utf8")


if __name__ == "__main__":
    main()
