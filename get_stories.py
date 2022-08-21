"""
This script loops through the tags in scraped_tags, and, until
every page is finished (indicated by finished_page value), scrapes
its pages. It gets the story URL, then makes an API call to the
REST API, populating the rest of the necessary story information.
Then it adds the story to the stories table.

You can run this arbitrarily, and it will update the stories table
with whatever new tags have been added to the scraped_tags table,
as long as the tag has the correct max_page/finished_page values.
"""

import sqlite3
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from Story import Story

import logging

Path("logging").mkdir(exist_ok = True)
logging.basicConfig(filename = f'logging/{time.time()}.log', encoding = 'utf-8', level = logging.INFO)


def getTagPage(base_url: str, page_num: int, cursor, connection):
    start_time = time.time()

    url = f"{base_url}?page={page_num}&sort_by=views"

    headers = {
        'User-agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582'
    }
    response = None
    while True:
        try:
            response = requests.get(url = url, headers = headers, timeout = 10)
            break
        except Exception as e:
            logging.error("Exception when getting page: " + str(e))
            continue

    soup = BeautifulSoup(response.text, 'html.parser')
    found = soup.find_all("a", attrs = {"class": "ai_ii"})

    for story_element in found:
        href = story_element.get("href")
        matching = cursor.execute('SELECT * FROM stories WHERE url = ?', (href,)).fetchall()
        if len(matching) > 0:
            continue

        story = Story(href)
        if story.fillFromAPI():
            to_insert = (story.title, story.description, story.getTagJSON(), story.author, story.word_count, story.url, story.dashed_title, story.api_endpoint)
            cursor.execute('INSERT OR IGNORE INTO stories(title, description, tags, author, word_count, url, dashed_title, api_endpoint) VALUES(?,?,?,?,?,?,?,?);', to_insert)
            connection.commit()

    taken = time.time() - start_time
    if len(found) == 0:
        to_log = f"Page {page_num} took {taken} seconds (0 sec/story)"
    else:
        to_log = f"Page {page_num} took {taken} seconds ({taken / len(found)} sec/story)"
    logging.info(to_log)
    print(to_log)
    return


if __name__ == "__main__":
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS stories(title text PRIMARY KEY, description text, tags text, author text, word_count int, url text, dashed_title text, api_endpoint text);')
    connection.commit()

    tags = cursor.execute('SELECT * FROM scraped_tags;').fetchall()
    for tag_row in tags:
        tag = tag_row[0]
        base_url = tag_row[1]
        max_page = tag_row[2]
        finished_page = tag_row[3]

        if finished_page is not None:
            if finished_page == max_page:
                continue
            start_page = finished_page + 1
        else:
            start_page = 1

        for page_num in range(start_page, max_page + 1):
            import time

            t = time.time()
            ft = time.strftime("%b %d %Y %H:%M:%S", time.localtime(t))
            to_log = f"{ft}: On page {page_num} of tag \"{tag}\""
            logging.info(to_log)
            print(to_log)
            getTagPage(base_url, page_num, cursor, connection)
            cursor.execute(f'UPDATE scraped_tags SET finished_page = ? WHERE tag = ?;', (page_num, tag))
