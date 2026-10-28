
from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole, VARKModality
from app.schemas.user import UserResponse


class GoogleAuthRequest(BaseModel):
    credential: str = Field(..., description="Google ID Token from Google Identity Services or Dev Mock")
    role: UserRole = Field(default=UserRole.STUDENT, description="Target role if a new account is registered")
    preferred_modality: VARKModality | None = Field(default=VARKModality.VISUAL, description="Initial VARK modality")


class StudentRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    full_name: str = Field(..., min_length=2, max_length=255)
    preferred_modality: VARKModality = VARKModality.VISUAL


class TeacherRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    full_name: str = Field(..., min_length=2, max_length=255)
    department: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")


class EmailVerificationRequest(BaseModel):
    email: EmailStr


class EmailVerificationConfirmRequest(BaseModel):
    token: str


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., pattern=r"^\d{6}$", description="Exactly 6 numeric digits")


class ResendOTPRequest(BaseModel):
    email: EmailStr


class MessageResponse(BaseModel):
    message: str
    detail: str | None = None
