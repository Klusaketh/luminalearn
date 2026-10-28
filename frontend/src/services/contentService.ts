import { API_BASE, apiFetch } from "./apiClient";

export interface ContentCategorySummary {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  display_order: number;
  subject_count: number;
}

export interface SubjectSummary {
  id: string;
  category_id: string;
  category_name: string | null;
  category_slug: string | null;
  name: string;
  slug: string;
  short_description: string | null;
  icon_key: string | null;
  difficulty_level: string;
  display_order: number;
  course_count: number;
  module_count: number;
  topic_count: number;
  lesson_count: number;
  /** Every topic title, in syllabus order, so the catalog can search topics. */
  topic_titles: string[];
}

export interface SubjectDetail {
  id: string;
  category_id: string;
  category_name: string | null;
  category_slug: string | null;
  name: string;
  slug: string;
  short_description: string | null;
  description: string | null;
  icon_key: string | null;
  difficulty_level: string;
  display_order: number;
  courses: CourseSummary[];
}

export interface CourseSummary {
  id: string;
  subject_id: string;
  title: string;
  slug: string;
  description: string | null;
  difficulty: string;
  estimated_hours: number;
  display_order: number;
  module_count: number;
}

export interface CourseDetail {
  id: string;
  subject_id: string;
  subject_name: string | null;
  subject_slug: string | null;
  title: string;
  slug: string;
  description: string | null;
  difficulty: string;
  estimated_hours: number;
  display_order: number;
  modules: ModuleDetail[];
}

export interface ModuleSummary {
  id: string;
  course_id: string;
  title: string;
  slug: string;
  description: string | null;
  estimated_minutes: number;
  display_order: number;
  topic_count: number;
}

export interface ModuleDetail {
  id: string;
  course_id: string;
  title: string;
  slug: string;
  description: string | null;
  estimated_minutes: number;
  display_order: number;
  topics: TopicSummary[];
}

export interface TopicSummary {
  id: string;
  module_id: string;
  title: string;
  slug: string;
  summary: string | null;
  estimated_minutes: number;
  difficulty: string;
  display_order: number;
  lesson_count: number;
}

export interface TopicDetail {
  id: string;
  module_id: string;
  module_title: string | null;
  course_id: string | null;
  course_title: string | null;
  course_slug: string | null;
  subject_name: string | null;
  subject_slug: string | null;
  title: string;
  slug: string;
  summary: string | null;
  estimated_minutes: number;
  difficulty: string;
  display_order: number;
  lessons: LessonSummary[];
  navigation: TopicNavigation | null;
}

export interface TopicNavLink {
  topic_id: string;
  title: string;
  module_title: string;
  lesson_id: string | null;
}

export interface TopicNavigation {
  previous: TopicNavLink | null;
  next: TopicNavLink | null;
  position: number;
  total: number;
}

export interface LessonSummary {
  id: string;
  topic_id: string;
  title: string;
  slug: string;
  summary: string | null;
  estimated_minutes: number;
  display_order: number;
  lesson_type: string;
}

export interface LessonNavLink {
  lesson_id: string;
  lesson_title: string;
  topic_id: string;
  topic_title: string;
  module_title: string;
}

export interface ModuleTopicLink {
  topic_id: string;
  title: string;
  lesson_id: string | null;
  is_current: boolean;
}

export interface LessonNavigation {
  previous: LessonNavLink | null;
  next: LessonNavLink | null;
  position: number;
  total: number;
  module_topics: ModuleTopicLink[];
}

export interface LessonDetail {
  id: string;
  topic_id: string;
  topic_title: string | null;
  topic_summary: string | null;
  topic_difficulty: string | null;
  module_id: string | null;
  module_title: string | null;
  course_id: string | null;
  course_title: string | null;
  course_slug: string | null;
  subject_name: string | null;
  subject_slug: string | null;
  title: string;
  slug: string;
  summary: string | null;
  content: string;
  learning_objectives: string[];
  estimated_minutes: number;
  display_order: number;
  lesson_type: string;
  navigation: LessonNavigation | null;
}

export interface SyllabusLesson {
  id: string;
  title: string;
  slug: string;
  estimated_minutes: number;
}

export interface SyllabusTopic {
  id: string;
  title: string;
  slug: string;
  summary: string | null;
  difficulty: string;
  estimated_minutes: number;
  display_order: number;
  lessons: SyllabusLesson[];
}

export interface SyllabusModule {
  id: string;
  title: string;
  slug: string;
  description: string | null;
  estimated_minutes: number;
  display_order: number;
  topics: SyllabusTopic[];
}

export interface SyllabusCourse {
  id: string;
  title: string;
  slug: string;
  description: string | null;
  difficulty: string;
  estimated_hours: number;
  display_order: number;
  modules: SyllabusModule[];
}

/** A subject with its full course -> module -> topic -> lesson tree (no lesson bodies). */
export interface SubjectSyllabus {
  id: string;
  name: string;
  slug: string;
  category_name: string | null;
  category_slug: string | null;
  short_description: string | null;
  description: string | null;
  icon_key: string | null;
  difficulty_level: string;
  module_count: number;
  topic_count: number;
  lesson_count: number;
  estimated_hours: number;
  courses: SyllabusCourse[];
}

class ContentService {
  private getHeaders(token?: string): HeadersInit {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  }

