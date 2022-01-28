from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from database import Base


class RegisterToken(Base):
    __tablename__ = "register_token"
    id = Column(Integer, primary_key=True, nullable=False)
    token_id = Column(String, nullable=False)
    email = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False,
                        server_default=text("now()"))
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False,
                        default=datetime.now() + timedelta(hours=24))


