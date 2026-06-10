import type { Metadata } from "next";

import { LegalPage } from "@/components/landing/LegalPage";

export const metadata: Metadata = {
  title: "Terms of Service - Postit",
  description: "The terms that govern your use of Postit.",
};

export default function TermsPage() {
  return (
    <LegalPage title="Terms of Service" updated="June 2026">
      <div className="legal-toc">
        <strong>On this page</strong>
        <a href="#acceptance">Acceptance</a>
        <a href="#accounts">Accounts</a>
        <a href="#acceptable">Acceptable use</a>
        <a href="#content">Your content</a>
        <a href="#billing">Billing</a>
        <a href="#termination">Termination</a>
        <a href="#liability">Liability</a>
        <a href="#contact">Contact</a>
      </div>

      <p>
        These Terms of Service (&quot;Terms&quot;) govern your access to and use of Postit, Inc.&apos;s
        website and application (the &quot;Service&quot;). By creating an account or using the Service you
        agree to these Terms. If you are using Postit on behalf of an organization, you agree on its
        behalf.
      </p>

      <h2 id="acceptance">1. Acceptance of terms</h2>
      <p>
        If you do not agree with these Terms, do not use the Service. We may update these Terms from time
        to time; continued use after changes take effect means you accept the revised Terms.
      </p>

      <h2 id="accounts">2. Your account</h2>
      <p>
        You are responsible for the activity under your account and for keeping your credentials secure.
        You must provide accurate information and be at least the age of majority in your jurisdiction.
        Workspace owners and admins are responsible for the members they invite and the roles they grant.
      </p>

      <h2 id="acceptable">3. Acceptable use</h2>
      <p>You agree not to use the Service to:</p>
      <ul>
        <li>Violate any law or the terms of a connected platform.</li>
        <li>Post spam, malware, or content that infringes others&apos; rights.</li>
        <li>Harass, abuse, or harm others, or publish unlawful or deceptive content.</li>
        <li>Attempt to disrupt, reverse-engineer, or gain unauthorized access to the Service.</li>
      </ul>
      <p>
        You are responsible for ensuring your content complies with the rules of each platform you
        publish to.
      </p>

      <h2 id="content">4. Your content</h2>
      <p>
        You retain ownership of the content you create. You grant Postit a limited license to store,
        process, and transmit that content solely to provide the Service, including generating
        platform-native versions and publishing on your behalf to the accounts you connect.
      </p>

      <h2 id="ai">5. AI-generated content</h2>
      <p>
        Postit can generate platform-native rewrites using an AI provider configured for your workspace.
        AI output may be inaccurate; you are responsible for reviewing content before it is published.
      </p>

      <h2 id="billing">6. Plans and billing</h2>
      <p>
        Paid plans and usage-based charges are billed through our payment processor. Fees are described
        at checkout and on our pricing page and may change with notice. Except where required by law,
        payments are non-refundable. You can cancel at any time; access continues until the end of the
        current billing period.
      </p>

      <h2 id="termination">7. Suspension and termination</h2>
      <p>
        You may stop using the Service and delete your account at any time. We may suspend or terminate
        access if you breach these Terms or use the Service in a way that risks harm to others or to the
        Service.
      </p>

      <h2 id="liability">8. Disclaimers and liability</h2>
      <p>
        The Service is provided &quot;as is&quot; without warranties of any kind. To the maximum extent
        permitted by law, Postit is not liable for indirect, incidental, or consequential damages, and our
        total liability is limited to the amount you paid us in the twelve months before the claim.
      </p>

      <h2 id="contact">9. Contact us</h2>
      <p>
        Questions about these Terms? Email us at <a href="mailto:legal@postit.app">legal@postit.app</a>.
      </p>
    </LegalPage>
  );
}
