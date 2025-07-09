import jwt
from passlib.context import CryptContext
from fastapi import Request
from jwt import ExpiredSignatureError, InvalidTokenError

SECRET_KEY = "supersecret"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_token(user_id):
    return jwt.encode({"user_id": user_id}, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except (ExpiredSignatureError, InvalidTokenError):
        return None

def get_current_user(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    token = auth.split(" ")[1]
    payload = decode_token(token)
    return payload.get("user_id") if payload else None