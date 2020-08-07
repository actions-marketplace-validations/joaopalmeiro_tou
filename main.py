import os
import re

# `?:`: Non-capturing group
URL = re.compile(
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)

FILENAMES = "https://raw.githubusercontent.com/joaopalmeiro/cheatsheets/master/airflow/README.md"

FILES = [file.strip() for file in FILENAMES.split(",")]


def get_markdown_files(path=os.getcwd()):
    markdown_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".md"):
                markdown_files.append(os.path.join(root, file))

    return markdown_files


print(get_markdown_files())
