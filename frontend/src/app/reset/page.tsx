"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState, type FormEvent } from "react";

import { api } from "@/lib/api/client";
import { errorMessage } from "@/lib/api/useApi";

import "@/styles/auth.css";

function ResetForm() {
  const router = useRouter();
  const params = useSearchParams();
  const token = params.get("token") ?? "";

  const [pw, setPw] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    if (pw.length < 8) return setError("Use at least 8 characters.");
    if (pw !== confirm) return setError("Passwords don't match.");
    setLoading(true);
    try {
      await api.post("auth/reset", { token, new_password: pw });
      setDone(true);
      setTimeout(() => router.push("/login"), 1400);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="auth-form">
        <h1>Invalid link</h1>
        <p className="sub">This reset link is missing its token. Request a new one.</p>
        <p className="auth-switch" style={{ marginTop: 20 }}>
          <Link href="/forgot">Request a reset link</Link>
        </p>
      </div>
    );
  }

  if (done) {
    return (
      <div className="auth-form">
        <h1>Password updated</h1>
        <p className="sub">Redirecting you to log in…</p>
      </div>
    );
  }

  return (
    <form className="auth-form" onSubmit={onSubmit} noValidate>
      <h1>Choose a new password</h1>
      <p className="sub">Make it 8+ characters.</p>

      <div className={"error-banner" + (error ? " show" : "")}>
        <span>{error}</span>
      </div>

      <div className="auth-fields">
        <div className="field">
          <label className="field-label" htmlFor="pw">
            New password
          </label>
          <input
            className="input"
            id="pw"
            type="password"
            autoComplete="new-password"
            value={pw}
            onChange={(e) => setPw(e.target.value)}
          />
        </div>
        <div className="field">
          <label className="field-label" htmlFor="confirm">
            Confirm password
          </label>
          <input
            className="input"
            id="confirm"
            type="password"
            autoComplete="new-password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
          />
        </div>
      </div>

      <button
        type="submit"
        className={"btn btn-spark btn-lg btn-block" + (loading ? " is-loading" : "")}
        style={{ marginTop: 24 }}
        disabled={loading}
      >
        {loading ? <span className="spin" /> : "Update password"}
      </button>
    </form>
  );
}

export default function ResetPage() {
  return (
    <main className="auth">
      <section className="auth-form-wrap" style={{ margin: "0 auto" }}>
        <Suspense fallback={null}>
          <ResetForm />
        </Suspense>
      </section>
    </main>
  );
}
