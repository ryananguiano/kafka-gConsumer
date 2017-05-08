#!/usr/bin/env python
"""
test_kafka_gconsumer
----------------------------------

Tests for `kafka_gconsumer` module.
"""

import os
import pytest
import random
import string

from confluent_kafka import Producer
from confluent_kafka.avro import AvroProducer
from kafka_gconsumer import Consumer, AvroConsumer


def random_str(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


@pytest.fixture
def consumer_settings():
    return {
        'bootstrap.servers': os.environ.get('KAFKA_BOOTSTRAP_SERVERS'),
        'group.id': 'gConsumer-test-consumer-{}'.format(random_str(5)),
        'topic.auto.offset.reset': 'earliest',
    }


@pytest.fixture
def producer_settings():
    return {
        'bootstrap.servers': os.environ.get('KAFKA_BOOTSTRAP_SERVERS'),
        'group.id': 'gConsumer-test-producer-{}'.format(random_str(5)),
    }


@pytest.fixture
def avro_consumer_settings(consumer_settings):
    settings = {
        'schema.registry.url': os.environ.get('KAFKA_SCHEMA_REGISTRY_URL'),
    }
    settings.update(consumer_settings)
    return settings


@pytest.fixture
def avro_producer_settings(producer_settings):
    settings = {
        'schema.registry.url': os.environ.get('KAFKA_SCHEMA_REGISTRY_URL'),
    }
    settings.update(producer_settings)
    return settings


def produced_plain_messages(topic, count):
    pass


def produced_avro_messages(topic):
    pass


def test_producer(producer_settings):
    producer = Producer(**producer_settings)
    producer.produce('test_messages', 'test123')
