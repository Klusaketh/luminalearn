const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

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
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Login failed." }));
      throw new Error(err.detail || "Invalid email or password.");
    }

    return res.json();
  }

  async loginWithGoogle(
    credential: string,
    role: "student" | "teacher" = "student",
    preferredModality?: "visual" | "auditory" | "read_write" | "kinesthetic"
  ): Promise<TokenResponse> {
    const res = await fetch(`${API_BASE}/auth/google`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({
        credential,
        role,
        preferred_modality: preferredModality || "visual",
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Google authentication failed." }));
      throw new Error(err.detail || "Google authentication failed.");
    }

    return res.json();
  }

  async registerStudent(payload: StudentRegisterPayload): Promise<UserResponse> {
    const res = await fetch(`${API_BASE}/auth/register/student`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Registration failed." }));
      throw new Error(err.detail || "Student registration failed.");
    }

    return res.json();
  }

  async registerTeacher(payload: TeacherRegisterPayload): Promise<UserResponse> {
    const res = await fetch(`${API_BASE}/auth/register/teacher`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Registration failed." }));
      throw new Error(err.detail || "Teacher registration failed.");
    }

    return res.json();
  }

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const res = await fetch(`${API_BASE}/auth/refresh`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Token refresh failed." }));
      throw new Error(err.detail || "Session expired. Please log in again.");
    }

    return res.json();
  }

  async logout(token: string): Promise<MessageResponse> {
    const res = await fetch(`${API_BASE}/auth/logout`, {
      method: "POST",
      headers: this.getHeaders(token),
    });

    if (!res.ok) {
      return { message: "Logged out locally." };
    }

    return res.json();
  }

  async getMe(token: string): Promise<UserResponse> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      method: "GET",
      headers: this.getHeaders(token),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Failed to fetch user." }));
      throw new Error(err.detail || "Unauthorized.");
    }

    return res.json();
  }

  async forgotPassword(email: string): Promise<MessageResponse> {
    const res = await fetch(`${API_BASE}/auth/forgot-password`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ email }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Request failed." }));
      throw new Error(err.detail || "Failed to process forgot password request.");
    }

    return res.json();
  }

  async resetPassword(token: string, new_password: string): Promise<MessageResponse> {
    const res = await fetch(`${API_BASE}/auth/reset-password`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ token, new_password }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Reset failed." }));
      throw new Error(err.detail || "Failed to reset password.");
    }

    return res.json();
  }

  async verifyEmail(email: string, otp: string): Promise<MessageResponse> {
    const res = await fetch(`${API_BASE}/auth/verify-email`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ email, otp }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Verification failed." }));
      throw new Error(err.detail || "Failed to verify email code.");
    }

    return res.json();
  }

  async resendOTP(email: string): Promise<MessageResponse> {
    const res = await fetch(`${API_BASE}/auth/verify-email/resend`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ email }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Resend failed." }));
      throw new Error(err.detail || "Failed to resend verification code.");
    }

    return res.json();
  }

  async requestVerifyEmail(email: string): Promise<MessageResponse> {
    return this.resendOTP(email);
  }

  async confirmVerifyEmail(token: string): Promise<MessageResponse> {
    const res = await fetch(`${API_BASE}/auth/verify-email/confirm`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ token }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Confirmation failed." }));
      throw new Error(err.detail || "Failed to confirm email verification.");
    }

    return res.json();
  }
}

export const authService = new AuthService();
