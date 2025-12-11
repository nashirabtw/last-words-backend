from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import FastAPI, Header, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid

from backend.database import SessionLocal, engine
from backend.models import Base, Message
# ========================
# FREE CODES (VIP ACCESS)
# ========================
FREE_CODES = {
    "ST4RLI1",
    "SOL1X0",
    "STARVT9",
    "MO33ON5",
    "LIGHTRS7",
    "SKYDD9",
    "NOVIE2A2",
    "GIFT4Y8L9",
    "VI3PP8",
    "TQET5T0"
}

USED_CODES = set()

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
    latitude: float
    longitude: float

class AdminLogin(BaseModel):
    username: str
    password: str

# ========================
# HEALTH CHECK
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

    # consumir token (1 pago = 1 mensaje)
    valid_tokens.remove(x_payment_token)

    db: Session = SessionLocal()
    msg = Message(
        name=data.name,
        message=data.message,
        country=data.country,
        emoji=data.emoji,
        latitude=data.latitude,
        longitude=data.longitude
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    db.close()

    return {"status": "guardado", "id": msg.id}

# ========================
# LISTAR MENSAJES (PUBLICO)
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
            "emoji": m.emoji,
            "latitude": m.latitude,
            "longitude": m.longitude,
            "created_at": m.created_at.isoformat()
        }
        for m in messages
    ]
class CodeRequest(BaseModel):
    code: str

@app.post("/use-free-code")
def use_free_code(data: CodeRequest):
    code = data.code.strip().upper()

    # validar que existe
    if code not in FREE_CODES:
        raise HTTPException(status_code=400, detail="Invalid code")

    # validar que no esté usado
    if code in USED_CODES:
        raise HTTPException(status_code=403, detail="Code already used")

    # marcar como usado
    USED_CODES.add(code)

    # generar token de 1 uso
    token = str(uuid.uuid4())
    valid_tokens.add(token)

    return {"token": token}

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
class CodeRequest(BaseModel):
    code: str

@app.post("/use-free-code")
def use_free_code(data: CodeRequest):
    code = data.code.strip().upper()

    # verificar código válido
    if code not in FREE_CODES:
        raise HTTPException(status_code=400, detail="Invalid code")

    # verificar que no esté usado
    if code in USED_CODES:
        raise HTTPException(status_code=403, detail="Code already used")

    # marcarlo como usado
    USED_CODES.add(code)

    # generar token GRATIS de 1 uso
    token = str(uuid.uuid4())
    valid_tokens.add(token)

    return {"token": token}

# ========================
# ADMIN: LISTAR MENSAJES
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
            "emoji": m.emoji,
            "latitude": m.latitude,
            "longitude": m.longitude,
            "created_at": m.created_at.isoformat()
        }
        for m in messages
    ]

# ========================
# ADMIN: EDITAR MENSAJE
# ========================
@app.put("/edit-message/{message_id}")
def edit_message(
    message_id: int,
    data: MessageRequest = Body(...),
    x_admin_token: str = Header(None)
):
    if not x_admin_token or x_admin_token not in admin_tokens:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    db: Session = SessionLocal()
    msg = db.query(Message).filter(Message.id == message_id).first()

