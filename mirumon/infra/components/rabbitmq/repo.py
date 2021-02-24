from aio_pika import Queue, Exchange

from mirumon.application.repositories import Repository


class RabbitMQRepository(Repository):
    """RabbitMQ repository implementation."""

    def __init__(
        self, queue: Queue, exchange: Exchange
    ) -> None:
        self.queue: Queue = queue
        self.exchange: Exchange = exchange

    def publish(self, topic, body):
        pass

    def consume(self, topic):
        pass
