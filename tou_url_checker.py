import os
import re
import sys
from collections.abc import Iterable

import requests

# `?:`: Non-capturing group
URL = r"(http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)"
MARKDOWN_URL = fr'\[(?:.+)\]\({URL}(?: "(?:.+)")?\)'

MARKDOWN_URL_OR_URL = re.compile(fr"{MARKDOWN_URL}|{URL}")

REPO = os.getenv("GITHUB_REPOSITORY")
print(REPO)
EXIT_STATUS = 0


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


def get_all_urls(files):
    urls = []
    for file in files:
        content = get_markdown_file_content(file)
        urls.append(MARKDOWN_URL_OR_URL.findall(content))
    return uniquify(irregular_flatify(urls))


def get_urls(file):
    content = get_markdown_file_content(file)
    return uniquify(irregular_flatify(MARKDOWN_URL_OR_URL.findall(content)))


print(os.getcwd())
markdown_files = get_markdown_files(os.getcwd())

for markdown_file in markdown_files:
    print(markdown_file)

    urls = get_urls(markdown_file)

    for url in urls:
        try:
            req = requests.get(url)
            if req.status_code == 200:
                print(f"✅ 200 · {url}")
            elif req.status_code >= 400:
                print(f"❌ {req.status_code} · {url}")
                EXIT_STATUS = 1
            else:
                print(f"{req.status_code} · {url}")
        except requests.exceptions.RequestException as e:
            # More info: https://requests.readthedocs.io/en/master/user/quickstart/#errors-and-exceptions
            print(f"❌ {e.__class__.__name__} · {url}")
            EXIT_STATUS = 1

sys.exit(EXIT_STATUS)
