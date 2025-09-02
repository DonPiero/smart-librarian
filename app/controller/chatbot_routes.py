import base64
from io import BytesIO
from fastapi.responses import Response
from openai import OpenAI
from app.utils.helpers import bots, get_db
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import UploadFile, File
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


@router.post("/conversations/{conversation_id}/stt",
             response_model=ConversationWithMessages)
async def speech_to_text(conversation_id: int,
                         file: UploadFile = File(...),
                         db: Session = Depends(get_db),
                         current_user=Depends(get_current_user)):
    conv = (
        db.query(m.Conversation)
        .filter(m.Conversation.id == conversation_id,
                m.Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    audio_bytes = await file.read()
    await file.close()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio upload")

    client = OpenAI()

    bio = BytesIO(audio_bytes)
    bio.name = file.filename or "audio.webm"

    transcript = ""
    try:
        res = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=bio,
            response_format="json"
        )
        transcript = (res.text or "").strip()
    except Exception:
        bio.seek(0)
        res2 = client.audio.transcriptions.create(
            model="whisper-1",
            file=bio,
            response_format="text"
        )
        transcript = res2.strip() if isinstance(res2, str) else str(res2 or "").strip()

    if not transcript:
        raise HTTPException(status_code=400, detail="Empty transcript")

    payload = MessageIn(content=transcript)
    return send_message(conversation_id=conversation_id,
                        payload=payload,
                        db=db,
                        current_user=current_user)


@router.get("/conversations/{conversation_id}/tts")
def text_to_speech(conversation_id: int,
                   db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):

    msg = (
        db.query(m.Message)
        .join(m.Conversation)
        .filter(m.Conversation.id == conversation_id,
                m.Conversation.user_id == current_user.id,
                m.Message.role == "assistant")
        .order_by(m.Message.created_at.desc())
        .first()
    )

    client = OpenAI()

    text_input = (msg.content or "").strip()
    if not text_input:
        raise HTTPException(status_code=400, detail="No text to synthesize")

    try:
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text_input
        ) as resp:
            audio_bytes = resp.read()
    except Exception:
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-realtime-preview-2024-12-17",
            voice="alloy",
            input=text_input
        ) as resp:
            audio_bytes = resp.read()

    return Response(content=audio_bytes, media_type="audio/mpeg")


@router.get("/conversations/{conversation_id}/image")
def image_generator(conversation_id: int,
                    db: Session = Depends(get_db),
                    current_user=Depends(get_current_user)):

    msgs = (
        db.query(m.Message)
        .join(m.Conversation)
        .filter(m.Conversation.id == conversation_id,
                m.Conversation.user_id == current_user.id)
        .order_by(m.Message.created_at.desc())
        .limit(2)
        .all()
    )
    if not msgs:
        raise HTTPException(status_code=404, detail="No messages found")

    prompt = "\n\n".join([(mm.content or "").strip() for mm in reversed(msgs)]).strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="No text to turn into image")

    client = OpenAI()

    try:
        img = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="512x512",
        )
        image_b64 = img.data[0].b64_json
    except Exception:
        img = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )
        image_b64 = img.data[0].b64_json

    image_bytes = base64.b64decode(image_b64)
    return Response(content=image_bytes, media_type="image/png")

