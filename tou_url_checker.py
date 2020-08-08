import os
import re
import sys
from collections.abc import Sequence
from typing import Iterator, List, Union

import requests

# `?:`: Non-capturing group
URL = r"(http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)"
MARKDOWN_URL = fr'\[(?:.+)\]\({URL}(?: "(?:.+)")?\)'

MARKDOWN_URL_OR_URL = re.compile(fr"{MARKDOWN_URL}|{URL}")

# More info: https://docs.github.com/en/actions/configuring-and-managing-workflows/using-environment-variables#default-environment-variables
REPO = os.getenv("GITHUB_REPOSITORY", "")
WORKSPACE = os.getenv("GITHUB_WORKSPACE", "")
EXIT_STATUS = 0


class Colors:
    BOLD = "\033[1m"
    RESET = "\033[0m"
    LIGHT_RED = "\033[1;31m"


# Sequence: https://docs.python.org/3/glossary.html#term-sequence
def irregular_flatify(lst: Sequence) -> Iterator[Sequence]:
    for el in lst:
        if el:
            # Sequence or Iterable
            if isinstance(el, Sequence) and not isinstance(el, (str, bytes)):
                yield from irregular_flatify(el)
            else:
                yield el


def uniquify(
    seq: Union[Sequence, Iterator[Sequence]], keep_order: bool = False
) -> list:
    return list(set(seq)) if not keep_order else list(dict.fromkeys(seq))


def get_markdown_files(path: str) -> List[str]:
    markdown_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".md"):
                markdown_files.append(os.path.join(root, file))
    return markdown_files


def get_markdown_file_content(filename: str) -> str:
    with open(filename, "r", encoding="utf-8") as file:
        content = file.read()
    return content


def get_all_urls(files: List[str]) -> List[str]:
    urls = []
    for file in files:
        content = get_markdown_file_content(file)
        urls.append(MARKDOWN_URL_OR_URL.findall(content))
    return uniquify(irregular_flatify(urls))


def get_urls(file: str) -> List[str]:
    content = get_markdown_file_content(file)
    return uniquify(irregular_flatify(MARKDOWN_URL_OR_URL.findall(content)))


markdown_files = get_markdown_files(os.getcwd())

for markdown_file in markdown_files:
    approx_path = markdown_file.replace(WORKSPACE, REPO)

    print(f"\n{Colors.BOLD}{approx_path}{Colors.RESET}")

    urls = get_urls(markdown_file)

    for url in urls:
        try:
            req = requests.get(url)
            if req.status_code == 200:
                print(f"✅ 200 · {url}")
            elif req.status_code >= 400:
                print(f"❌ {Colors.LIGHT_RED}{req.status_code} · {url}{Colors.RESET}")
                EXIT_STATUS = 1
            else:
                print(f"{req.status_code} · {url}")
        except requests.exceptions.RequestException as e:
            # More info: https://requests.readthedocs.io/en/master/user/quickstart/#errors-and-exceptions
            print(f"❌ {Colors.LIGHT_RED}{e.__class__.__name__} · {url}{Colors.RESET}")
            EXIT_STATUS = 1

sys.exit(EXIT_STATUS)
