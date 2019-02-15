FROM python:3.6
MAINTAINER James W. Curtin <jameswcurtin@gmail.com>

ENV PYTHONUNBUFFERED 1

RUN apt-get update


COPY ./Pipfile /
COPY ./Pipfile.lock /

RUN pip install --upgrade pip pipenv
RUN pipenv install --deploy --system --skip-lock --dev

COPY . /

EXPOSE 5000 
