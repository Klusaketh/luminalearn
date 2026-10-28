import { create } from "zustand";
import {
  authService,
  UserResponse,
  TokenResponse,
  StudentRegisterPayload,
  TeacherRegisterPayload,
} from "../services/authService";
import { BackendUnavailableError, connectSession } from "../services/apiClient";
import { SESSION_COOKIE } from "../utils/routes";

/**
 * unknown       nothing checked yet (also the server render, so markup always matches)
 * checking      verifying stored tokens with the server
 * authenticated a verified learner is signed in
 * anonymous     no valid session; workspace pages redirect to sign-in
 * unreachable   tokens exist but the server can't be reached; kept, and re-checked when it's back
 */
export type SessionStatus = "unknown" | "checking" | "authenticated" | "anonymous" | "unreachable";

interface AuthState {
  user: UserResponse | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  sessionStatus: SessionStatus;
  /** The learner pressed "Sign out", so pages should not send them to sign-in with a return path. */
  signedOutByUser: boolean;
  /** A sign-in or registration form is submitting. */
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
  /** Verify the stored session once; concurrent callers share the same check. */
  initializeAuth: () => Promise<void>;
  /** Exchange the refresh token for a new pair; concurrent callers share one request. */
  refreshSession: () => Promise<string | null>;
  /** The access token, refreshed first when it expires within a minute. Null when signed out. */
  ensureFreshAccessToken: () => Promise<string | null>;
  clearError: () => void;
}

const ACCESS_KEY = "lumina_access_token";
const REFRESH_KEY = "lumina_refresh_token";
const SESSION_COOKIE_MAX_AGE = 7 * 24 * 60 * 60; // matches the refresh token's lifetime
const REFRESH_MARGIN_MS = 60_000;

function writeSessionCookie(present: boolean): void {
  const secure = window.location.protocol === "https:" ? "; Secure" : "";
  document.cookie = present
    ? `${SESSION_COOKIE}=1; Path=/; Max-Age=${SESSION_COOKIE_MAX_AGE}; SameSite=Lax${secure}`
    : `${SESSION_COOKIE}=; Path=/; Max-Age=0; SameSite=Lax${secure}`;
}

