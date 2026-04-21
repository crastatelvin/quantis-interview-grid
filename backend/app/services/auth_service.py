from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from passlib.context import CryptContext
from sqlalchemy import select

from backend.app.config import settings
from backend.app.db import SessionLocal
from backend.app.models import UserModel

pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class AuthService:
    def register(self, email: str, password: str) -> dict:
        email_norm = email.strip().lower()
        with SessionLocal() as db:
            exists = db.execute(select(UserModel).where(UserModel.email == email_norm)).scalar_one_or_none()
            if exists:
                raise ValueError("Email already exists")
            user = UserModel(
                id=f"user_{uuid4().hex[:16]}",
                email=email_norm,
                password_hash=pwd.hash(password),
                created_at=datetime.now(timezone.utc),
            )
            db.add(user)
            db.commit()
            return {"id": user.id, "email": user.email}

    def login(self, email: str, password: str) -> str:
        email_norm = email.strip().lower()
        with SessionLocal() as db:
            user = db.execute(select(UserModel).where(UserModel.email == email_norm)).scalar_one_or_none()
            if not user or not pwd.verify(password, user.password_hash):
                raise ValueError("Invalid credentials")
            payload = {
                "sub": user.id,
                "email": user.email,
                "exp": datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expire_hours),
            }
            return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

    def decode_token(self, token: str) -> dict:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])

