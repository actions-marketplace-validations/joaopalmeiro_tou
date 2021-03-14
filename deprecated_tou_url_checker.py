import os
import re
import sys
from collections.abc import Sequence
from functools import partial
from typing import Iterator, List, Union

import requests

# `?:`: Non-capturing group
# `$-_@` -> `#-_@`
URL = r"(http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)"
MARKDOWN_URL = fr'\[(?:[^\[]+)\]\({URL}(?: "(?:.+)")?\)'

MARKDOWN_URL_OR_URL = re.compile(fr"{MARKDOWN_URL}|{URL}")

# More info: https://docs.github.com/en/actions/configuring-and-managing-workflows/using-environment-variables#default-environment-variables
REPO = os.getenv("GITHUB_REPOSITORY", "")
WORKSPACE = os.getenv("GITHUB_WORKSPACE", "")

# EXIT_STATUS = 0
LINK_STATUS = dict(ok=0, not_ok=0)

TAB = " " * 4


class Colors:
    BOLD = "\033[1m"
    RESET = "\033[0m"
    LIGHT_RED = "\033[1;31m"


def lprint(lst: Sequence) -> None:
    """Pretty print `lst`."""
    print(*lst, sep="\n")


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


# https://www.python.org/dev/peps/pep-0484/#the-numeric-tower
def get_percentage(numerator: int, denominator: int) -> float:  # or Union[int, float]
    try:
        fraction = numerator / denominator
        return fraction
    except ZeroDivisionError:
        return 0


def get_number_links_breakdown(status: str, percentage: float) -> str:
    label = "Not OK" if status == "not_ok" else status.upper()
    fmt = (
        ".0%"
        if isinstance(percentage, int) or (percentage * 100).is_integer()
        else ".2%"
    )

    return f"{TAB}{label}: {LINK_STATUS[status]} ({percentage:{fmt}})"


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


def process_markdown_links_within_parentheses(
    content: str, urls: List[str]
) -> List[str]:
    within_parentheses = fr"\(*\[(.*?)\]\((.*?)\)+"

    # `url.group(2)`: URL only.
    urls_markdown_aux = [
        url.group() for url in re.compile(within_parentheses).finditer(content)
    ]

    double_check = [
        (url_md, url)
        for url_md in urls_markdown_aux
        for url in urls
        if url.endswith(")") and url in url_md
    ]

    for url_pair in double_check:
        number_left_par = len(url_pair[0]) - len(url_pair[0].lstrip("("))

        urls[urls.index(url_pair[1])] = url_pair[1][:-number_left_par]

    return urls


def process_markdown_links_within_parentheses_v2(
    content: str, urls: List[str]
) -> List[str]:
    within_parentheses = fr"\(*\[(.*?)\]\((.*?)\)+"

    urls_markdown_aux = [
        url.group(2) for url in re.compile(within_parentheses).finditer(content)
    ]

    double_check = [
        (url_md, url)
        for url_md in urls_markdown_aux
        for url in urls
        if url.endswith(")") and url.rstrip(")") in url_md
    ]

    for url_pair in double_check:
        urls[urls.index(url_pair[1])] = url_pair[0]

    return urls


def get_urls(file: str) -> List[str]:
    content = get_markdown_file_content(file)

    urls = uniquify(irregular_flatify(MARKDOWN_URL_OR_URL.findall(content)))
    urls = process_markdown_links_within_parentheses_v2(content, urls)

    return urls


markdown_files = get_markdown_files(os.getcwd())

for markdown_file in markdown_files:
    approx_path = markdown_file.replace(WORKSPACE, REPO)

    print(f"\n{Colors.BOLD}{approx_path}{Colors.RESET}")

    urls = get_urls(markdown_file)

    for url in urls:
        try:
            req = requests.get(url)
            if req.status_code == 200:
                LINK_STATUS["ok"] += 1
                print(f"✅ 200 · {url}")
            elif req.status_code >= 400:
                LINK_STATUS["not_ok"] += 1
                print(f"❌ {Colors.LIGHT_RED}{req.status_code} · {url}{Colors.RESET}")
                # EXIT_STATUS = 1
            else:
                LINK_STATUS["not_ok"] += 1
                print(f"{req.status_code} · {url}")
        except requests.exceptions.RequestException as e:
            # More info: https://requests.readthedocs.io/en/master/user/quickstart/#errors-and-exceptions
            LINK_STATUS["not_ok"] += 1
            print(f"❌ {Colors.LIGHT_RED}{e.__class__.__name__} · {url}{Colors.RESET}")
            # EXIT_STATUS = 1

total_number_links = sum(LINK_STATUS.values())

get_percentage_links = partial(get_percentage, denominator=total_number_links)

ok_percentage = get_percentage_links(LINK_STATUS["ok"])
not_ok_percentage = get_percentage_links(LINK_STATUS["not_ok"])

print(f"\n🧮 {Colors.BOLD}Metrics{Colors.RESET}")
print(f"Number of Markdown files: {len(markdown_files)}")
print(f"Number of links: {total_number_links}")
print(get_number_links_breakdown("ok", ok_percentage))
print(get_number_links_breakdown("not_ok", not_ok_percentage))

exit_status = 0 if LINK_STATUS["not_ok"] == 0 else 1
sys.exit(exit_status)
