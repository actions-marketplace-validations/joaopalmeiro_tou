FROM python:3.7

LABEL version="0.2.2" \ 
    maintainer="jm.palmeiro@campus.fct.unl.pt" \ 
    description="Tou.md, a Github Action to find broken links in Markdown files."

ENV WORKON_HOME /root
ENV PIPENV_PIPFILE /Pipfile

COPY tou_url_checker.py /
COPY Pipfile /
COPY Pipfile.lock /

RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile
ENTRYPOINT ["pipenv", "run", "python", "/tou_url_checker.py"]