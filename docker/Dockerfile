# qwerty112358/python-uv:1.0.0
FROM python:3.11.4-slim-bookworm

RUN apt update -y && apt install git openssh-client curl sudo -y

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

RUN export PATH=/root/.local/bin:$PATH
