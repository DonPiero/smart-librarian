from sqlalchemy import (Column,
                        Integer,
                        String,
                        ForeignKey,
                        Index,
                        Text,
                        DateTime,
                        func)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    conversations = relationship("Conversation",
                                 back_populates="user",
                                 cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                     index=True, nullable=False)
    title = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(),
                        onupdate=func.now())

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message",
                            back_populates="conversation",
                            cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_conversations_user_updated", "user_id", "updated_at"),
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer,
                             ForeignKey("conversations.id",
                                        ondelete="CASCADE"),
                             index=True,
                             nullable=False)
    role = Column(String(16), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    conversation = relationship("Conversation",
                                back_populates="messages")

    __table_args__ = (
        Index("ix_messages_conv_created",
              "conversation_id",
              "created_at"),
    )
