import { API_BASE, apiFetch, readErrorDetail } from "./apiClient";

export interface QuizQuestionStudentView {
  id: string;
  question_index: number;
  prompt: string;
  options: string[];
  blooms_level: string;
  question_type?: string;
  source_reference?: string | null;
  irt_difficulty: number;
}

export interface QuizSessionDetail {
  id: string;
  topic_title: string;
  difficulty_level: string;
  total_questions: number;
  score: number;
  status: string;
  initial_mastery: number;
  final_mastery: number | null;
  created_at: string;
  completed_at: string | null;
  questions: QuizQuestionStudentView[];
}

export interface QuizSubmitAnswerRequest {
  session_id: string;
  question_id: string;
  selected_answer: string;
  latency_ms: number;
}

export interface QuizSubmitAnswerResponse {
  attempt_id: string;
  is_correct: boolean;
  selected_answer: string;
  correct_answer: string;
  explanation: string;
  detected_misconception: string | null;
  feedback: string;
  prior_mastery: number;
  posterior_mastery: number;
  next_opportunity_mastery: number;
  predicted_accuracy: number;
  confidence?: number | null;
  session_completed: boolean;
  session_score: number;
  session_final_mastery: number | null;
  previous_retention_level?: RetentionLevel | null;
  retention_level?: RetentionLevel | null;
  /** True when this answer lifted the learner into a higher competency tier. */
  level_up?: boolean;
}

export type RetentionLevel = "Novice" | "Developing" | "Competent" | "Mastered";

export interface RetentionForecast {
  days: number[];
  no_review: number[];
  spaced: number[];
  review_days: number[];
  target_retention: number;
  half_life_days: number;
  initial_stability_days: number;
}

export interface TopicMasterySummary {
  topic_title: string;
  current_mastery: number;
  predicted_accuracy: number;
  retention_level: RetentionLevel;
  total_attempts: number;
  correct_attempts: number;
  streak: number;
  last_attempt_at: string | null;
}

export interface QuizMasteryHistoryItem {
  attempt_id: string;
  is_correct: boolean;
  latency_ms: number;
  posterior_mastery: number;
  created_at: string;
}

export interface QuizMasteryResponse {
  topic_title: string;
  topic_id: string | null;
  current_mastery: number;
  predicted_accuracy: number;
  total_attempts: number;
  correct_attempts: number;
  retention_level: RetentionLevel;
  history: QuizMasteryHistoryItem[];
  retention_forecast?: RetentionForecast | null;
}

export interface QuizGenerateRequest {
  topic: string;
  topic_id?: string;
  difficulty?: "beginner" | "intermediate" | "advanced";
  question_count?: number;
}

class QuizService {
  /** The API client attaches the session token; an explicit token still takes precedence. */
  private getHeaders(token?: string): HeadersInit {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  }

  /** Generating questions can take a while with the live model, so allow 15 seconds. */
  private fetchWithTimeout(url: string, options: RequestInit = {}, timeoutMs = 15000): Promise<Response> {
    return apiFetch(url, { ...options, timeoutMs });
  }

  async generateQuiz(
    payload: QuizGenerateRequest,
    token?: string
  ): Promise<QuizSessionDetail> {
    const res = await this.fetchWithTimeout(`${API_BASE}/quiz/generate`, {
      method: "POST",
      headers: this.getHeaders(token),
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      if (res.status === 401) {
        throw new Error("AUTHENTICATION_REQUIRED");
      }
      if (res.status === 403) {
        const errorData = await res.json().catch(() => ({}));
        if (errorData.detail === "EMAIL_VERIFICATION_REQUIRED") {
          throw new Error("EMAIL_VERIFICATION_REQUIRED");
        }
        throw new Error("Access forbidden. Account not verified.");
      }
      throw new Error(await readErrorDetail(res, "Failed to generate adaptive quiz."));
    }
    return res.json();
  }

  async getQuizSession(
    sessionId: string,
    token?: string
  ): Promise<QuizSessionDetail> {
    const res = await this.fetchWithTimeout(
      `${API_BASE}/quiz/session/${sessionId}`,
      {
        method: "GET",
        headers: this.getHeaders(token),
      }
    );

    if (!res.ok) {
      if (res.status === 401) throw new Error("AUTHENTICATION_REQUIRED");
      if (res.status === 403) throw new Error("Access denied to this session.");
      if (res.status === 404) throw new Error("Quiz session not found.");
      throw new Error("Failed to load quiz session.");
    }
    return res.json();
  }

  async submitAnswer(
    payload: QuizSubmitAnswerRequest,
    token?: string
  ): Promise<QuizSubmitAnswerResponse> {
    const res = await this.fetchWithTimeout(`${API_BASE}/quiz/submit-answer`, {
      method: "POST",
      headers: this.getHeaders(token),
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      if (res.status === 401) throw new Error("AUTHENTICATION_REQUIRED");
      if (res.status === 403) throw new Error("Access denied.");
      if (res.status === 404) throw new Error("Question or session not found.");
      throw new Error(await readErrorDetail(res, "Failed to evaluate answer submission."));
    }
    return res.json();
  }

  async getMastery(
    topic: string,
    token?: string
  ): Promise<QuizMasteryResponse> {
    const encoded = encodeURIComponent(topic);
    const res = await this.fetchWithTimeout(`${API_BASE}/quiz/mastery/${encoded}`, {
      method: "GET",
      headers: this.getHeaders(token),
    });

    if (!res.ok) {
      if (res.status === 401) throw new Error("AUTHENTICATION_REQUIRED");
      throw new Error("Failed to load mastery retention metrics.");
    }
    return res.json();
  }

  async getMasteries(token?: string): Promise<TopicMasterySummary[]> {
    const res = await this.fetchWithTimeout(`${API_BASE}/quiz/masteries`, {
      method: "GET",
      headers: this.getHeaders(token),
    });
    if (!res.ok) {
      if (res.status === 401) throw new Error("AUTHENTICATION_REQUIRED");
      throw new Error("Failed to load topic masteries.");
    }
    return res.json();
  }
}

export const quizService = new QuizService();
