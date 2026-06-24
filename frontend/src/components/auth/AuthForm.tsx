"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, type FormEvent } from "react";

type Mode = "login" | "signup";
type FieldId = "name" | "email" | "password";

const STRENGTH_LABELS = ["Too short", "Weak", "Fair", "Good", "Strong"];

function isEmail(v: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
}

function scorePassword(v: string): number {
  let score = 0;
  if (v.length >= 8) score++;
  if (/[A-Z]/.test(v) && /[a-z]/.test(v)) score++;
  if (/\d/.test(v)) score++;
  if (/[^A-Za-z0-9]/.test(v)) score++;
  if (v.length === 0) score = 0;
  return score;
}

export function AuthForm({ mode }: { mode: Mode }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const isSignup = mode === "signup";

  const [values, setValues] = useState({ name: "", email: "", password: "" });
  const [invalid, setInvalid] = useState<Record<FieldId, boolean>>({
    name: false,
    email: false,
    password: false,
  });
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Email-verification (OTP) step, entered after signup or when an unverified
  // user tries to log in.
  const [step, setStep] = useState<"form" | "otp">("form");
  const [code, setCode] = useState("");
  const [pendingEmail, setPendingEmail] = useState("");

  const goToApp = (user: { is_superuser?: boolean } | undefined) => {
    const next = user?.is_superuser ? "/admin" : searchParams.get("next") || "/app/compose";
    router.push(next);
    router.refresh();
  };

  const strength = scorePassword(values.password);
  const strengthLabel =
    values.password.length === 0
      ? "Use 8+ characters with a mix of letters & numbers."
      : STRENGTH_LABELS[Math.min(strength, 4)] + " password";

  const setField = (id: FieldId, value: string) => {
    setValues((v) => ({ ...v, [id]: value }));
    setInvalid((iv) => ({ ...iv, [id]: false })); // clear on input
  };

  const validateEmailBlur = () => {
    setInvalid((iv) => ({ ...iv, email: values.email !== "" && !isEmail(values.email) }));
  };

  const onSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    const checks: Array<[FieldId, boolean]> = isSignup
      ? [
          ["name", values.name.trim().length > 1],
          ["email", isEmail(values.email)],
          ["password", values.password.length >= 8],
        ]
      : [
          ["email", isEmail(values.email)],
          ["password", values.password.length >= 1],
        ];

    const nextInvalid = { ...invalid };
    let ok = true;
    for (const [id, pass] of checks) {
      nextInvalid[id] = !pass;
      if (!pass) ok = false;
    }
    setInvalid(nextInvalid);
    if (!ok) return;

    setLoading(true);
    try {
      const endpoint = isSignup ? "/api/auth/register" : "/api/auth/login";
      const payload = isSignup
        ? {
            full_name: values.name.trim(),
            email: values.email.trim(),
            password: values.password,
            workspace_name: `${values.name.trim().split(" ")[0]}'s Workspace`,
          }
        : { email: values.email.trim(), password: values.password };

      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json().catch(() => null);
      if (!res.ok) {
        // An unverified account trying to log in → send them to the OTP step.
        if (data?.error?.code === "email_not_verified") {
          setPendingEmail(values.email.trim());
          setStep("otp");
          setError(null);
          setLoading(false);
          void fetch("/api/auth/resend", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: values.email.trim() }),
          });
          return;
        }
        setError(data?.error?.message || "Something went wrong. Please try again.");
        setLoading(false);
        return;
      }

      // Signup now returns "verification required" instead of a session.
      if (isSignup && data?.verification_required) {
        setPendingEmail(data.email || values.email.trim());
        setStep("otp");
        setLoading(false);
        return;
      }

      goToApp(data?.user);
    } catch {
      setError("Couldn't reach the server. Is the API running?");
      setLoading(false);
    }
  };

  const verifyOtp = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    if (code.trim().length < 4) {
      setError("Enter the code from your email.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("/api/auth/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: pendingEmail, code: code.trim() }),
      });
      const data = await res.json().catch(() => null);
      if (!res.ok) {
        setError(data?.error?.message || "That code didn't work. Try again.");
        setLoading(false);
        return;
      }
      goToApp(data?.user);
    } catch {
      setError("Couldn't reach the server. Is the API running?");
      setLoading(false);
    }
  };

  const resendOtp = async () => {
    setError(null);
    await fetch("/api/auth/resend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: pendingEmail }),
    }).catch(() => {});
    setError("A new code is on the way.");
  };

  if (step === "otp") {
    return (
      <form className="auth-form" id="otpForm" noValidate onSubmit={verifyOtp}>
        <h1>Verify your email</h1>
        <p className="sub">
          Enter the {6}-digit code we sent to <strong>{pendingEmail}</strong>.
        </p>

        <div className={"error-banner" + (error ? " show" : "")}>
          <svg width="18" height="18">
            <use href="#i-alert" />
          </svg>{" "}
          <span>{error}</span>
        </div>

        <div className="auth-fields">
          <div className="field">
            <label className="field-label" htmlFor="otp">
              Verification code
            </label>
            <input
              className="input"
              id="otp"
              inputMode="numeric"
              autoComplete="one-time-code"
              placeholder="123456"
              maxLength={6}
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
            />
          </div>
        </div>

        <button
          type="submit"
          className={"btn btn-spark btn-lg btn-block" + (loading ? " is-loading" : "")}
          style={{ marginTop: 24 }}
          disabled={loading}
        >
          {loading ? <span className="spin" /> : "Verify & continue"}
        </button>

        <p className="auth-switch">
          Didn&apos;t get it?{" "}
          <button type="button" className="link" onClick={resendOtp}>
            Resend code
          </button>
        </p>
      </form>
    );
  }

  return (
    <form className="auth-form" id={isSignup ? "signupForm" : "loginForm"} noValidate onSubmit={onSubmit}>
      <h1>{isSignup ? "Create your Postit account" : "Welcome back"}</h1>
      <p className="sub">
        {isSignup ? "Connect your platforms after - takes a minute." : "Pick up where you left off."}
      </p>

      <div className={"error-banner" + (error ? " show" : "")} id="errorBanner">
        <svg width="18" height="18">
          <use href="#i-alert" />
        </svg>{" "}
        <span>{error}</span>
      </div>

      <div className="auth-fields">
        {isSignup && (
          <div className={"field" + (invalid.name ? " invalid" : "")} id="f-name">
            <label className="field-label" htmlFor="name">
              Full name
            </label>
            <input
              className="input"
              id="name"
              type="text"
              placeholder="Rina Alvarez"
              autoComplete="name"
              value={values.name}
              onChange={(e) => setField("name", e.target.value)}
            />
            <span className="field-error">Please enter your name.</span>
          </div>
        )}

        <div className={"field" + (invalid.email ? " invalid" : "")} id="f-email">
          <label className="field-label" htmlFor="email">
            Email
          </label>
          <input
            className="input"
            id="email"
            type="email"
            placeholder="you@company.com"
            autoComplete="email"
            value={values.email}
            onChange={(e) => setField("email", e.target.value)}
            onBlur={validateEmailBlur}
          />
          <span className="field-error">Enter a valid email address.</span>
        </div>

        <div className={"field" + (invalid.password ? " invalid" : "")} id="f-password">
          {isSignup ? (
            <label className="field-label" htmlFor="password">
              Password
            </label>
          ) : (
            <div className="field-row">
              <label className="field-label" htmlFor="password">
                Password
              </label>
              <Link href="/forgot" className="link">
                Forgot password?
              </Link>
            </div>
          )}
          <div className="pw-wrap">
            <input
              className="input"
              id="password"
              type={showPw ? "text" : "password"}
              placeholder={isSignup ? "At least 8 characters" : "Your password"}
              autoComplete={isSignup ? "new-password" : "current-password"}
              value={values.password}
              onChange={(e) => setField("password", e.target.value)}
            />
            <button type="button" className="pw-toggle" onClick={() => setShowPw((s) => !s)}>
              {showPw ? "Hide" : "Show"}
            </button>
          </div>

          {isSignup ? (
            <>
              <div className={"strength" + (strength ? " s" + Math.min(strength, 4) : "")} id="strength">
                <i />
                <i />
                <i />
                <i />
              </div>
              <div className="strength-label" id="strengthLabel">
                {strengthLabel}
              </div>
            </>
          ) : (
            <span className="field-error">Please enter your password.</span>
          )}
        </div>

        {!isSignup && (
          <label className="checkbox-row">
            <input type="checkbox" defaultChecked /> Remember me on this device
          </label>
        )}
      </div>

      <button
        type="submit"
        className={"btn btn-spark btn-lg btn-block" + (loading ? " is-loading" : "")}
        id="submitBtn"
        style={{ marginTop: 24 }}
        disabled={loading}
      >
        {loading ? <span className="spin" /> : isSignup ? "Create account" : "Log in"}
      </button>

      {isSignup ? (
        <>
          <p className="fineprint">
            By continuing you agree to our <Link href="/terms">Terms</Link> &amp;{" "}
            <Link href="/privacy">Privacy</Link>.
          </p>
          <p className="auth-switch">
            Already have an account? <Link href="/login">Log in</Link>
          </p>
        </>
      ) : (
        <p className="auth-switch">
          New here? <Link href="/signup">Create an account.</Link>
        </p>
      )}
    </form>
  );
}
