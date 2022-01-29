import threading
import uvicorn
from fastapi import FastAPI, status, Depends, HTTPException
from rabbitmq import ConsumerThread
from logging import getLogger
from schemas import TokenIn, TokenOut
from sqlalchemy.orm import Session
from database import get_db
from models import Token, Manipulation
from datetime import datetime, timezone

app = FastAPI()
logger = getLogger("uvicorn")


@app.post(
    "/check_token",
    status_code=status.HTTP_200_OK,
    response_model=TokenOut
)
def check_token(request: TokenIn, db: Session = Depends(get_db)) -> dict:
    auth_data = db.query(
        Token.email, Token.expires_at, Manipulation.manipulation
    ).join(
        Manipulation, Token.id == Manipulation.token_id
    ).filter(
        Token.token == request.token
    ).first()

    if not auth_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="認証情報が取得できませんでした。")

    email, expires_at, manipulation = auth_data
    if manipulation != request.manipulation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="認証情報が一致しません。")

    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="トークンの期限が切れています。")

    return {"email": email}


@app.on_event("shutdown")
def terminate_threads() -> None:
    for thread in threading.enumerate():
        if thread is threading.current_thread():
            continue
        thread.terminate_consume()


if __name__ == "__main__":
    queue_name_and_action = (
        ("register_mail_queue", "register"),
        ("update_mail_queue", "update_email"),
        ("confirm_register_queue", "confirm_register")
    )

    for queue_name, action in queue_name_and_action:
        thread = ConsumerThread(queue_name=queue_name, action=action)
        thread.start()

    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=False)
