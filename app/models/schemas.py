from typing import List
from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class ConversationOut(BaseModel):
    id: int
    title: str
    model_config = ConfigDict(from_attributes=True)


class MessageIn(BaseModel):
    content: str = Field(min_length=1)


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    model_config = ConfigDict(from_attributes=True)


class ConversationWithMessages(BaseModel):
    conversation: ConversationOut
    messages: List[MessageOut]
