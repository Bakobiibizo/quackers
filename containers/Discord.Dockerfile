FROM ubuntu:22.04

WORKDIR /app

ARG DISCORD_TOKEN
ENV DISCORD_TOKEN=$DISCORD_TOKEN

RUN apt update && apt upgrade -y
RUN apt install build-essential -y
RUN apt install python3 python3-pip -y
RUN python3 -m pip install --upgrade pip
RUN pip install setuptools wheel
RUN apt install python-is-python3


COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app
COPY data/layers /app/data/layers
COPY data/fallacies.json /app/data/fallacies.json
COPY scripts/run_bot.py /app/entrypoint.py
COPY configs /app/configs

CMD python entrypoint.py
