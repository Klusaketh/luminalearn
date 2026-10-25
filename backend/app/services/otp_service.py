"""
Secure OTP Management Service for LuminaLearn AI.
Handles 6-digit generation, keyed HMAC verification, 10-minute expiry,
5-attempt brute-force protection, 60-second resend cooldown, and state invalidation.
"""
import json
import logging
import time
from typing import Any

from fastapi import HTTPException, status

from app.core.security import generate_secure_otp, hash_otp, verify_otp_hash

logger = logging.getLogger(__name__)

OTP_EXPIRY_SECONDS = 600       # Exactly 10 minutes
MAX_FAILED_ATTEMPTS = 5        # Maximum 5 failed attempts allowed
RESEND_COOLDOWN_SECONDS = 60   # 60 seconds resend cooldown


class OTPService:
    """Service managing cryptographically secure OTP state in Redis."""

    def _get_key(self, email: str) -> str:
        return f"otp:{email.strip().lower()}"

    async def get_otp_raw_state(self, email: str, redis: Any) -> dict[str, Any] | None:
        """Utility for inspection in tests (raw state in Redis)."""
        key = self._get_key(email)
        raw = await redis.get(key)
        if not raw:
            return None
        try:
            val = json.loads(raw)
            return val if isinstance(val, dict) else None
        except (ValueError, TypeError):
            return None

    async def generate_and_store_otp(
        self,
        email: str,
        redis: Any,
        is_resend: bool = False,
    ) -> str:
        """
        Generate a secure 6-digit OTP and store its keyed HMAC in Redis.
        Enforces 60-second cooldown on resend.
        Invalidates any previous OTP (overwriting state).
        Returns the raw OTP string for email dispatch only.
        """
        key = self._get_key(email)
        now = time.time()

        # Check existing state for resend cooldown
        existing_raw = await redis.get(key)
        if existing_raw:
            try:
                existing_data = json.loads(existing_raw)
                last_sent_at = float(existing_data.get("last_sent_at", 0))
                elapsed = now - last_sent_at
                if is_resend and elapsed < RESEND_COOLDOWN_SECONDS:
                    cooldown_remaining = int(RESEND_COOLDOWN_SECONDS - elapsed)
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Please wait {cooldown_remaining} seconds before requesting a new code.",
                    )
            except HTTPException:
                raise
            except (ValueError, TypeError, AttributeError) as exc:
                # Corrupted or foreign state: overwrite it with a fresh OTP below.
                logger.warning("Failed to decode previous OTP state: %s", exc)

        # 1. Generate cryptographically secure 6-digit OTP
        otp = generate_secure_otp()

        # 2. Compute keyed HMAC (never store plaintext OTP)
        otp_hmac = hash_otp(email, otp)

        # 3. Create fresh state (invalidating previous OTP)
        state_payload = {
            "otp_hash": otp_hmac,
            "attempts": 0,
            "created_at": now,
            "last_sent_at": now,
        }

        # 4. Store in Redis with exactly 10 minutes (600s) TTL
        await redis.setex(key, OTP_EXPIRY_SECONDS, json.dumps(state_payload))
        logger.info("New secure OTP state generated and stored for %s", email)

        return otp

    async def verify_otp(
        self,
        email: str,
        candidate_otp: str,
        redis: Any,
    ) -> bool:
        """
        Verify candidate 6-digit OTP against stored keyed HMAC.
        Enforces 10-minute expiry and max 5 failed attempts limit.
        On success, invalidates all OTP state.
        """
        key = self._get_key(email)
        now = time.time()

        raw_state = await redis.get(key)
        if not raw_state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired or does not exist. Please request a new code.",
            )

        try:
            state = json.loads(raw_state)
            if not isinstance(state, dict):
                raise TypeError("OTP state must be a JSON object.")
        except (ValueError, TypeError):
            await redis.delete(key)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Corrupted verification state. Please request a new code.",
            ) from None

        # Check expiration
        created_at = float(state.get("created_at", 0))
        if (now - created_at) > OTP_EXPIRY_SECONDS:
            await redis.delete(key)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired. Please request a new code.",
            )

        # Check maximum attempts exceeded
        attempts = int(state.get("attempts", 0))
        if attempts >= MAX_FAILED_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum verification attempts exceeded. Please request a new code.",
            )

        # Constant-time comparison against keyed HMAC
        stored_hash = state.get("otp_hash", "")
        is_valid = verify_otp_hash(email, candidate_otp, stored_hash)

        if not is_valid:
            attempts += 1
            state["attempts"] = attempts
            remaining_attempts = MAX_FAILED_ATTEMPTS - attempts

            remaining_ttl = max(1, int(OTP_EXPIRY_SECONDS - (now - created_at)))
            await redis.setex(key, remaining_ttl, json.dumps(state))

            if attempts >= MAX_FAILED_ATTEMPTS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Maximum verification attempts exceeded. Please request a new code.",
                )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid verification code. {remaining_attempts} attempt{'s' if remaining_attempts > 1 else ''} remaining.",
            )

        # Successful verification: invalidate all OTP state
        await redis.delete(key)
        logger.info("OTP successfully verified and invalidated for %s", email)
        return True

    async def invalidate_otp(self, email: str, redis: Any) -> None:
        """Explicitly invalidate any OTP state for email."""
        key = self._get_key(email)
        await redis.delete(key)


otp_service = OTPService()
