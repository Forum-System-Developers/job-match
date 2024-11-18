FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    make \
    git \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    llvm \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    liblzma-dev \
    tk-dev \
    libffi-dev \
    libdb-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl https://pyenv.run | bash

ENV PATH="/root/.pyenv/shims:/root/.pyenv/bin:$PATH"

WORKDIR /app
COPY . /app

RUN pyenv install 3.12.7
RUN pyenv local 3.12.7

RUN pip install --upgrade pip
RUN pip install build
RUN python -m build
RUN pip install .

EXPOSE 8000
