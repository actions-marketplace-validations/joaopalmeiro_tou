FROM python:3.7

ENV WORKON_HOME /root
ENV PIPENV_PIPFILE /Pipfile

COPY tou_url_checker.py /
COPY Pipfile /
COPY Pipfile.lock /

RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile
ENTRYPOINT ["pipenv", "run", "python", "/tou_url_checker.py"]