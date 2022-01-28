import threading
import uvicorn
from fastapi import FastAPI
from rabbitmq import consume
from threading import Thread
from logging import getLogger

app = FastAPI()
logger = getLogger("uvicorn")


@app.on_event("shutdown")
def terminate_threads() -> None:
    for thread in threading.enumerate():
        if thread is threading.current_thread():
            continue
        thread.join()


if __name__ == "__main__":
    queue_name_and_action = (
        ("register_mail_queue", "register"),
        ("update_mail_queue", "update_email"),
        ("confirm_register_queue", "confirm_register")
    )

    threads_list = []
    for thread_arg in queue_name_and_action:
        thread = Thread(target=consume, args=thread_arg, daemon=True)
        threads_list.append(thread)

    for thread in threads_list:
        thread.start()

    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)
