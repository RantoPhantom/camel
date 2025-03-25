FROM python:3.10.16-alpine AS base

WORKDIR /api

COPY ./requirements.txt ./
RUN apk add --no-cache curl &&\
	pip install --no-cache-dir setuptools>=65.5.1 &&\
	pip install --no-cache-dir -r requirements.txt 

COPY ./ ./

CMD [ "python3", "-m", "fastapi", "run", "main.py"]
