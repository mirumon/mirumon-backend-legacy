from mirumon.infra.repo_protocol import Repository


class RabbitMQRepository(Repository):
    """RabbitMQ repository implementation."""

    def __init__(self, queue: object, exchange: object, process_timeout: float) -> None:
        self.queue = queue
        self.exchange = exchange
        self.process_timeout = process_timeout
