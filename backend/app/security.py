"""Password hashing and short-lived signed bearer tokens."""
import base64
import binascii
import hashlib
import hmac
import json
import os
import secrets
import time

from fastapi import Header

from .public import PartnerError

TOKEN_SECONDS = 3600


def token_secret():
    value = os.getenv("COURTSLOT_TOKEN_SECRET", "")
    if len(value) < 32:
        raise PartnerError(503, "SOURCE_UNAVAILABLE", "Autentikasi belum dikonfigurasi.")
    return value.encode()


def encode_bytes(value):
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def decode_bytes(value):
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600_000)
    return f"pbkdf2_sha256$600000${encode_bytes(salt)}${encode_bytes(digest)}"


def verify_password(password, stored):
    try:
        _, rounds, salt, digest = stored.split("$")
        computed = hashlib.pbkdf2_hmac("sha256", password.encode(), decode_bytes(salt), int(rounds))
        return hmac.compare_digest(computed, decode_bytes(digest))
    except (ValueError, TypeError):
        return False


def create_token(user_id):
    header = encode_bytes(b'{"alg":"HS256","typ":"JWT"}')
    payload = encode_bytes(json.dumps({"sub": user_id, "exp": int(time.time()) + TOKEN_SECONDS}, separators=(",", ":")).encode())
    content = f"{header}.{payload}"
    signature = encode_bytes(hmac.new(token_secret(), content.encode(), hashlib.sha256).digest())
    return f"{content}.{signature}"


def current_user(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise PartnerError(401, "UNAUTHORIZED", "Login diperlukan.")
    token = authorization[7:]
    try:
        header, payload, signature = token.split(".")
        content = f"{header}.{payload}"
        expected = hmac.new(token_secret(), content.encode(), hashlib.sha256).digest()
        claims = json.loads(decode_bytes(payload))
        if not hmac.compare_digest(expected, decode_bytes(signature)) or claims["exp"] <= time.time() or not isinstance(claims["sub"], str):
            raise ValueError()
        return claims["sub"]
    except (ValueError, KeyError, TypeError, UnicodeError, binascii.Error):
        raise PartnerError(401, "UNAUTHORIZED", "Sesi tidak valid atau kedaluwarsa.")
