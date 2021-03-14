import os
import re
import sys
from functools import partial
from typing import List

import mistune
import requests
from mistune.plugins.extra import URL_LINK_PATTERN


# Helper functions
def get_gh_input_name(yml_input_name: str) -> str:
    yml_input_name = yml_input_name.replace(" ", "_").upper()

    return f"INPUT_{yml_input_name}".strip()


# Constants
# Based on: https://github.com/marketplace/actions/value-as-flag
BOOLEAN_VALUES = {
    "true": True,
    "t": True,
    "yes": True,
    "y": True,
    "1": True,
    "false": False,
    "f": False,
    "no": False,
    "n": False,
    "0": False,
}


# More info: https://docs.github.com/en/actions/configuring-and-managing-workflows/using-environment-variables#default-environment-variables
REPO = os.getenv("GITHUB_REPOSITORY", "")
WORKSPACE = os.getenv("GITHUB_WORKSPACE", "")

# GitHub creates an environment variable for the input with the name `INPUT_<VARIABLE_NAME>`
# os.environ["INPUT_IGNORE-403-FORBIDDEN"] = "false"
IGNORE_403_FORBIDDEN = BOOLEAN_VALUES[
    os.getenv(get_gh_input_name("ignore-403-forbidden"), "false").lower()
]

# EXIT_STATUS = 0
LINK_STATUS = dict(ok=0, not_ok=0)

TAB = " " * 4
URL_PATTERN = re.compile(URL_LINK_PATTERN)


# Based on: https://gist.github.com/rene-d/9e584a7dd2935d0f461904b9f2950007
class Style:
    BOLD = "\033[1m"
    RESET = "\033[0m"
    LIGHT_RED = "\033[1;31m"
    YELLOW = "\033[1;33m"


class Icons:
    OK = "✅"
    NOT_OK = "❌"
    SUMMARY = "🧮"
    IGNORE = "🤔"


# Functions
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


def get_urls(file: str, parser: mistune.Markdown) -> List[str]:
    content = get_markdown_file_content(file)
    html = parser(content)

    # Group #1 — None of: '" >
    # Includes anchor links
    links = set(re.findall(r'href=[\'"]?([^\'" >]+)', html))

    urls = list(filter(URL_PATTERN.match, links))

    return urls


# https://www.python.org/dev/peps/pep-0484/#the-numeric-tower
def get_percentage(numerator: int, denominator: int) -> float:
    try:
        fraction = numerator / denominator
        return fraction
    except ZeroDivisionError:
        return 0


def get_number_links_breakdown(status: str, percentage: float) -> str:
    label = "Not OK" if status == "not_ok" else status.upper()
    # icon = "👎" if status == "not_ok" else "👍"
    icon = Icons.NOT_OK if status == "not_ok" else Icons.OK

    fmt = (
        ".0%"
        if isinstance(percentage, int) or (percentage * 100).is_integer()
        else ".2%"
    )

    return f"{TAB}{icon} {label}: {LINK_STATUS[status]} ({percentage:{fmt}})"


# Script
markdown_files = get_markdown_files(os.getcwd())
markdown_parser = mistune.create_markdown(plugins=["url"])

for markdown_file in markdown_files:
    approx_path = markdown_file.replace(WORKSPACE, REPO)
    print(f"\n{Style.BOLD}{approx_path}{Style.RESET}")

    urls = get_urls(markdown_file, markdown_parser)

    for url in urls:
        try:
            req = requests.get(url)
            if req.status_code == 200:
                LINK_STATUS["ok"] += 1
                print(f"{Icons.OK} 200 · {url}")
            elif req.status_code >= 400:
                if IGNORE_403_FORBIDDEN and req.status_code == 403:
                    print(
                        f"{Icons.IGNORE} {Style.YELLOW}{req.status_code} · {url}{Style.RESET}"
                    )
                else:
                    LINK_STATUS["not_ok"] += 1
                    print(
                        f"{Icons.NOT_OK} {Style.LIGHT_RED}{req.status_code} · {url}{Style.RESET}"
                    )
            else:
                LINK_STATUS["not_ok"] += 1
                print(f"{req.status_code} · {url}")
        except requests.exceptions.RequestException as e:
            # More info: https://requests.readthedocs.io/en/master/user/quickstart/#errors-and-exceptions
            LINK_STATUS["not_ok"] += 1
            print(
                f"{Icons.NOT_OK} {Style.LIGHT_RED}{e.__class__.__name__} · {url}{Style.RESET}"
            )

total_number_links = sum(LINK_STATUS.values())

get_percentage_links = partial(get_percentage, denominator=total_number_links)

ok_percentage = get_percentage_links(LINK_STATUS["ok"])
not_ok_percentage = get_percentage_links(LINK_STATUS["not_ok"])

print(f"\n{Icons.SUMMARY} {Style.BOLD}Metrics{Style.RESET}")
print(f"Number of Markdown files: {len(markdown_files)}")
print(f"Number of links: {total_number_links}")
print(get_number_links_breakdown("ok", ok_percentage))
print(get_number_links_breakdown("not_ok", not_ok_percentage))

exit_status = 0 if LINK_STATUS["not_ok"] == 0 else 1
sys.exit(exit_status)
