import os
import re
from collections.abc import Iterable

import requests

# `?:`: Non-capturing group
URL = r"(http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)"
MARKDOWN_URL = fr'\[(?:.+)\]\({URL}(?: "(?:.+)")?\)'

MARKDOWN_URL_OR_URL = re.compile(fr"{MARKDOWN_URL}|{URL}")


def irregular_flatify(lst):
    for el in lst:
        if el:
            if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
                yield from irregular_flatify(el)
            else:
                yield el


def uniquify(seq, keep_order=False):
    return list(set(seq)) if not keep_order else list(dict.fromkeys(seq))


def get_markdown_files(path):
    markdown_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".md"):
                markdown_files.append(os.path.join(root, file))

    return markdown_files


def get_markdown_file_content(filename):
    with open(filename, "r", encoding="utf-8") as file:
        content = file.read()
    return content


def get_urls(files):
    urls = []
    for file in files:
        content = get_markdown_file_content(file)
        urls.append(MARKDOWN_URL_OR_URL.findall(content))
    return uniquify(irregular_flatify(urls))


def main():
    markdown_files = get_markdown_files(os.getcwd())
    urls = get_urls(markdown_files)

    for url in urls:
        try:
            req = requests.get(url)
            if req.status_code == 200:
                print("Good")
        except requests.exceptions.RequestException:
            # More info: https://requests.readthedocs.io/en/master/user/quickstart/#errors-and-exceptions
            print("Bad")


main()
