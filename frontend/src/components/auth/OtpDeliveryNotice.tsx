import { AlertTriangle, MailCheck, Terminal } from "lucide-react";
import type { OTPDelivery } from "../../services/authService";

const DELIVERIES: readonly OTPDelivery[] = ["email", "console", "failed"];

/** Read a `delivery` query parameter; anything else means "unknown" (null). */
export function parseDelivery(value: string | null): OTPDelivery | null {
  return DELIVERIES.find((delivery) => delivery === value) ?? null;
}

const STYLES: Record<OTPDelivery, string> = {
  email: "bg-indigo-500/10 border-indigo-500/30 text-indigo-200",
  console: "bg-amber-500/10 border-amber-500/40 text-amber-200",
  failed: "bg-rose-500/10 border-rose-500/30 text-rose-300",
};

/**
 * Says truthfully where the 6-digit code went. Shown after sign-up, Resend and "Forgot password",
 * so the page never claims an email was sent when the server didn't send one.
 */
export function OtpDeliveryNotice({ delivery, email }: { delivery: OTPDelivery; email: string }) {
  const Icon = delivery === "email" ? MailCheck : delivery === "console" ? Terminal : AlertTriangle;
  return (
    <div
      role={delivery === "failed" ? "alert" : "status"}
      className={`p-3.5 rounded-xl border text-xs leading-relaxed flex items-start gap-2.5 ${STYLES[delivery]}`}
    >
      <Icon className="w-4 h-4 shrink-0 mt-0.5" />
      {delivery === "email" ? (
        <p>
          Sent to <strong className="text-white break-all">{email || "your email address"}</strong>. Check Spam if it
          hasn&apos;t arrived in a minute.
        </p>
      ) : delivery === "console" ? (
        <p>
          Email isn&apos;t set up on this server. In development, the code is printed in the terminal running the
          API.
        </p>
      ) : (
        <p>We couldn&apos;t send the email. Try Resend in a minute.</p>
      )}
    </div>
  );
}
