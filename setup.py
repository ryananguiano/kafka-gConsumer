#!/usr/bin/env python

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'confluent-kafka[avro]',
    'gevent',
    'gipc',
    'requests',
]

setup(
    name='kafka_gconsumer',
    version='0.1.0',
    description="gEvent compatible Kafka Consumer for Python 2",
    long_description=readme + '\n\n' + history,
    author="Ryan Anguiano",
    author_email='ryan.anguiano@gmail.com',
    url='https://github.com/ryananguiano/kafka-gConsumer',
    packages=[
        'kafka_gconsumer',
    ],
    package_dir={'kafka_gconsumer':
                 'kafka_gconsumer'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='kafka_gconsumer',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests'
)
