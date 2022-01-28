import pika
from os import environ
from logging import getLogger
from mail_sender import EmailSender
from functools import partial

logger = getLogger("uvicorn")


def callback(ch, method, properties, body, queue_name: str,
             action: str) -> None:
    mail_address = body.decode()
    logger.info(f"Received {mail_address} from {queue_name}.")
    mail_sender = EmailSender(recipient=mail_address, action=action)
    status_code, message = mail_sender.send()
    if status_code == 200:
        logger.info(f"Succeeded in sending email to {mail_address}")
    else:
        logger.error(
            f"Failed to send email to {mail_address}."
            f"Error code: {status_code}, error message: {message}"
        )
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume(queue_name: str, action: str) -> None:
    user = environ.get("RABBITMQ_USER")
    password = environ.get("RABBITMQ_PASSWORD")
    host = environ.get("RABBITMQ_HOST")
    port = environ.get("RABBITMQ_PORT")

    try:
        params = pika.URLParameters(f"amqp://{user}:{password}@{host}:{port}")
        connection = pika.BlockingConnection(params)
    except NameError as e:
        logger.error(f"Failed to connect to RabbitMQ. {type(e)}: {e}")
        return
    except RuntimeError as e:
        logger.error(f"Failed to connect to RabbitMQ. {type(e)}: {e}")
        return

    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    print(f"Waiting for messages from {queue_name}.")
    channel.basic_qos(prefetch_count=1)
    # partial関数のドキュメントURL
    # https://docs.python.org/3/library/functools.html#functools.partial
    callback_with_arguments = partial(
        callback, queue_name=queue_name, action=action
    )

    channel.basic_consume(
        queue=queue_name, on_message_callback=callback_with_arguments
    )

    channel.start_consuming()
