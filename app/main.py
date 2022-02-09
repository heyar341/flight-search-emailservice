import threading
from rabbitmq import ConsumerThread
from logging import getLogger

logger = getLogger("uvicorn")


if __name__ == "__main__":
    queue_name_and_action = (
        ("pre_register_email", "pre_register"),
        ("update_email_email", "update_email"),
        ("confirm_register_email", "confirm_register")
    )

    for queue_name, action in queue_name_and_action:
        thread = ConsumerThread(queue_name=queue_name, action=action)
        thread.start()

    for thread in threading.enumerate():
        if thread is threading.current_thread():
            continue
        thread.join()

