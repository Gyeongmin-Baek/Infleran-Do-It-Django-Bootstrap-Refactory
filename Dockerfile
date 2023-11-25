# pull of official base image
FROM python:3.10-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variable
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

COPY . /usr/src/app/

# intsall dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt