from app.utils.helpers import bots, get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth.jwt_auth import get_current_user
from app.models import db_model as m
from app.models.schemas import (ConversationOut,
                                ConversationWithMessages,
                                MessageIn)
from app.config.constants import MODEL_CONFIG, PROMPT_CONFIG
from app.services.chat_service import create_agent  # your bot factory


router = APIRouter()


@router.post("/conversations", response_model=ConversationOut)
def create_conversation(db: Session = Depends(get_db),
                        current_user=Depends(get_current_user)):
    conv = m.Conversation(user_id=current_user.id, title="New conversation")
    db.add(conv)
    db.commit()
    db.refresh(conv)

    bots[conv.id] = create_agent(MODEL_CONFIG, PROMPT_CONFIG)

    return {"id": conv.id, "title": conv.title}


@router.get("/conversations", response_model=list[ConversationOut])
def list_conversations(db: Session = Depends(get_db),
                       current_user=Depends(get_current_user)):
    convos = (
        db.query(m.Conversation)
        .filter(m.Conversation.user_id == current_user.id)
        .order_by(m.Conversation.updated_at.desc().nullslast())
        .all()
    )
    return [{"id": c.id, "title": c.title} for c in convos]


@router.get("/conversations/{conversation_id}",
            response_model=ConversationWithMessages)
def get_conversation(conversation_id: int,
                     db: Session = Depends(get_db),
                     current_user=Depends(get_current_user)):
    conv = (
        db.query(m.Conversation)
        .filter(m.Conversation.id == conversation_id,
                m.Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Conversation not found")

    msgs = (
        db.query(m.Message)
        .filter(m.Message.conversation_id == conv.id)
        .order_by(m.Message.created_at.asc())
        .all()
    )
    return {
        "conversation": {"id": conv.id, "title": conv.title},
        "messages": [{"id": m_.id,
                      "role": m_.role,
                      "content": m_.content} for m_ in msgs],
    }


@router.post("/conversations/{conversation_id}/messages",
             response_model=ConversationWithMessages)
def send_message(conversation_id: int,
                 payload: MessageIn,
                 db: Session = Depends(get_db),
                 current_user=Depends(get_current_user)):
    conv = (
        db.query(m.Conversation)
        .filter(m.Conversation.id == conversation_id,
                m.Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Conversation not found")
    if not payload.content.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Message content required")

    user_msg = m.Message(conversation_id=conv.id,
                         role="user",
                         content=payload.content.strip())
    db.add(user_msg)
    db.commit()

    if conv.id not in bots:
        bots[conv.id] = create_agent(MODEL_CONFIG, PROMPT_CONFIG)

    chat_fn = bots[conv.id]
    bot_reply = chat_fn(payload.content.strip())

    bot_msg = m.Message(conversation_id=conv.id,
                        role="assistant",
                        content=bot_reply)
    db.add(bot_msg)
    db.commit()

    if conv.title == "New conversation":
        words = payload.content.strip().split()
        conv.title = " ".join(words[:8]) if words else "New conversation"
        db.commit()

    msgs = (
        db.query(m.Message)
        .filter(m.Message.conversation_id == conv.id)
        .order_by(m.Message.created_at.asc())
        .all()
    )
    return {
        "conversation": {"id": conv.id, "title": conv.title},
        "messages": [{"id": m_.id,
                      "role": m_.role,
                      "content": m_.content} for m_ in msgs],
    }


@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int,
                        db: Session = Depends(get_db),
                        current_user=Depends(get_current_user)):
    conv = (
        db.query(m.Conversation)
        .filter(m.Conversation.id == conversation_id,
                m.Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Conversation not found")

    db.delete(conv)
    db.commit()

    bots.pop(conv.id, None)
    return
