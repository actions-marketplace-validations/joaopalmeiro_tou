FROM python:3.7

ADD tou_url_checker.py /tou_url_checker.py
ADD Pipfile /Pipfile
ADD Pipfile.lock /Pipfile.lock

RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile
ENTRYPOINT ["pipenv", "run", "python", "./tou_url_checker.py"]