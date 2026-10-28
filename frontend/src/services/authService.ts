// Auth requests carry their own credentials and must never trigger a token refresh (auth: false).
import { API_BASE, apiFetch, readErrorDetail } from "./apiClient";

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  role: "student" | "teacher" | "admin" | "parent";
  preferred_modality: "visual" | "auditory" | "read_write" | "kinesthetic";
  is_active: boolean;
  is_verified?: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: UserResponse;
}

export interface MessageResponse {
  message: string;
  detail?: string;
}

export interface StudentRegisterPayload {
  email: string;
  password: string;
  full_name: string;
  preferred_modality?: "visual" | "auditory" | "read_write" | "kinesthetic";
}

export interface TeacherRegisterPayload {
  email: string;
  password: string;
  full_name: string;
  department?: string;
}

class AuthService {
  private getHeaders(token?: string): HeadersInit {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  }

  async login(email: string, password: string): Promise<TokenResponse> {
    const res = await apiFetch(`${API_BASE}/auth/login`, {
      auth: false,
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      throw new Error(await readErrorDetail(res, "Invalid email or password."));
    }

    return res.json();
  }

  async loginWithGoogle(
    credential: string,
    role: "student" | "teacher" = "student",
    preferredModality?: "visual" | "auditory" | "read_write" | "kinesthetic"
  ): Promise<TokenResponse> {
    const res = await apiFetch(`${API_BASE}/auth/google`, {
      auth: false,
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({
        credential,
        role,
        preferred_modality: preferredModality || "visual",
      }),
    });

    if (!res.ok) {
      throw new Error(await readErrorDetail(res, "Google authentication failed."));
    }

    return res.json();
  }

  async registerStudent(payload: StudentRegisterPayload): Promise<UserResponse> {
    const res = await apiFetch(`${API_BASE}/auth/register/student`, {
      auth: false,
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error(await readErrorDetail(res, "Student registration failed."));
    }

    return res.json();
  }

  async registerTeacher(payload: TeacherRegisterPayload): Promise<UserResponse> {
    const res = await apiFetch(`${API_BASE}/auth/register/teacher`, {
      auth: false,
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error(await readErrorDetail(res, "Teacher registration failed."));
    }

    return res.json();
  }

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const res = await apiFetch(`${API_BASE}/auth/refresh`, {
      auth: false,
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!res.ok) {
      throw new Error(await readErrorDetail(res, "Session expired. Please log in again."));
    }

    return res.json();
  }

  async logout(token: string): Promise<MessageResponse> {
    const res = await apiFetch(`${API_BASE}/auth/logout`, {
      auth: false,
      method: "POST",
      headers: this.getHeaders(token),
    });

    if (!res.ok) {
      return { message: "Logged out locally." };
    }

    return res.json();
  }

  async getMe(token: string): Promise<UserResponse> {
    const res = await apiFetch(`${API_BASE}/auth/me`, {
      auth: false,
      method: "GET",
      headers: this.getHeaders(token),
    });

    if (!res.ok) {
      throw new Error(await readErrorDetail(res, "Unauthorized."));
    }

    return res.json();
  }

  async forgotPassword(email: string): Promise<MessageResponse> {
    const res = await apiFetch(`${API_BASE}/auth/forgot-password`, {
      auth: false,
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ email }),
    });

    if (!res.ok) {
      throw new Error(await readErrorDetail(res, "Failed to process forgot password request."));
    }

    return res.json();
  }

  async resetPassword(token: string, new_password: string): Promise<MessageResponse> {
    const res = await apiFetch(`${API_BASE}/auth/reset-password`, {
      auth: false,
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ token, new_password }),
    });

    if (!res.ok) {
      throw new Error(await readErrorDetail(res, "Failed to reset password."));
    }

    return res.json();
  }

  async verifyEmail(email: string, otp: string): Promise<MessageResponse> {
    const res = await apiFetch(`${API_BASE}/auth/verify-email`, {
      auth: false,
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ email, otp }),
    });

    if (!res.ok) {
      throw new Error(await readErrorDetail(res, "Failed to verify email code."));
    }

    return res.json();
  }

  async resendOTP(email: string): Promise<MessageResponse> {
    const res = await apiFetch(`${API_BASE}/auth/verify-email/resend`, {
      auth: false,
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ email }),
    });

    if (!res.ok) {
      throw new Error(await readErrorDetail(res, "Failed to resend verification code."));
    }

    return res.json();
  }

  async requestVerifyEmail(email: string): Promise<MessageResponse> {
    return this.resendOTP(email);
  }

  async confirmVerifyEmail(token: string): Promise<MessageResponse> {
    const res = await apiFetch(`${API_BASE}/auth/verify-email/confirm`, {
      auth: false,
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ token }),
    });

    if (!res.ok) {
      throw new Error(await readErrorDetail(res, "Failed to confirm email verification."));
    }

    return res.json();
  }
}

export const authService = new AuthService();
