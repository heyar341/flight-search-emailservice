import sys
import pika
from os import environ
from logging import getLogger
from mail_sender import EmailSender
from threading import Thread

logger = getLogger("uvicorn")


class ConsumerThread(Thread):
    def __init__(self, queue_name: str, action: str):
        super(ConsumerThread, self).__init__()
        self.daemon = True
        self.name = queue_name

        self.queue_name = queue_name
        self.action = action

    def callback(self, ch, method, properties, body) -> None:
        mail_address = body.decode()
        logger.info(f"Received {mail_address} from {self.queue_name}.")
        mail_sender = EmailSender(recipient=mail_address, action=self.action)
        status_code, message = mail_sender.send()
        if status_code == 200:
            logger.info(f"Succeeded in sending email to {mail_address}")
        else:
            logger.error(
                f"Failed to send email to {mail_address}."
                f"Error code: {status_code}, error message: {message}"
            )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self) -> None:
        user = environ.get("RABBITMQ_USER")
        password = environ.get("RABBITMQ_PASSWORD")
        host = environ.get("RABBITMQ_HOST")
        port = environ.get("RABBITMQ_PORT")

        try:
            params = pika.URLParameters(
                f"amqp://{user}:{password}@{host}:{port}")
            connection = pika.BlockingConnection(params)
        except NameError as e:
            logger.error(f"Failed to connect to RabbitMQ. {type(e)}: {e}")
            return
        except RuntimeError as e:
            logger.error(f"Failed to connect to RabbitMQ. {type(e)}: {e}")
            return
        channel = connection.channel()

        channel.queue_declare(queue=self.queue_name, durable=True)
        print(f"Waiting for messages from {self.queue_name}.")
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue=self.queue_name, on_message_callback=self.callback,
            consumer_tag=self.action
        )

        channel.start_consuming()

    def terminate_consume(self):
        try:
            sys.exit(0)
        except SystemExit:
            logger.info(f"Thread for {self.name} was terminated.")
