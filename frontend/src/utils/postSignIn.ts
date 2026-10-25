import { BackendUnavailableError } from "@/services/apiClient";
import { onboardingService } from "@/services/onboardingService";
import { homePathFor, safeRedirectTarget, type WorkspaceRole } from "@/utils/routes";

/**
 * Where to go right after signing in: the workspace page the visitor asked for, else their
 * role's home. Students without a learner profile still have onboarding to finish.
 */
async function postSignInPath(role: WorkspaceRole, requested: string | null): Promise<string> {
  const safe = safeRedirectTarget(requested);
  if (safe) return safe;
  if (role !== "student") return homePathFor(role);
  try {
    await onboardingService.getLearnerProfile();
    return "/dashboard";
  } catch (err) {
    // A missing profile means onboarding; an unreachable server is no reason to redo it.
    return err instanceof BackendUnavailableError ? "/dashboard" : "/onboarding";
  }
}

/**
 * Enter the workspace after signing in. A full page load, not a client-side navigation: while
 * signed out, Next.js may have prefetched workspace links and cached the middleware's redirect to
 * sign-in, and a client-side navigation would replay that cached redirect straight back to /login.
 * replace() keeps the sign-in form out of the Back history.
 */
export async function enterWorkspace(role: WorkspaceRole, requested: string | null): Promise<void> {
  window.location.replace(await postSignInPath(role, requested));
}
