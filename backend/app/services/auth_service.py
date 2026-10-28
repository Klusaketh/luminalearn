import logging
import secrets
import uuid
from collections.abc import Awaitable
from typing import Any

import jwt
from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User, UserRole, VARKModality
from app.repositories.user_repository import user_repository
from app.schemas.auth import (
    GoogleAuthRequest,
    StudentRegisterRequest,
    TeacherRegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse
from app.services.email_service import email_service
from app.services.otp_service import otp_service

logger = logging.getLogger(__name__)


async def _cache_best_effort(operation: Awaitable[Any], action: str) -> Any:
    """Token cache I/O is best-effort: a cache outage must never block signing in or out."""
    try:
        return await operation
    except Exception as exc:  # noqa: BLE001 - any cache/transport failure degrades gracefully
        logger.warning("Token cache unavailable while trying to %s: %s", action, exc)
        return None


class AuthService:
    """Authentication Domain Service managing user identity and tokens."""

    async def register_student(
        self,
        db: AsyncSession,
        payload: StudentRegisterRequest,
        redis: Redis | None = None
    ) -> User:
        """Register a new student account as unverified and dispatch verification OTP."""
        existing_user = await user_repository.get_by_email(db, payload.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists."
            )

        hashed_password = get_password_hash(payload.password)
        user = await user_repository.create(
            db,
            email=payload.email,
            password_hash=hashed_password,
            full_name=payload.full_name,
            role=UserRole.STUDENT,
            preferred_modality=payload.preferred_modality,
            is_verified=False
        )

        if redis is not None:
            otp = await otp_service.generate_and_store_otp(user.email, redis)
            await email_service.send_otp_email(user.email, otp, user.full_name)

        return user

    async def register_teacher(
        self,
        db: AsyncSession,
        payload: TeacherRegisterRequest,
        redis: Redis | None = None
    ) -> User:
        """Register a new teacher account as unverified and dispatch verification OTP."""
        existing_user = await user_repository.get_by_email(db, payload.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists."
            )

        hashed_password = get_password_hash(payload.password)
        user = await user_repository.create(
            db,
            email=payload.email,
            password_hash=hashed_password,
            full_name=payload.full_name,
            role=UserRole.TEACHER,
            preferred_modality=VARKModality.VISUAL,
            is_verified=False
        )

        if redis is not None:
            otp = await otp_service.generate_and_store_otp(user.email, redis)
            await email_service.send_otp_email(user.email, otp, user.full_name)

        return user

    async def authenticate_user(
        self,
        db: AsyncSession,
        email: str,
        password: str
    ) -> User:
        """Authenticate user credentials, rejecting unverified, inactive, or Google-only accounts."""
        user = await user_repository.get_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Check if account was created via Google Sign-In and lacks a local password
        if user.password_hash.startswith("!google_oauth_only_"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This account was created via Google Sign-In. Please click 'Continue with Google', or reset your password if you wish to use password login."
            )

        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive. Please contact system support."
            )
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="EMAIL_VERIFICATION_REQUIRED"
            )
        return user

    async def generate_token_pair(
        self,
        user: User,
        redis: Redis | None = None
    ) -> TokenResponse:
        """Generate Access and Refresh Token pair for user, saving refresh token in Redis."""
        access_token = create_access_token(subject=str(user.id), role=user.role.value)
        refresh_token = create_refresh_token(subject=str(user.id))

        if redis:
            # Store refresh token in Redis (7 days TTL = 604800 seconds)
            await _cache_best_effort(
                redis.setex(f"refresh_token:{user.id}", 604800, refresh_token),
                "store the refresh token",
            )

        user_response = UserResponse.model_validate(user)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=user_response
        )

    async def refresh_tokens(
        self,
        db: AsyncSession,
        refresh_token: str,
        redis: Redis | None = None
    ) -> TokenResponse:
        """Validate Refresh Token and issue a new token pair."""
        invalid = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is expired or invalid."
        )
        try:
            payload = decode_token(refresh_token)
        except jwt.PyJWTError:
            raise invalid from None
        if payload.get("type") != "refresh" or not payload.get("sub"):
            raise invalid
        try:
            user_id = uuid.UUID(str(payload["sub"]))
        except ValueError:
            raise invalid from None
        user = await user_repository.get_by_id(db, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer exists or is inactive."
            )

        if redis:
            stored_token = await _cache_best_effort(redis.get(f"refresh_token:{user.id}"), "read the refresh token")
            if stored_token and stored_token != refresh_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token has been revoked or replaced."
                )

        return await self.generate_token_pair(user, redis)

    async def logout_user(self, user_id: str, redis: Redis | None = None) -> None:
        """Revoke refresh token upon user logout."""
        if redis:
            await _cache_best_effort(redis.delete(f"refresh_token:{user_id}"), "revoke the refresh token")

    async def request_password_reset(
        self,
        db: AsyncSession,
        email: str,
        redis: Redis | None = None
    ) -> str:
        """Generate a password reset token for the given email."""
        user = await user_repository.get_by_email(db, email)
        if not user:
            # Return generic success to avoid email enumeration
            return "If an account exists with that email, a password reset link has been issued."

        reset_token = secrets.token_urlsafe(32)
        if redis:
            # Store reset token in Redis (15 mins TTL = 900 seconds)
            await _cache_best_effort(
                redis.setex(f"reset_token:{reset_token}", 900, str(user.id)),
                "store the password reset token",
            )

        return reset_token

    async def reset_password(
        self,
        db: AsyncSession,
        token: str,
        new_password: str,
        redis: Redis | None = None
    ) -> None:
        """Reset password using reset token."""
        user_id_str = None
        if redis:
            user_id_str = await _cache_best_effort(redis.get(f"reset_token:{token}"), "read the password reset token")

        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired password reset token."
            )

        user_id = uuid.UUID(str(user_id_str))
        user = await user_repository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        new_hash = get_password_hash(new_password)
        await user_repository.update_password(db, user, new_hash)

        if redis:
            await _cache_best_effort(redis.delete(f"reset_token:{token}"), "spend the password reset token")

    async def request_email_verification(
        self,
        db: AsyncSession,
        email: str,
        redis: Redis | None = None
    ) -> str:
        """Structure for issuing email verification token."""
        user = await user_repository.get_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No account registered with this email."
            )

        verify_token = secrets.token_urlsafe(32)
        if redis:
            # Store verification token in Redis (24 hours = 86400 seconds)
            await _cache_best_effort(
                redis.setex(f"verify_token:{verify_token}", 86400, str(user.id)),
                "store the email verification token",
            )

        return verify_token

    async def verify_email_otp(
        self,
        db: AsyncSession,
        email: str,
        otp: str,
        redis: Redis
    ) -> bool:
        """
        Verify user email using 6-digit OTP.
        On success, marks is_verified=True, invalidates OTP state, and returns True.
        """
        user = await user_repository.get_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User account not found."
            )

        if user.is_verified:
            # Already verified, safely invalidate any residual OTP state
            await otp_service.invalidate_otp(user.email, redis)
            return True

        # Verify candidate OTP (enforces 10m expiry and 5 attempts limit)
        await otp_service.verify_otp(user.email, otp, redis)

        # Mark user as verified and commit to DB
        await user_repository.update_verified_status(db, user, is_verified=True)
        return True

    async def resend_email_otp(
        self,
        db: AsyncSession,
        email: str,
        redis: Redis
    ) -> None:
        """
        Resend verification OTP.
        Enforces 60-second cooldown, invalidates old OTP, dispatches email.
        Never returns the OTP in response.
        """
        user = await user_repository.get_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User account not found."
            )

        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address is already verified."
            )

        # Generate fresh OTP and store keyed HMAC (enforces 60s cooldown, invalidates previous OTP)
        otp = await otp_service.generate_and_store_otp(user.email, redis, is_resend=True)

        # Dispatch via email service
        await email_service.send_otp_email(user.email, otp, user.full_name)

    async def authenticate_or_register_google_user(
        self,
        db: AsyncSession,
        payload: GoogleAuthRequest,
        redis: Redis | None = None
    ) -> TokenResponse:
        """
        Authenticate or register a user via Google OAuth2 (Google Identity Services).
        Uses official google.oauth2.id_token.verify_oauth2_token() with strict validation
        of signature, audience, issuer, expiration, and email_verified claim.
        Fail closed: Mock tokens are strictly rejected in non-development environments.
        """
        email: str | None = None
        full_name: str | None = None
        credential = payload.credential.strip()

        if not credential:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Google authentication credential."
            )

        # Check for development mock token (strictly gated behind ENVIRONMENT == 'development' AND DEBUG == True)
        is_mock_token = credential.startswith(("mock-google-token:", "dev-google:"))
        if is_mock_token:
            if settings.ENVIRONMENT != "development" or not settings.DEBUG:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Development mock tokens are strictly forbidden in this environment."
                )
            parts = credential.split(":")
            email = parts[1].strip().lower() if len(parts) > 1 and parts[1].strip() else "google.learner@luminalearn.ai"
            full_name = parts[2].strip() if len(parts) > 2 and parts[2].strip() else "Google Learner"
        else:
            # Cryptographic verification using official Google Auth library
            from google.auth import exceptions as google_auth_exceptions
            from google.auth.transport import requests as google_requests
            from google.oauth2 import id_token as google_id_token

            client_id = settings.GOOGLE_CLIENT_ID
            if not client_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Google Client ID is not configured on this server."
                )

            try:
                # verify_oauth2_token validates signature against Google certs, exp, iss, and aud
                id_info = google_id_token.verify_oauth2_token(
                    credential,
                    google_requests.Request(),
                    audience=client_id,
                    clock_skew_in_seconds=10
                )
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid Google ID token: {e!s}"
                )
            except google_auth_exceptions.GoogleAuthError as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Google token verification failed: {e!s}"
                ) from e

            # Strict issuer check
            issuer = id_info.get("iss", "")
            if issuer not in ["accounts.google.com", "https://accounts.google.com"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google token issuer."
                )

            # Enforce that Google confirms email ownership
            if not id_info.get("email_verified", False):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Google account email address is not verified by Google."
                )

            email = id_info.get("email", "").strip().lower()
            full_name = id_info.get("name") or id_info.get("given_name") or (email.split("@")[0] if email else "Google Learner")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google credential did not provide a valid email address."
            )

        # Lookup user by verified email
        user = await user_repository.get_by_email(db, email)
        if user:
            # Account exists: Google OAuth confirms ownership of the email.
            # Preserve existing user.id, user.role, onboarding profile, and learning progress.
            if not user.is_verified:
                await user_repository.update_verified_status(db, user, is_verified=True)
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This account has been deactivated."
                )
        else:
            # Create new user automatically verified.
            # Assign sentinel password hash that cannot be matched by any plain password.
            google_password_sentinel = f"!google_oauth_only_{secrets.token_urlsafe(32)}"
            # Never trust client-supplied admin role; restrict to student or teacher
            assigned_role = payload.role if payload.role in [UserRole.STUDENT, UserRole.TEACHER] else UserRole.STUDENT
            user = await user_repository.create(
                db,
                email=email,
                password_hash=google_password_sentinel,
                full_name=full_name or "Google Learner",
                role=assigned_role,
                preferred_modality=payload.preferred_modality or VARKModality.VISUAL,
                is_verified=True
            )

        return await self.generate_token_pair(user, redis)


auth_service = AuthService()

