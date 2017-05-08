#!/usr/bin/env python
"""
test_kafka_gconsumer
----------------------------------

Tests for `kafka_gconsumer` module.
"""

import pytest

from kafka_gconsumer import Consumer, AvroConsumer


@pytest.fixture(scope='session')
def produced_plain_messages():
    pass


@pytest.fixture(scope='session')
def produced_avro_messages():
    pass


def test_content(produced_plain_messages):
    pass
