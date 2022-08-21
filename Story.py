"""
This represents a single story. It is constructed
from the story's URL, which is then used to make
an API call to populate the rest of the necessary
information.
"""

import json
import sqlite3

from requests import JSONDecodeError

import logging
import re

import requests

from misc import endpoint, pattern


class Story:

    def __init__(self, url: str):
        self.title: str  # ["submission"]["title"]
        self.description: str  # ["submission"]["description"]

        self.dashed_title: str
        self.url: str
        self.api_endpoint: str

        self.tags: list = []  # ["submission"]["tags"]
        self.word_count: int  # ["submission"]["words_count"]
        self.author: str  # ["submission"]["authorname"]

        self.url = url
        matched = re.match(pattern = pattern, string = url)
        self.dashed_title = matched.group(1)
        self.api_endpoint = f"{endpoint}{self.dashed_title}"

    def fillFromAPI(self):
        headers = {
            'User-agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582'
        }

        while True:
            try:
                response = requests.get(url = self.api_endpoint, headers = headers, timeout = 10)
                json_response = response.json()
                break
            except JSONDecodeError as e:
                logging.error("JSON exception while retrieving from API: " + str(e))
                continue
            except Exception as e:
                logging.error("Other exception while retrieving from API: " + str(e))
                continue

        if "submission" not in json_response:
            connection = sqlite3.connect('database.db')
            cursor = connection.cursor()
            cursor.execute('INSERT OR IGNORE INTO errored(url) VALUES(?);', (self.url,))
            connection.commit()
            return False

        self.title = json_response["submission"]["title"]
        self.description = json_response["submission"]["description"]
        tags = json_response["submission"]["tags"]
        for tag in tags:
            self.tags.append(tag["tag"])
        self.word_count = json_response["submission"]["words_count"]
        self.author = json_response["submission"]["authorname"]
        return True

    def toDict(self):
        story_dict = {}
        story_dict["title"] = self.title
        story_dict["description"] = self.description
        story_dict["author"] = self.author
        story_dict["url"] = self.url
        story_dict["tags"] = self.tags
        story_dict["word_count"] = self.word_count
        story_dict["dashed_title"] = self.dashed_title
        story_dict["api_endpoint"] = self.api_endpoint

        return story_dict

    def getTagJSON(self):
        return json.dumps(self.tags)