  /** Catalog reads use the signed-in session and give up after 8 seconds. */
  private fetchWithTimeout(url: string, options: RequestInit = {}, timeoutMs = 8000): Promise<Response> {
    return apiFetch(url, { ...options, timeoutMs });
  }

  async getCategories(): Promise<ContentCategorySummary[]> {
    const res = await this.fetchWithTimeout(`${API_BASE}/content/categories`, {
      method: "GET",
      headers: this.getHeaders(),
    });
    if (!res.ok) {
      throw new Error("Failed to load academic categories.");
    }
    return res.json();
  }

  async getSubjects(params?: {
    category_slug?: string;
    difficulty?: string;
    search?: string;
  }): Promise<SubjectSummary[]> {
    const query = new URLSearchParams();
    if (params?.category_slug) {
      query.append("category_slug", params.category_slug);
    }
    if (params?.difficulty) {
      query.append("difficulty", params.difficulty);
    }
    if (params?.search) {
      query.append("search", params.search);
    }

    const queryString = query.toString();
    const suffix = queryString ? `?${queryString}` : "";
    const res = await this.fetchWithTimeout(`${API_BASE}/content/subjects${suffix}`, {
      method: "GET",
      headers: this.getHeaders(),
    });
    if (!res.ok) {
      throw new Error("Failed to load academic subjects.");
    }
    return res.json();
  }

  async getSubject(slug: string): Promise<SubjectDetail> {
    const res = await this.fetchWithTimeout(
      `${API_BASE}/content/subjects/${slug}`,
      {
        method: "GET",
        headers: this.getHeaders(),
      }
    );
    if (!res.ok) {
      if (res.status === 404) throw new Error("Subject not found.");
      throw new Error("Failed to load subject details.");
    }
    return res.json();
  }

  async getSyllabus(slug: string): Promise<SubjectSyllabus> {
    const res = await this.fetchWithTimeout(`${API_BASE}/content/subjects/${encodeURIComponent(slug)}/syllabus`, {
      method: "GET",
      headers: this.getHeaders(),
    });
    if (!res.ok) {
      if (res.status === 404) throw new Error("Subject not found.");
      throw new Error("Failed to load the subject syllabus.");
    }
    return res.json();
  }

  async getCourses(subjectSlug: string): Promise<CourseSummary[]> {
    const res = await this.fetchWithTimeout(
      `${API_BASE}/content/subjects/${subjectSlug}/courses`,
      {
        method: "GET",
        headers: this.getHeaders(),
      }
    );
    if (!res.ok) {
      throw new Error("Failed to load courses for this subject.");
    }
    return res.json();
  }

  async getCourse(slug: string): Promise<CourseDetail> {
    const res = await this.fetchWithTimeout(
      `${API_BASE}/content/courses/${slug}`,
      {
        method: "GET",
        headers: this.getHeaders(),
      }
    );
    if (!res.ok) {
      if (res.status === 404) throw new Error("Course not found.");
      throw new Error("Failed to load course details.");
    }
    return res.json();
  }

  async getModules(courseSlug: string): Promise<ModuleDetail[]> {
    const res = await this.fetchWithTimeout(
      `${API_BASE}/content/courses/${courseSlug}/modules`,
      {
        method: "GET",
        headers: this.getHeaders(),
      }
    );
    if (!res.ok) {
      throw new Error("Failed to load course modules.");
    }
    return res.json();
  }

  async getTopics(moduleId: string): Promise<TopicSummary[]> {
    const res = await this.fetchWithTimeout(
      `${API_BASE}/content/modules/${moduleId}/topics`,
      {
        method: "GET",
        headers: this.getHeaders(),
      }
    );
    if (!res.ok) {
      throw new Error("Failed to load module topics.");
    }
    return res.json();
  }

  async getTopic(id: string): Promise<TopicDetail> {
    const res = await this.fetchWithTimeout(
      `${API_BASE}/content/topics/${id}`,
      {
        method: "GET",
        headers: this.getHeaders(),
      }
    );
    if (!res.ok) {
      if (res.status === 404) throw new Error("Topic not found.");
      throw new Error("Failed to load topic details.");
    }
    return res.json();
  }

  async getLessons(topicId: string): Promise<LessonSummary[]> {
    const res = await this.fetchWithTimeout(
      `${API_BASE}/content/topics/${topicId}/lessons`,
      {
        method: "GET",
        headers: this.getHeaders(),
      }
    );
    if (!res.ok) {
      throw new Error("Failed to load topic lessons.");
    }
    return res.json();
  }

  async getLesson(id: string, token?: string): Promise<LessonDetail> {
    const res = await this.fetchWithTimeout(
      `${API_BASE}/content/lessons/${id}`,
      {
        method: "GET",
        headers: this.getHeaders(token),
      }
    );
    if (!res.ok) {
      if (res.status === 401) {
        throw new Error("AUTHENTICATION_REQUIRED");
      }
      if (res.status === 403) {
        const errorData = await res.json().catch(() => ({}));
        if (errorData.detail === "EMAIL_VERIFICATION_REQUIRED") {
          throw new Error("EMAIL_VERIFICATION_REQUIRED");
        }
        throw new Error("Access forbidden.");
      }
      if (res.status === 404) {
        throw new Error("Lesson not found.");
      }
      throw new Error("Failed to load lesson content.");
    }
    return res.json();
  }
}

export const contentService = new ContentService();
