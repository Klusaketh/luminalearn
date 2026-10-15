"""
Security & Cryptography helper module.
Standardized password hashing using Argon2 and JWT creation/verification routines.
"""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password Cryptography Context (Argon2id with bcrypt fallback)
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def generate_secure_otp() -> str:
    """
    Generate an exactly 6-digit cryptographically secure OTP string using secrets.
    secrets.randbelow(1_000_000) generates an integer from 0 to 999,999 uniformly,
    and :06d formatting ensures leading zeros are preserved.
    """
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(email: str, otp: str) -> str:
    """
    Compute keyed HMAC-SHA256 digest of normalized email and OTP.
    Ensures OTP is not stored plaintext and avoids raw SHA256 rainbow attacks.
    """
    message = f"{email.strip().lower()}:{otp.strip()}".encode()
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        message,
        hashlib.sha256
    ).hexdigest()


def verify_otp_hash(email: str, candidate_otp: str, stored_hash: str) -> bool:
    """
    Constant-time comparison of candidate OTP keyed HMAC digest against stored digest.
    Protects against timing attacks.
    """
    candidate_hash = hash_otp(email, candidate_otp)
    return hmac.compare_digest(candidate_hash, stored_hash)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password."""
    return bool(pwd_context.verify(plain_password, hashed_password))


def get_password_hash(password: str) -> str:
    """Generate Argon2 hash of plain password."""
    return str(pwd_context.hash(password))


def create_access_token(
    subject: str | Any,
    role: str = "student",
    expires_delta: timedelta | None = None
) -> str:
    """Generate signed JWT Access Token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(subject),
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    subject: str | Any,
    expires_delta: timedelta | None = None
) -> str:
    """Generate signed JWT Refresh Token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "sub": str(subject),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT payload.
    Raises jwt.PyJWTError if invalid or expired.
    """
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )
