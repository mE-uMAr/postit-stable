import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

import { AuthIconSprite } from "@/components/auth/AuthIconSprite";
import { AuthForm } from "@/components/auth/AuthForm";
import { PlatformLogo } from "@/components/PlatformLogo";

import "@/styles/auth.css";

export const metadata: Metadata = {
  title: "Create your Postit account",
};

export default function SignupPage() {
  return (
    <>
      <AuthIconSprite />

      <main className="auth">
        {/* Brand panel */}
        <aside className="auth-brand">
          <Link href="/" className="wordmark">
            <span className="wm-text">Postit</span>
            <span className="wm-corner" />
          </Link>
          <div className="auth-brand-body">
            <h2>One idea in. Nine native posts out.</h2>
            <p>
              Connect your platforms after sign-up — it takes about a minute. Then write once and watch it go
              everywhere.
            </p>
            <div className="auth-stack">
              <div className="auth-pcard c1">
                <div className="h">
                  <span className="pf pf-x" style={{ width: 22, height: 22, borderRadius: 6 }}>
                    <PlatformLogo platform="x" />
                  </span>
                  <span className="nm">@maplehome</span>
                  <span className="hd">now</span>
                </div>
                <div className="b">Spring just dropped. 🌷 New collection live now. #SpringDrop</div>
              </div>
              <div className="auth-pcard c2">
                <div className="h">
                  <span className="pf pf-linkedin" style={{ width: 22, height: 22, borderRadius: 6 }}>
                    <PlatformLogo platform="linkedin" />
                  </span>
                  <span className="nm">Maple &amp; Co</span>
                  <span className="hd">1d</span>
                </div>
                <div className="b">
                  We&apos;re thrilled to launch our Spring Collection today — lighter materials, a brighter
                  palette.
                </div>
              </div>
              <div className="auth-pcard c3">
                <div className="h">
                  <span className="pf pf-instagram" style={{ width: 22, height: 22, borderRadius: 6 }}>
                    <PlatformLogo platform="instagram" />
                  </span>
                  <span className="nm">maple.home</span>
                  <span className="hd">2m</span>
                </div>
                <div className="b">spring is here 🌷✨ our new collection just landed →</div>
              </div>
            </div>
          </div>
          <div className="auth-brand-foot">Write once. Post everywhere. Sound native on each.</div>
        </aside>

        {/* Form */}
        <section className="auth-form-wrap">
          <Suspense fallback={null}>
            <AuthForm mode="signup" />
          </Suspense>
        </section>
      </main>
    </>
  );
}
