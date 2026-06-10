import type { Metadata } from "next";

import { LegalPage } from "@/components/landing/LegalPage";

export const metadata: Metadata = {
  title: "Privacy Policy - Postit",
  description: "How Postit collects, uses, and protects your data.",
};

export default function PrivacyPage() {
  return (
    <LegalPage title="Privacy Policy" updated="June 2026">
      <div className="legal-toc">
        <strong>On this page</strong>
        <a href="#info">Information we collect</a>
        <a href="#use">How we use it</a>
        <a href="#sharing">Sharing</a>
        <a href="#platforms">Connected platforms</a>
        <a href="#security">Security</a>
        <a href="#rights">Your rights</a>
        <a href="#contact">Contact</a>
      </div>

      <p>
        This Privacy Policy explains how Postit, Inc. (&quot;Postit&quot;, &quot;we&quot;, &quot;us&quot;)
        collects, uses, and safeguards information when you use our website and application (the
        &quot;Service&quot;). We keep it short and plain: we collect what we need to run the Service, we
        never sell your data, and you stay in control of your connected accounts.
      </p>

      <h2 id="info">1. Information we collect</h2>
      <h3>Account information</h3>
      <p>
        When you create an account we collect your name, email address, and a securely hashed password.
        If you create a workspace, we store its name and your role within it.
      </p>
      <h3>Content you create</h3>
      <p>
        Posts, drafts, media, brand-voice settings, and schedules you create in Postit are stored so we
        can generate platform-native versions and publish on your behalf.
      </p>
      <h3>Connected platform data</h3>
      <p>
        When you connect a social account we store the access tokens needed to publish, encrypted at
        rest. We request the minimum scopes required and never store your platform passwords.
      </p>
      <h3>Usage and device data</h3>
      <p>
        We collect basic technical data (IP address, browser type, request logs) to operate, secure, and
        improve the Service.
      </p>

      <h2 id="use">2. How we use information</h2>
      <ul>
        <li>To provide the Service: composing, scheduling, and publishing your posts.</li>
        <li>To generate platform-native rewrites using the AI provider you or your admin configure.</li>
        <li>To authenticate you, secure your account, and prevent abuse.</li>
        <li>To send service-related notifications you have enabled.</li>
        <li>To process billing through our payment processor.</li>
      </ul>

      <h2 id="sharing">3. How we share information</h2>
      <p>
        We do not sell your personal data. We share information only with service providers who help us
        operate the Service (hosting, payment processing, and the AI provider configured for your
        workspace), and when required by law. These providers are bound to use the data only to provide
        their services to us.
      </p>

      <h2 id="platforms">4. Connected platforms</h2>
      <p>
        Postit posts to third-party platforms (such as X, LinkedIn, Instagram, Threads, Facebook,
        TikTok, YouTube, WordPress, and Blogger) using the permissions you grant. You can disconnect any
        account at any time from the Connections page, which revokes the stored tokens. If a platform
        notifies us that you deauthorized Postit or requested deletion of your data, we promptly revoke
        the related connection and remove its tokens.
      </p>

      <h2 id="security">5. Data security</h2>
      <p>
        We protect your data with industry-standard measures, including encryption of stored OAuth
        tokens, hashed passwords (argon2), rotating session tokens with reuse detection, and access
        controls. No system is perfectly secure, but we work hard to keep yours safe.
      </p>

      <h2 id="rights">6. Your rights</h2>
      <p>
        You can access, correct, export, or delete your personal data. Deleting your account removes your
        personal information and revokes connected platform tokens. To exercise any of these rights,
        contact us using the details below.
      </p>

      <h2 id="retention">7. Data retention</h2>
      <p>
        We retain your data for as long as your account is active. When you delete your account, we
        remove or anonymize your personal data within a reasonable period, except where retention is
        required by law.
      </p>

      <h2 id="contact">8. Contact us</h2>
      <p>
        Questions about this policy or your data? Email us at{" "}
        <a href="mailto:privacy@postit.app">privacy@postit.app</a>.
      </p>
    </LegalPage>
  );
}
