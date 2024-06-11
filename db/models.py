import uuid
from sqlalchemy import Column
from sqlalchemy import UUID
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy import func
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

    messages = relationship(argument="Message", back_populates="user")
    connection_history = relationship(argument="ConnectionHistory", back_populates="user")

class ConnectionHistory(Base):
    __tablename__ = "connection_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    connected_at = Column(DateTime(timezone=True), default=func.now())
    disconnected_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="connection_history")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

    user = relationship(argument="User", back_populates="messages")
    