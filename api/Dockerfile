FROM python:3.10.16-alpine AS base

WORKDIR /api

COPY ./ /api
RUN apk add curl

RUN pip install setuptools>=65.5.1

RUN pip install --no-cache-dir -r requirements.txt 

CMD [ "python3", "-m", "fastapi", "dev", "main.py"]
