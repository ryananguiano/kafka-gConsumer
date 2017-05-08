from confluent_kafka import Consumer as KafkaConsumer, KafkaError, KafkaException
from confluent_kafka.avro import AvroConsumer as KafkaAvroConsumer
import gevent
import gipc
import logging
import signal

logger = logging.getLogger(__name__)


class ConsumerBlockingLoop(object):
    @classmethod
    def spawn(cls, *args, **kwargs):
        loop = cls(*args, **kwargs)
        try:
            loop.run()
        finally:
            loop.shutdown()

    def __init__(self, worker_settings, consumer_class, consumer_settings, topics, queue):
        self.worker_settings = worker_settings
        self.enable_commit = not consumer_settings.get('enable.auto.commit')
        self.consumer = consumer_class(consumer_settings)
        self.consumer.subscribe(topics)
        self.queue = queue

    def run(self):
        while True:
            message = self.consumer.poll(timeout=self.worker_settings['poll_timeout'])

            if message is None:
                continue

            if message.error():
                if message.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    logger.info('%% %s [%d] reached end at offset %d\n' %
                                (message.topic(), message.partition(), message.offset()))
                elif message.error():
                    raise KafkaException(message.error())

            else:
                # Put message value in the queue
                self.queue.put(message)

                if self.worker_settings['commit_on_complete']:
                    self.commit()

    def shutdown(self):
        self.consumer.close()

    def commit(self):
        if self.enable_commit:
            self.consumer.commit(async=self.worker_settings['async_commit'])


class BaseConsumer(object):
    topics = []
    consumer_class = None
    consumer_settings = {}
    required_settings = []
    commit_on_complete = True
    async_commit = True
    poll_timeout = 1

    @classmethod
    def spawn(cls, *args, **kwargs):
        consumer = cls(*args, **kwargs)
        try:
            consumer.run()
        finally:
            consumer.teardown()

    def __init__(self, topics=None, settings=None, handler=None, commit_on_complete=None,
                 async_commit=None, poll_timeout=None):
        self.topics = topics or self.topics
        self.consumer_settings = settings or self.consumer_settings
        self.handler = handler or self.handle_message
        self.commit_on_complete = self.commit_on_complete if commit_on_complete is None else commit_on_complete
        self.async_commit = self.async_commit if async_commit is None else async_commit
        self.poll_timeout = self.poll_timeout if poll_timeout is None else poll_timeout

    def run(self):
        try:
            self.setup()
            while True:
                # If consumer has died, raise error
                if not self.loop.is_alive():
                    raise KafkaException(KafkaError._FAIL)

                try:
                    message = self.queue_read.get()
                except (gipc.GIPCError, EOFError):
                    pass
                else:
                    self.handler(message)
        except (KeyboardInterrupt, SystemExit, gevent.GreenletExit):
            pass
        finally:
            self.teardown()

    def setup(self):
        gevent.signal(signal.SIGTERM, self.teardown)
        self.queue_read, self.queue_write = gipc.pipe()
        self.loop = gipc.start_process(target=ConsumerBlockingLoop.spawn,
                                       args=(self.get_worker_settings(),
                                             self.get_consumer_class(),
                                             self.get_consumer_settings(),
                                             self.get_topics(),
                                             self.queue_write))

    def teardown(self):
        self.loop.terminate()
        self.loop.join()
        try:
            self.queue_read.close()
            self.queue_write.close()
        except gipc.GIPCClosed:
            pass

    def get_worker_settings(self):
        return {
            'commit_on_complete': self.commit_on_complete,
            'async_commit': self.async_commit,
            'poll_timeout': self.poll_timeout,
        }

    def get_consumer_class(self):
        if self.consumer_class is None:
            raise NotImplementedError
        return self.consumer_class

    def get_consumer_settings(self):
        initial_settings = {
            'enable.auto.commit': False,
            'api.version.request': True,
            'broker.version.fallback': '0.9.0',
        }
        return generate_consumer_settings(initial_settings, self.consumer_settings, self.required_settings)

    def get_topics(self):
        if not self.topics:
            raise NotImplementedError
        if not isinstance(self.topics, (list, tuple)):
            return [self.topics]
        return self.topics

    def handle_message(self, message):
        raise NotImplementedError


class Consumer(BaseConsumer):
    consumer_class = KafkaConsumer
    required_settings = ['bootstrap.servers', 'group.id']


class AvroConsumer(BaseConsumer):
    consumer_class = KafkaAvroConsumer
    required_settings = ['bootstrap.servers', 'group.id', 'schema.registry.url']


def generate_consumer_settings(initial_settings, user_settings, required_settings):
    for setting in required_settings:
        if setting not in user_settings:
            raise ValueError('Missing consumer setting: ' + setting)

    settings = initial_settings.copy()
    for key, val in user_settings.iteritems():
        if val is None:
            continue
        logger.debug('using kafka setting {}: {}'.format(key, val))
        if key.startswith('topic.'):
            settings['default.topic.config'][key[6:]] = val
        else:
            settings[key] = val
    return settings
