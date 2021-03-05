# Tou.md

A [Github Action](https://docs.github.com/en/actions) to find broken links in Markdown files.

The name `Tou.md` comes from the [apheretic](https://en.wiktionary.org/wiki/apheresis) and informal form ([_tar_](https://www.flip.pt/Duvidas-Linguisticas/Duvida-Linguistica/DID/1878)) of the verb to be ([_estar_](https://en.wiktionary.org/wiki/estar#Portuguese)) in Portuguese (and the filename extension for [Markdown files](https://en.wikipedia.org/wiki/Markdown)).

## Quickstart

```yml
name: Sample workflow

on:
  push:
    branches:
      - master

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Tou.md
        uses: joaopalmeiro/tou@v0.1.3
```

## Acknowledgments

- https://github.com/paramt/url-checker
- https://stackoverflow.com/questions/19747371/python-exit-commands-why-so-many-and-when-should-each-be-used
- https://stackoverflow.com/questions/63143360/how-do-you-use-pipenv-in-a-github-action
- https://regex101.com/

## Development

- Update the version in the `Dockerfile` and in the `README.md` file.
