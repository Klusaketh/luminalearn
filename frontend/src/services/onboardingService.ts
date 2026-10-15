const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

export interface DiagnosticQuestion {
  id: number;
  subject: string;
  topic: string;
  difficulty: "Easy" | "Medium" | "Hard";
  question: string;
  options: string[];
}

export interface QuestionAnswer {
  question_id: number;
  selected_option_index: number;
  time_taken_ms?: number;
}

export interface OnboardingSubmitPayload {
  goals: string[];
  interests: string[];
  selected_subjects: string[];
  answers: QuestionAnswer[];
}

export interface LearnerProfile {
  user_id: string;
  goals: string[];
  interests: string[];
  selected_subjects: string[];
  assessment_score: number;
  strengths: string[];
  weak_areas: string[];
  recommended_weekly_hours: number;
  suggested_starting_topic: string;
  created_at: string;
}

export interface RoadmapModule {
  id: number;
  title: string;
  description: string;
  estimated_hours: number;
  difficulty: string;
  is_key_focus: boolean;
}

export interface PersonalizedRoadmap {
  profile: LearnerProfile;
  recommended_course: string;
  weekly_goal_hours: number;
  daily_target_minutes: number;
  starting_module: string;
  roadmap_modules: RoadmapModule[];
}

class OnboardingService {
  private getHeaders(token?: string): HeadersInit {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  }

  async getDiagnosticQuestions(): Promise<DiagnosticQuestion[]> {
    const res = await fetch(`${API_BASE}/onboarding/questions`, {
      method: "GET",
      headers: this.getHeaders(),
    });

    if (!res.ok) {
      throw new Error("Failed to load diagnostic assessment questions.");
    }

    return res.json();
  }

  async submitOnboarding(
    payload: OnboardingSubmitPayload,
    token?: string
  ): Promise<LearnerProfile> {
    const res = await fetch(`${API_BASE}/onboarding/submit`, {
      method: "POST",
      headers: this.getHeaders(token),
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Submission failed." }));
      throw new Error(err.detail || "Failed to submit onboarding responses.");
    }

    return res.json();
  }

  async getLearnerProfile(token?: string): Promise<LearnerProfile> {
    const res = await fetch(`${API_BASE}/onboarding/profile`, {
      method: "GET",
      headers: this.getHeaders(token),
    });

    if (!res.ok) {
      throw new Error("Failed to fetch learner profile.");
    }

    return res.json();
  }

  async getPersonalizedRoadmap(token?: string): Promise<PersonalizedRoadmap> {
    const res = await fetch(`${API_BASE}/onboarding/roadmap`, {
      method: "GET",
      headers: this.getHeaders(token),
    });

    if (!res.ok) {
      throw new Error("Failed to fetch personalized study roadmap.");
    }

    return res.json();
  }
}

export const onboardingService = new OnboardingService();
