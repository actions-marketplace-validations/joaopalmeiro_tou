import os
import re
from typing import List, Set

import mistune


# Helper functions
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


def get_urls(file: str, parser: mistune.Markdown) -> Set[str]:
    content = get_markdown_file_content(file)
    html = parser(content)

    urls = set(re.findall(r'href=[\'"]?([^\'" >]+)', html))

    return urls


# Script
markdown_files = get_markdown_files(os.getcwd())
markdown_parser = mistune.create_markdown(plugins=["url"])

for markdown_file in markdown_files:
    urls = get_urls(markdown_file, markdown_parser)

