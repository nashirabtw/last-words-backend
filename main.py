from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid

from database import SessionLocal, engine
from models import Base, Message

# ========================
# APP
# ========================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # solo para desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# DB
# ========================
Base.metadata.create_all(bind=engine)

# ========================
# TOKENS
# ========================
valid_tokens = set()
admin_tokens = {}

# ========================
# MODELOS
# ========================
class MessageRequest(BaseModel):
    name: str
    message: str
    country: str
    emoji: str

class AdminLogin(BaseModel):
    username: str
    password: str

# ========================
# HEALTH
# ========================
@app.get("/")
def home():
    return {"status": "API funcionando"}

# ========================
# PAGO → TOKEN
# ========================
@app.post("/payment-success")
def payment_success():
    token = str(uuid.uuid4())
    valid_tokens.add(token)
    return {"token": token}

# ========================
# ENVIAR MENSAJE
# ========================
@app.post("/send-message")
def send_message(
    data: MessageRequest,
    x_payment_token: str = Header(None)
):
    if not x_payment_token or x_payment_token not in valid_tokens:
        raise HTTPException(status_code=403, detail="Pago requerido")

    # consumir token
    valid_tokens.remove(x_payment_token)

    db: Session = SessionLocal()
    msg = Message(
        name=data.name,
        message=data.message,
        country=data.country,
        emoji=data.emoji
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    db.close()

    return {"status": "guardado", "id": msg.id}

# ========================
# LISTAR MENSAJES
# ========================
@app.get("/messages")
def get_messages():
    db: Session = SessionLocal()
    messages = db.query(Message).all()
    db.close()

    return [
        {
            "id": m.id,
            "name": m.name,
            "message": m.message,
            "country": m.country,
            "emoji": m.emoji
        }
        for m in messages
    ]

# ========================
# ADMIN LOGIN
# ========================
ADMIN_USER = "admin"
ADMIN_PASSWORD = "issas_admin_2025"

@app.post("/admin/login")
def admin_login(data: AdminLogin):
    if data.username != ADMIN_USER or data.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    token = str(uuid.uuid4())
    admin_tokens[token] = True
    return {"admin_token": token}

# ========================
# ADMIN: VER MENSAJES
# ========================
@app.get("/admin/messages")
def admin_messages(x_admin_token: str = Header(None)):
    if not x_admin_token or x_admin_token not in admin_tokens:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    db: Session = SessionLocal()
    messages = db.query(Message).all()
    db.close()

    return [
        {
            "id": m.id,
            "name": m.name,
            "message": m.message,
            "country": m.country,
            "emoji": m.emoji
        }
        for m in messages
    ]
