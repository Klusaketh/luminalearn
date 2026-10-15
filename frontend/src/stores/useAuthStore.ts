import { create } from "zustand";
import {
  authService,
  UserResponse,
  TokenResponse,
  StudentRegisterPayload,
  TeacherRegisterPayload,
} from "../services/authService";

interface AuthState {
  user: UserResponse | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  loginWithGoogle: (
    credential: string,
    role?: "student" | "teacher",
    preferredModality?: "visual" | "auditory" | "read_write" | "kinesthetic"
  ) => Promise<UserResponse>;
  registerStudent: (payload: StudentRegisterPayload) => Promise<void>;
  registerTeacher: (payload: TeacherRegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
  fetchCurrentUser: () => Promise<void>;
  initializeAuth: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  clearError: () => set({ error: null }),

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const tokens: TokenResponse = await authService.login(email, password);
      
      if (typeof window !== "undefined") {
        localStorage.setItem("lumina_access_token", tokens.access_token);
        localStorage.setItem("lumina_refresh_token", tokens.refresh_token);
      }

      set({
        user: tokens.user,
        accessToken: tokens.access_token,
        refreshToken: tokens.refresh_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (err: any) {
      set({
        error: err.message || "Failed to log in.",
        isLoading: false,
      });
      throw err;
    }
  },

  loginWithGoogle: async (credential, role = "student", preferredModality) => {
    set({ isLoading: true, error: null });
    try {
      const tokens: TokenResponse = await authService.loginWithGoogle(credential, role, preferredModality);

      if (typeof window !== "undefined") {
        localStorage.setItem("lumina_access_token", tokens.access_token);
        localStorage.setItem("lumina_refresh_token", tokens.refresh_token);
      }

      set({
        user: tokens.user,
        accessToken: tokens.access_token,
        refreshToken: tokens.refresh_token,
        isAuthenticated: true,
        isLoading: false,
      });

      return tokens.user;
    } catch (err: any) {
      set({
        error: err.message || "Failed to authenticate with Google.",
        isLoading: false,
      });
      throw err;
    }
  },

  registerStudent: async (payload) => {
    set({ isLoading: true, error: null });
    try {
      await authService.registerStudent(payload);
      set({ isLoading: false, error: null });
    } catch (err: any) {
      set({
        error: err.message || "Failed to register student.",
        isLoading: false,
      });
      throw err;
    }
  },

  registerTeacher: async (payload) => {
    set({ isLoading: true, error: null });
    try {
      await authService.registerTeacher(payload);
      set({ isLoading: false, error: null });
    } catch (err: any) {
      set({
        error: err.message || "Failed to register teacher.",
        isLoading: false,
      });
      throw err;
    }
  },

  logout: async () => {
    const token = get().accessToken;
    if (token) {
      await authService.logout(token).catch(() => {});
    }

    if (typeof window !== "undefined") {
      localStorage.removeItem("lumina_access_token");
      localStorage.removeItem("lumina_refresh_token");
    }

    set({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      error: null,
    });
  },

  fetchCurrentUser: async () => {
    const token = get().accessToken;
    if (!token) return;
    try {
      const user = await authService.getMe(token);
      set({ user, isAuthenticated: true });
    } catch {
      // If token expired, try refreshing
      const refreshToken = get().refreshToken;
      if (refreshToken) {
        try {
          const tokens = await authService.refreshToken(refreshToken);
          if (typeof window !== "undefined") {
            localStorage.setItem("lumina_access_token", tokens.access_token);
            localStorage.setItem("lumina_refresh_token", tokens.refresh_token);
          }
          set({
            user: tokens.user,
            accessToken: tokens.access_token,
            refreshToken: tokens.refresh_token,
            isAuthenticated: true,
          });
          return;
        } catch {
          // Token refresh failed, log out
          get().logout();
        }
      }
      set({ isAuthenticated: false, user: null, accessToken: null, refreshToken: null });
    }
  },

  initializeAuth: async () => {
    if (typeof window === "undefined") return;
    const accessToken = localStorage.getItem("lumina_access_token");
    const refreshToken = localStorage.getItem("lumina_refresh_token");

    if (accessToken) {
      set({ accessToken, refreshToken, isLoading: true });
      try {
        const user = await authService.getMe(accessToken);
        set({ user, isAuthenticated: true, isLoading: false });
      } catch {
        if (refreshToken) {
          try {
            const tokens = await authService.refreshToken(refreshToken);
            localStorage.setItem("lumina_access_token", tokens.access_token);
            localStorage.setItem("lumina_refresh_token", tokens.refresh_token);
            set({
              user: tokens.user,
              accessToken: tokens.access_token,
              refreshToken: tokens.refresh_token,
              isAuthenticated: true,
              isLoading: false,
            });
          } catch {
            localStorage.removeItem("lumina_access_token");
            localStorage.removeItem("lumina_refresh_token");
            set({ isAuthenticated: false, user: null, accessToken: null, refreshToken: null, isLoading: false });
          }
        } else {
          set({ isLoading: false });
        }
      }
    }
  },
}));
