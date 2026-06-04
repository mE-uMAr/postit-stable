"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";

import { api } from "@/lib/api/client";
import { errorMessage } from "@/lib/api/useApi";

import "@/styles/auth.css";

export default function ForgotPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Dev convenience: the API returns the token outside production so the demo works without email.
  const [devToken, setDevToken] = useState<string | null>(null);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.post<{ message: string; reset_token: string | null }>("auth/forgot", {
        email: email.trim(),
      });
      setSent(true);
      setDevToken(res.reset_token ?? null);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth">
      <section className="auth-form-wrap" style={{ margin: "0 auto" }}>
        {sent ? (
          <div className="auth-form">
            <h1>Check your email</h1>
            <p className="sub">
              If an account exists for <strong>{email}</strong>, a password-reset link is on its way.
            </p>
            {devToken && (
              <p className="magic-link" style={{ marginTop: 16 }}>
                <Link className="link" href={`/reset?token=${devToken}`}>
                  Dev shortcut: reset your password →
                </Link>
              </p>
            )}
            <p className="auth-switch" style={{ marginTop: 20 }}>
              <Link href="/login">Back to log in</Link>
            </p>
          </div>
        ) : (
          <form className="auth-form" onSubmit={onSubmit} noValidate>
            <h1>Reset your password</h1>
            <p className="sub">Enter your account email and we&apos;ll send you a reset link.</p>

            <div className={"error-banner" + (error ? " show" : "")}>
              <span>{error}</span>
            </div>

            <div className="auth-fields">
              <div className="field">
                <label className="field-label" htmlFor="email">
                  Email
                </label>
                <input
                  className="input"
                  id="email"
                  type="email"
                  placeholder="you@company.com"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className={"btn btn-spark btn-lg btn-block" + (loading ? " is-loading" : "")}
              style={{ marginTop: 24 }}
              disabled={loading || !email.trim()}
            >
              {loading ? <span className="spin" /> : "Send reset link"}
            </button>

            <p className="auth-switch" style={{ marginTop: 20 }}>
              Remembered it? <Link href="/login">Log in</Link>
            </p>
          </form>
        )}
      </section>
    </main>
  );
}
