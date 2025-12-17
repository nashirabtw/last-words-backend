from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Message, Base
from datetime import datetime
import uuid

app = FastAPI()

Base.metadata.create_all(bind=engine)

# =========================
# CONFIG
# =========================
ADMIN_TOKEN = "CAMBIA_ESTE_TOKEN_SUPER_SECRETO"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# DB DEP
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# HELPERS
# =========================
def check_admin(x_admin_token: str):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

# =========================
# PUBLIC — MAP MESSAGES
# =========================
@app.get("/messages")
def get_messages(db: Session = next(get_db())):
    messages = (
        db.query(Message)
        .filter(Message.hidden == False)
        .order_by(Message.created_at.desc())
        .all()
    )

    return [
        {
            "id": m.id,
            "name": m.name,
            "message": m.message,
            "country": m.country,
            "emoji": m.emoji,
            "latitude": m.latitude,
            "longitude": m.longitude,
            "created_at": m.created_at,
        }
        for m in messages
    ]

# =========================
# SEND MESSAGE (TOKEN)
# =========================
@app.post("/send-message")
def send_message(payload: dict, x_payment_token: str = Header(None)):
    if not x_payment_token:
        raise HTTPException(status_code=401, detail="Missing token")

    db = SessionLocal()

    msg = Message(
        name=payload.get("name"),
        message=payload.get("message"),
        country=payload.get("country"),
        emoji="📍",
        latitude=payload.get("latitude"),
        longitude=payload.get("longitude"),
    )

    db.add(msg)
    db.commit()
    db.refresh(msg)
    db.close()

    return {"status": "ok"}

# =========================
# ADMIN — LIST ALL
# =========================
@app.get("/admin/messages")
def admin_messages(x_admin_token: str = Header(...)):
    check_admin(x_admin_token)

    db = SessionLocal()
    messages = db.query(Message).order_by(Message.created_at.desc()).all()
    db.close()

    return [
        {
            "id": m.id,
            "message": m.message,
            "country": m.country,
            "hidden": m.hidden,
            "created_at": m.created_at,
        }
        for m in messages
    ]

# =========================
# ADMIN — HIDE MESSAGE
# =========================
@app.patch("/admin/messages/{message_id}/hide")
def hide_message(message_id: int, x_admin_token: str = Header(...)):
    check_admin(x_admin_token)

    db = SessionLocal()
    msg = db.query(Message).filter(Message.id == message_id).first()

    if not msg:
        db.close()
        raise HTTPException(status_code=404, detail="Message not found")

    msg.hidden = True
    db.commit()
    db.close()

    return {"status": "hidden"}

# =========================
# MOCK PAYMENT (NO TOCAR)
# =========================
@app.post("/payment-success")
def payment_success():
    token = str(uuid.uuid4())
    return {"token": token}

@app.post("/use-free-code")
def use_free_code(payload: dict):
    token = str(uuid.uuid4())
    return {"token": token}
