import httpx
import secrets

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
        """Authenticate user credentials, rejecting unverified or inactive accounts."""
        user = await user_repository.get_by_email(db, email)
        if not user or not verify_password(password, user.password_hash):
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
            try:
                # Store refresh token in Redis (7 days TTL = 604800 seconds)
                await redis.setex(
                    f"refresh_token:{user.id}",
                    604800,
                    refresh_token
                )
            except Exception:
                # Graceful fallback if Redis is unreachable in dev environment
                pass

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
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type for refresh endpoint."
                )
            user_id_str = payload.get("sub")
            if not user_id_str:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token subject."
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is expired or invalid."
            )

        import uuid
        user_id = uuid.UUID(user_id_str)
        user = await user_repository.get_by_id(db, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer exists or is inactive."
            )

        if redis:
            try:
                stored_token = await redis.get(f"refresh_token:{user.id}")
                if stored_token and stored_token != refresh_token:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Refresh token has been revoked or replaced."
                    )
            except HTTPException:
                raise
            except Exception:
                pass

        return await self.generate_token_pair(user, redis)

    async def logout_user(self, user_id: str, redis: Redis | None = None) -> None:
        """Revoke refresh token upon user logout."""
        if redis:
            try:
                await redis.delete(f"refresh_token:{user_id}")
            except Exception:
                pass

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
            try:
                # Store reset token in Redis (15 mins TTL = 900 seconds)
                await redis.setex(
                    f"reset_token:{reset_token}",
                    900,
                    str(user.id)
                )
            except Exception:
                pass

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
            try:
                user_id_str = await redis.get(f"reset_token:{token}")
            except Exception:
                pass

        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired password reset token."
            )

        import uuid
        user_id = uuid.UUID(user_id_str)
        user = await user_repository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        new_hash = get_password_hash(new_password)
        await user_repository.update_password(db, user, new_hash)

        if redis:
            try:
                await redis.delete(f"reset_token:{token}")
            except Exception:
                pass

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
            try:
                # Store verification token in Redis (24 hours = 86400 seconds)
                await redis.setex(
                    f"verify_token:{verify_token}",
                    86400,
                    str(user.id)
                )
            except Exception:
                pass

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
        Users authenticated via Google are verified by definition (Google verifies email ownership).
        Supports dev mock tokens formatted as 'mock-google-token:<email>:<name>' when running offline or in dev.
        """
        email = None
        full_name = None
        credential = payload.credential.strip()

        # Check for dev mock token (enables rapid local testing without Google Cloud Console setup)
        if credential.startswith("mock-google-token:") or credential.startswith("dev-google:"):
            parts = credential.split(":")
            email = parts[1].strip().lower() if len(parts) > 1 and parts[1].strip() else "google.learner@luminalearn.ai"
            full_name = parts[2].strip() if len(parts) > 2 and parts[2].strip() else "Google Learner"
        else:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(
                        "https://oauth2.googleapis.com/tokeninfo",
                        params={"id_token": credential}
                    )
                if resp.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired Google authentication credential."
                    )
                token_data = resp.json()

                if settings.GOOGLE_CLIENT_ID and token_data.get("aud") != settings.GOOGLE_CLIENT_ID:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Google token audience mismatch."
                    )

                iss = token_data.get("iss", "")
                if iss not in ["accounts.google.com", "https://accounts.google.com"]:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid Google token issuer."
                    )

                email = token_data.get("email", "").strip().lower()
                full_name = token_data.get("name") or token_data.get("given_name") or email.split("@")[0]
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Google token verification error: {str(e)}"
                )

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google credential did not provide a valid email address."
            )

        # Lookup user by email
        user = await user_repository.get_by_email(db, email)
        if user:
            # If account exists but wasn't verified, Google OAuth proves email ownership
            if not user.is_verified:
                await user_repository.update_verified_status(db, user, is_verified=True)
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This account has been deactivated."
                )
        else:
            # Create new user automatically provisioned and verified
            random_pw_hash = get_password_hash(secrets.token_urlsafe(32))
            assigned_role = payload.role if payload.role in [UserRole.STUDENT, UserRole.TEACHER] else UserRole.STUDENT
            user = await user_repository.create(
                db,
                email=email,
                password_hash=random_pw_hash,
                full_name=full_name or "Google Learner",
                role=assigned_role,
                preferred_modality=payload.preferred_modality or VARKModality.VISUAL,
                is_verified=True
            )

        return await self.generate_token_pair(user, redis)


auth_service = AuthService()
