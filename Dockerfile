FROM python:2.7-slim

MAINTAINER Ryan Anguiano

# Install librdkafka from Confluent Repo
ADD http://packages.confluent.io/deb/3.2/archive.key /confluent.key
RUN apt-key add /confluent.key && \
    echo "deb [arch=amd64] http://packages.confluent.io/deb/3.2 stable main" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y librdkafka-dev confluent-kafka-2.11 --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* && \
    rm /confluent.key

WORKDIR /app
ADD requirements.txt requirements_dev.txt ./

RUN set -ex && \
    buildDeps='build-essential curl gcc git make' && \
    projectDeps='libpcre3-dev libssl-dev libffi-dev' && \
    apt-get update && \
    apt-get install -y $buildDeps $projectDeps --no-install-recommends && \
    pip install -U pip setuptools wheel && \
    pip install -r /app/requirements.txt -r /app/requirements_dev.txt && \
    apt-get purge -y $buildDeps && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

ADD kafka_gconsumer/ kafka_gconsumer/
ADD tests/ tests/
ADD HISTORY.rst README.rst setup.py ./

RUN pip install .

CMD ["py.test"]
