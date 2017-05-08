FROM confluentinc/cp-base

MAINTAINER Ryan Anguiano

WORKDIR /app
ADD requirements.txt requirements_dev.txt ./

RUN set -ex && \
    buildDeps='build-essential curl gcc git make' && \
    projectDeps='libpcre3-dev libssl-dev libffi-dev python-dev librdkafka-dev confluent-kafka-2.11' && \
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