function storeTokens(tokens: TokenResponse): void {
  localStorage.setItem(ACCESS_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
  writeSessionCookie(true);
}

function clearStoredTokens(): void {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
  writeSessionCookie(false);
}

/** Milliseconds since the epoch at which a JWT expires, or null when it can't be read. */
function tokenExpiry(token: string): number | null {
  try {
    const payload = token.split(".")[1];
    const json = JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/"))) as { exp?: unknown };
    return typeof json.exp === "number" ? json.exp * 1000 : null;
  } catch {
    return null;
  }
}

const SIGNED_OUT = {
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  sessionStatus: "anonymous" as const,
};

let verifyInFlight: Promise<void> | null = null;
let refreshInFlight: Promise<string | null> | null = null;
let syncingTabs = false;

export const useAuthStore = create<AuthState>((set, get) => {
  const signIn = (tokens: TokenResponse) => {
    storeTokens(tokens);
    set({
      user: tokens.user,
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
      isAuthenticated: true,
      sessionStatus: "authenticated",
      signedOutByUser: false,
      isLoading: false,
      error: null,
    });
  };

  const signOutLocally = () => {
    clearStoredTokens();
    set(SIGNED_OUT);
  };

  /** Keep every open tab on the same session: sign-in, refresh and sign-out spread to the others. */
  const syncAcrossTabs = () => {
    if (syncingTabs) return;
    syncingTabs = true;
    window.addEventListener("storage", (event) => {
      if (event.key !== ACCESS_KEY && event.key !== REFRESH_KEY && event.key !== null) return;
      const accessToken = localStorage.getItem(ACCESS_KEY);
      const refreshToken = localStorage.getItem(REFRESH_KEY);
      if (!accessToken && !refreshToken) {
        set({ ...SIGNED_OUT, signedOutByUser: true });
      } else if (get().sessionStatus === "authenticated") {
        set({ accessToken, refreshToken }); // another tab refreshed the pair; adopt it quietly
      } else if (accessToken !== get().accessToken) {
        set({ accessToken, refreshToken, sessionStatus: "unknown" }); // signed in elsewhere
        void get().initializeAuth();
      }
    });
  };

  const verifyStoredSession = async () => {
    const accessToken = localStorage.getItem(ACCESS_KEY);
    const refreshToken = localStorage.getItem(REFRESH_KEY);
    if (!accessToken && !refreshToken) {
      signOutLocally();
      return;
    }
    set({ accessToken, refreshToken, sessionStatus: "checking" });
    try {
      // A token that has expired (or is about to) goes straight to the refresh: no doomed request.
      const expiry = accessToken ? tokenExpiry(accessToken) : null;
      if (accessToken && expiry !== null && expiry - Date.now() > REFRESH_MARGIN_MS) {
        try {
          const user = await authService.getMe(accessToken);
          writeSessionCookie(true);
          set({ user, isAuthenticated: true, sessionStatus: "authenticated" });
          return;
        } catch (error) {
          if (error instanceof BackendUnavailableError) throw error;
          // Expired or revoked access token: fall through to the refresh token.
        }
      }
      await get().refreshSession();
    } catch (error) {
      if (error instanceof BackendUnavailableError) {
        set({ sessionStatus: "unreachable" });
      } else {
        signOutLocally();
      }
    }
  };

  return {
    user: null,
    accessToken: null,
    refreshToken: null,
    isAuthenticated: false,
    sessionStatus: "unknown",
    signedOutByUser: false,
    isLoading: false,
    error: null,

    clearError: () => set({ error: null }),

    login: async (email, password) => {
      set({ isLoading: true, error: null });
      try {
        signIn(await authService.login(email, password));
      } catch (err) {
        set({ error: err instanceof Error ? err.message : "Failed to log in.", isLoading: false });
        throw err;
      }
    },

    loginWithGoogle: async (credential, role = "student", preferredModality) => {
      set({ isLoading: true, error: null });
      try {
        const tokens = await authService.loginWithGoogle(credential, role, preferredModality);
        signIn(tokens);
        return tokens.user;
      } catch (err) {
        set({ error: err instanceof Error ? err.message : "Failed to authenticate with Google.", isLoading: false });
        throw err;
      }
    },

    registerStudent: async (payload) => {
      set({ isLoading: true, error: null });
      try {
        await authService.registerStudent(payload);
        set({ isLoading: false, error: null });
      } catch (err) {
        set({ error: err instanceof Error ? err.message : "Failed to register student.", isLoading: false });
        throw err;
      }
    },

    registerTeacher: async (payload) => {
      set({ isLoading: true, error: null });
      try {
        await authService.registerTeacher(payload);
        set({ isLoading: false, error: null });
      } catch (err) {
        set({ error: err instanceof Error ? err.message : "Failed to register teacher.", isLoading: false });
        throw err;
      }
    },

    logout: async () => {
      const token = get().accessToken;
      // Sign out locally first: an unreachable server must never keep someone signed in.
      signOutLocally();
      set({ error: null, signedOutByUser: true });
      if (token) await authService.logout(token).catch(() => undefined);
    },

    initializeAuth: () => {
      if (typeof window === "undefined") return Promise.resolve();
      syncAcrossTabs();
      const { sessionStatus } = get();
      if (sessionStatus === "authenticated" || sessionStatus === "anonymous") return Promise.resolve();
      verifyInFlight ??= verifyStoredSession().finally(() => {
        verifyInFlight = null;
      });
      return verifyInFlight;
    },

    refreshSession: () => {
      // One request at a time: refresh tokens are single-use, so parallel refreshes would
      // invalidate each other and sign the learner out.
      refreshInFlight ??= (async () => {
        const refreshToken = get().refreshToken ?? localStorage.getItem(REFRESH_KEY);
        if (!refreshToken) {
          signOutLocally();
          return null;
        }
        try {
          const tokens = await authService.refreshToken(refreshToken);
          signIn(tokens);
          return tokens.access_token;
        } catch (error) {
          if (error instanceof BackendUnavailableError) throw error; // keep the session for later
          signOutLocally();
          return null;
        }
      })().finally(() => {
        refreshInFlight = null;
      });
      return refreshInFlight;
    },

    ensureFreshAccessToken: async () => {
      const token = get().accessToken ?? localStorage.getItem(ACCESS_KEY);
      if (!token && !(get().refreshToken ?? localStorage.getItem(REFRESH_KEY))) return null; // signed out
      const expiry = token ? tokenExpiry(token) : null;
      if (token && expiry !== null && expiry - Date.now() > REFRESH_MARGIN_MS) return token;
      return get().refreshSession().catch(() => null);
    },
  };
});

connectSession({
  accessToken: () => useAuthStore.getState().ensureFreshAccessToken(),
  refresh: () => useAuthStore.getState().refreshSession().catch(() => null),
});
