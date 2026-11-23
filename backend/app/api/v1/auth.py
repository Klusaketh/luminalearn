from typing import Any

from fastapi import APIRouter, Depends, Response, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db, get_redis
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import (
    EmailVerificationRequest,
    ForgotPasswordRequest,
    GoogleAuthRequest,
    LoginRequest,
    MessageResponse,
    OTPDelivery,
    OTPDeliveryResponse,
    RefreshTokenRequest,
    RegisterResponse,
    ResendOTPRequest,
    ResetPasswordRequest,
    StudentRegisterRequest,
    TeacherRegisterRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.schemas.user import UserResponse
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

_EMAIL_NOT_SET_UP = (
    "Email isn't set up on this server. In development, the code is printed in the "
    "terminal running the API."
)
_SEND_FAILED = "We couldn't send the email. Try Resend in a minute."


def _verification_message(delivery: OTPDelivery) -> str:
    return {
        "email": "Verification code sent to your email address.",
        "console": _EMAIL_NOT_SET_UP,
        "failed": _SEND_FAILED,
    }[delivery]


def _registered(user: User, delivery: OTPDelivery) -> RegisterResponse:
    return RegisterResponse(**UserResponse.model_validate(user).model_dump(), otp_delivery=delivery)


@router.post(
    "/register/student",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Student Account"
)
async def register_student(
    payload: StudentRegisterRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> Any:
    """Register a new student account as unverified and dispatch verification OTP."""
    user, delivery = await auth_service.register_student(db, payload, redis)
    return _registered(user, delivery)


@router.post(
    "/register/teacher",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Teacher Account"
)
async def register_teacher(
    payload: TeacherRegisterRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> Any:
    """Register a new teacher account as unverified and dispatch verification OTP."""
    user, delivery = await auth_service.register_teacher(db, payload, redis)
    return _registered(user, delivery)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Secure Login (Students, Teachers, Admins)"
)
async def login(
    payload: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> Any:
    """Authenticate user credentials and issue Access & Refresh Token pair."""
    user = await auth_service.authenticate_user(db, payload.email, payload.password)
    token_pair = await auth_service.generate_token_pair(user, redis)

    # Set HTTP-Only Cookie for web clients
    response.set_cookie(
        key="access_token",
        value=token_pair.access_token,
        httponly=True,
        samesite="lax",
        secure=(settings.ENVIRONMENT == "production"),
        max_age=15 * 60
    )
    return token_pair


@router.post(
    "/google",
    response_model=TokenResponse,
    summary="Google OAuth2 Sign In / Sign Up"
)
async def google_auth(
    payload: GoogleAuthRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> Any:
    """Authenticate or register a user via Google OAuth2 credential (Google Identity Services)."""
    token_pair = await auth_service.authenticate_or_register_google_user(db, payload, redis)

    # Set HTTP-Only Cookie for web clients
    response.set_cookie(
        key="access_token",
        value=token_pair.access_token,
        httponly=True,
        samesite="lax",
        secure=(settings.ENVIRONMENT == "production"),
        max_age=15 * 60
    )
    return token_pair


@router.post(

    "/refresh",
    response_model=TokenResponse,
    summary="Refresh Access Token"
)
async def refresh_token(
    payload: RefreshTokenRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> Any:
    """Issue a new Access Token using a valid Refresh Token."""
    token_pair = await auth_service.refresh_tokens(db, payload.refresh_token, redis)
    response.set_cookie(
        key="access_token",
        value=token_pair.access_token,
        httponly=True,
        samesite="lax",
        secure=(settings.ENVIRONMENT == "production"),
        max_age=15 * 60
    )
    return token_pair


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="User Logout"
)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_active_user),
    redis: Redis = Depends(get_redis)
) -> Any:
    """Revoke user refresh tokens and clear auth cookie."""
    await auth_service.logout_user(str(current_user.id), redis)
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=(settings.ENVIRONMENT == "production")
    )
    return MessageResponse(message="Successfully logged out.")


@router.post(
    "/forgot-password",
    response_model=OTPDeliveryResponse,
    summary="Email a Password Reset Code"
)
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> Any:
    """Email a 6-digit reset code. The code is never part of the response."""
    delivery = await auth_service.request_password_reset(db, payload.email, redis)
    message = {
        "email": "If an account exists for this email, a reset code has been sent to it.",
        "console": _EMAIL_NOT_SET_UP,
        "failed": _SEND_FAILED,
    }[delivery]
    return OTPDeliveryResponse(message=message, otp_delivery=delivery)


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset Password with the Emailed Code"
)
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> Any:
    """Set a new password using the 6-digit code from the reset email."""
    await auth_service.reset_password(db, payload.email, payload.otp, payload.new_password, redis)
    return MessageResponse(message="Password reset successfully. You may now log in with your new password.")


@router.post(
    "/verify-email",
    response_model=MessageResponse,
    summary="Verify Email Address with 6-Digit OTP"
)
async def verify_email(
    payload: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> Any:
    """Verify user account with 6-digit OTP."""
    await auth_service.verify_email_otp(db, payload.email, payload.otp, redis)
    return MessageResponse(message="Email address verified successfully.")


@router.post(
    "/verify-email/confirm",
    response_model=MessageResponse,
    summary="Confirm Email Verification (OTP)"
)
async def confirm_verify_email(
    payload: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> Any:
    """Confirm email verification with 6-digit OTP."""
    await auth_service.verify_email_otp(db, payload.email, payload.otp, redis)
    return MessageResponse(message="Email address verified successfully.")


@router.post(
    "/verify-email/resend",
    response_model=OTPDeliveryResponse,
    summary="Resend Verification OTP"
)
async def resend_verify_email(
    payload: ResendOTPRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> Any:
    """Resend 6-digit verification code with 60-second cooldown."""
    delivery = await auth_service.resend_email_otp(db, payload.email, redis)
    return OTPDeliveryResponse(message=_verification_message(delivery), otp_delivery=delivery)


@router.post(
    "/verify-email/request",
    response_model=OTPDeliveryResponse,
    summary="Request Email Verification OTP"
)
async def request_verify_email(
    payload: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> Any:
    """Request a fresh email verification code without exposing OTP in response."""
    delivery = await auth_service.resend_email_otp(db, payload.email, redis)
    return OTPDeliveryResponse(message=_verification_message(delivery), otp_delivery=delivery)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Authenticated User Profile"
)
async def get_me(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Fetch profile of currently logged-in user."""
    return current_user
