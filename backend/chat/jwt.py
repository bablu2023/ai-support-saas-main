import jwt
from django.conf import settings
from datetime import datetime, timedelta


def create_jwt(payload, expires_minutes=60):
    payload = payload.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=expires_minutes)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_jwt(token):
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=["HS256"],
    )
