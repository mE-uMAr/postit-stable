import Link from "next/link";

import { LandingIconSprite } from "@/components/landing/LandingIconSprite";
import { LandingNav } from "@/components/landing/LandingNav";
import { HeroDemo } from "@/components/landing/HeroDemo";
import { PricingTable } from "@/components/landing/PricingTable";
import { PlatformLogo } from "@/components/PlatformLogo";

import "@/styles/landing.css";

export default function LandingPage() {
  return (
    <>
      <LandingIconSprite />

      <LandingNav />

      {/* ===== Hero ===== */}
      <header className="hero lp-section lp-rhythm" style={{ paddingTop: 72 }}>
        <div className="hero-grid paper-grid" />
        <div className="hero-inner">
          <div className="hero-text">
            <div className="hero-eyebrow t-caption">AI-Powered Social Autopilot</div>
            <h1 className="t-display-xl">
              Write it once.
              <br />
              <span className="postit-word">Postit</span> everywhere.
            </h1>
            <p className="hero-sub t-body-l">
              One idea in, nine native posts out. Postit&apos;s AI rewrites and reformats your post for
              every platform — then publishes on your schedule. Stop copy-pasting. Start shipping.
            </p>
            <div className="hero-cta">
              <Link href="/signup" className="btn btn-spark btn-lg">
                Start free — no card needed
              </Link>
              <a href="#" className="btn btn-ghost btn-lg">
                <svg className="sparkle" style={{ width: 18, height: 18 }}>
                  <use href="#i-play" />
                </svg>{" "}
                Watch the 40-sec demo
              </a>
            </div>
            <div className="trust-strip">
              <div className="trust-logos">
                <span className="pf pf-facebook"><PlatformLogo platform="facebook" /></span>
                <span className="pf pf-instagram"><PlatformLogo platform="instagram" /></span>
                <span className="pf pf-threads"><PlatformLogo platform="threads" /></span>
                <span className="pf pf-linkedin"><PlatformLogo platform="linkedin" /></span>
                <span className="pf pf-x"><PlatformLogo platform="x" /></span>
                <span className="pf pf-youtube"><PlatformLogo platform="youtube" /></span>
                <span className="pf pf-tiktok"><PlatformLogo platform="tiktok" /></span>
                <span className="pf pf-blogger"><PlatformLogo platform="blogger" /></span>
                <span className="pf pf-wordpress"><PlatformLogo platform="wordpress" /></span>
              </div>
              <span className="t-caption" style={{ textTransform: "none", letterSpacing: 0 }}>
                Connect all your accounts in minutes.
              </span>
            </div>
          </div>

          {/* Hero demo */}
          <div className="hero-demo-wrap" style={{ position: "relative" }}>
            <div className="sticky-peek" />
            <HeroDemo />
          </div>
        </div>
      </header>

      {/* ===== Social proof ===== */}
      <section className="lp-section proof" style={{ padding: "48px 32px" }}>
        <div className="proof-label t-body-s">Trusted by 4,000+ creators, founders, and social teams</div>
        <div className="proof-row">
          <span className="proof-logo">Northwind</span>
          <span className="proof-logo">Lumen</span>
          <span className="proof-logo">Foundry</span>
          <span className="proof-logo">Maple&amp;Co</span>
          <span className="proof-logo">Beacon</span>
          <span className="proof-logo">Driftwood</span>
        </div>
      </section>

      {/* ===== Problem ===== */}
      <section className="lp-section lp-rhythm">
        <div className="problem">
          <h2 className="t-h1">Posting everywhere shouldn&apos;t take all morning.</h2>
          <div className="pain-list">
            <div className="pain-item">
              <span className="pain-icon">
                <svg width="20" height="20">
                  <use href="#i-copy" />
                </svg>
              </span>{" "}
              Rewriting the same post nine times.
            </div>
            <div className="pain-item">
              <span className="pain-icon">
                <svg width="20" height="20">
                  <use href="#i-shuffle" />
                </svg>
              </span>{" "}
              Reformatting for every platform&apos;s quirks.
            </div>
            <div className="pain-item">
              <span className="pain-icon">
                <svg width="20" height="20">
                  <use href="#i-keys" />
                </svg>
              </span>{" "}
              Juggling nine logins and nine schedulers.
            </div>
          </div>
        </div>
      </section>

      {/* ===== How it works ===== */}
      <section className="lp-section lp-rhythm" id="features">
        <div className="how-head">
          <div className="section-eyebrow" style={{ marginBottom: 14 }}>
            How it works
          </div>
          <h2 className="t-h1">From one idea to everywhere, in three steps.</h2>
        </div>
        <div className="steps">
          <div className="step-card">
            <div className="step-num">01</div>
            <div className="step-illus placeholder">composer illustration</div>
            <h3 className="t-h3">Write your idea</h3>
            <p>Drop one post into a single clean composer.</p>
            <svg className="step-arrow" width="28" height="28" style={{ right: -26 }}>
              <use href="#i-arrow" />
            </svg>
          </div>
          <div className="step-card">
            <div className="step-num">02</div>
            <div className="step-illus placeholder" style={{ backgroundColor: "var(--ai-tint)" }}>
              AI rewrite illustration
            </div>
            <h3 className="t-h3">
              AI makes it native{" "}
              <svg className="sparkle" style={{ color: "var(--ai)", width: 18, height: 18, verticalAlign: -2 }}>
                <use href="#i-spark" />
              </svg>
            </h3>
            <p>Postit rewrites tone, length, hashtags, and format for each platform.</p>
            <svg className="step-arrow" width="28" height="28" style={{ right: -26 }}>
              <use href="#i-arrow" />
            </svg>
          </div>
          <div className="step-card">
            <div className="step-num">03</div>
            <div className="step-illus placeholder">schedule illustration</div>
            <h3 className="t-h3">Publish or schedule</h3>
            <p>Hit post once. It goes live everywhere — or queues for the perfect time.</p>
          </div>
        </div>
      </section>

      {/* ===== Platform showcase ===== */}
      <section className="lp-section lp-rhythm" id="platforms">
        <div className="pf-head">
          <div className="section-eyebrow" style={{ marginBottom: 14 }}>
            Nine platforms
          </div>
          <h2 className="t-h1">Nine platforms. One composer.</h2>
        </div>
        <div className="pf-grid">
          <div className="pf-tile">
            <span className="pf pf-x"><PlatformLogo platform="x" /></span>
            <div className="pf-name">X</div>
            <div className="pf-cap">Punchy posts, threads &amp; live character ceiling.</div>
          </div>
          <div className="pf-tile">
            <span className="pf pf-linkedin"><PlatformLogo platform="linkedin" /></span>
            <div className="pf-name">LinkedIn</div>
            <div className="pf-cap">Long-form, professional tone, articles.</div>
          </div>
          <div className="pf-tile">
            <span className="pf pf-instagram"><PlatformLogo platform="instagram" /></span>
            <div className="pf-name">Instagram</div>
            <div className="pf-cap">Reels, image &amp; carousel — media required.</div>
          </div>
          <div className="pf-tile">
            <span className="pf pf-threads"><PlatformLogo platform="threads" /></span>
            <div className="pf-name">Threads</div>
            <div className="pf-cap">Conversational, casual, fast.</div>
          </div>
          <div className="pf-tile">
            <span className="pf pf-facebook"><PlatformLogo platform="facebook" /></span>
            <div className="pf-name">Facebook</div>
            <div className="pf-cap">Updates, links &amp; rich previews.</div>
          </div>
          <div className="pf-tile">
            <span className="pf pf-tiktok"><PlatformLogo platform="tiktok" /></span>
            <div className="pf-name">TikTok</div>
            <div className="pf-cap">Shorts &amp; video — needs a clip.</div>
          </div>
          <div className="pf-tile">
            <span className="pf pf-youtube"><PlatformLogo platform="youtube" /></span>
            <div className="pf-name">YouTube</div>
            <div className="pf-cap">Shorts &amp; video descriptions.</div>
          </div>
          <div className="pf-tile">
            <span className="pf pf-wordpress"><PlatformLogo platform="wordpress" /></span>
            <div className="pf-name">WordPress</div>
            <div className="pf-cap">Articles with title, tags &amp; category.</div>
          </div>
          <div className="pf-tile">
            <span className="pf pf-blogger"><PlatformLogo platform="blogger" /></span>
            <div className="pf-name">Blogger</div>
            <div className="pf-cap">Long-form posts &amp; labels.</div>
          </div>
        </div>
        <div className="pf-callout">
          <svg className="ico" width="24" height="24">
            <use href="#i-shield" />
          </svg>
          <span>
            <strong>Postit knows the rules.</strong> It auto-disables TikTok for image-only posts, flags X
            character limits, and resizes media per network — so nothing breaks on the way out.
          </span>
        </div>
      </section>

      {/* ===== Feature deep-dives ===== */}
      <section className="lp-section lp-rhythm">
        <div className="feat-row">
          <div className="feat-text">
            <span className="badge badge-spark">
              <span className="badge-dot" /> Compose
            </span>
            <h3>One canvas, live multi-platform preview.</h3>
            <p>
              See every post as it&apos;ll actually look on each network, before it goes out. No guessing, no
              surprise truncation.
            </p>
          </div>
          <div className="feat-shot placeholder">compose screen — product shot</div>
        </div>
        <div className="feat-row reverse">
          <div className="feat-text">
            <span className="badge badge-ai">
              <svg className="sparkle" style={{ width: 13, height: 13 }}>
                <use href="#i-spark" />
              </svg>{" "}
              AI voice
            </span>
            <h3>AI that sounds like you.</h3>
            <p>
              Tone controls, brand voice, and regenerate-per-platform. Tune your voice once; Postit keeps it
              consistent everywhere.
            </p>
          </div>
          <div className="feat-shot placeholder" style={{ backgroundColor: "var(--ai-tint)" }}>
            brand-voice panel — product shot
          </div>
        </div>
        <div className="feat-row">
          <div className="feat-text">
            <span className="badge badge-spark">
              <span className="badge-dot" /> Schedule
            </span>
            <h3>Plan a week in one sitting.</h3>
            <p>
              Drag-to-schedule, best-time suggestions, and a smart queue. Build your calendar once and let it
              run.
            </p>
          </div>
          <div className="feat-shot placeholder">calendar — product shot</div>
        </div>
        <div className="feat-row reverse">
          <div className="feat-text">
            <span className="badge badge-spark">
              <span className="badge-dot" /> Connections
            </span>
            <h3>Real connections. No surprises.</h3>
            <p>
              Secure OAuth, clear permissions, and status at a glance. You always know exactly what posts
              where.
            </p>
          </div>
          <div className="feat-shot placeholder">connections — product shot</div>
        </div>
      </section>

      {/* ===== Stats band ===== */}
      <section className="lp-section" style={{ padding: "48px 32px" }}>
        <div className="stats-band">
          <div className="stats-grid">
            <div>
              <div className="stat-num">9×</div>
              <div className="stat-label">fewer copy-pastes</div>
            </div>
            <div>
              <div className="stat-num">Minutes</div>
              <div className="stat-label">not mornings</div>
            </div>
            <div>
              <div className="stat-num">1</div>
              <div className="stat-label">composer to rule them all</div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== Testimonials ===== */}
      <section className="lp-section lp-rhythm">
        <div className="tst-head">
          <div className="section-eyebrow" style={{ marginBottom: 14 }}>
            Loved by busy people
          </div>
          <h2 className="t-h1">The morning copy-paste ritual is over.</h2>
        </div>
        <div className="tst-grid">
          <div className="tst-card">
            <p className="tst-quote">
              &quot;I used to block 45 minutes every launch just to reformat one announcement. Now it&apos;s one
              draft and I&apos;m done before my coffee&apos;s cold.&quot;
            </p>
            <div className="tst-who">
              <div className="tst-avatar">RA</div>
              <div>
                <div className="tst-name">Rina Alvarez</div>
                <div className="tst-role">Founder, Maple &amp; Co</div>
              </div>
            </div>
          </div>
          <div className="tst-card">
            <p className="tst-quote">
              &quot;The per-platform rewrites genuinely sound native. My LinkedIn posts read like LinkedIn, my X
              posts read like X. That used to be my whole job.&quot;
            </p>
            <div className="tst-who">
              <div className="tst-avatar">DO</div>
              <div>
                <div className="tst-name">Devon Okafor</div>
                <div className="tst-role">Creator, 280k followers</div>
              </div>
            </div>
          </div>
          <div className="tst-card">
            <p className="tst-quote">
              &quot;Our three-person social team plans a full week in one sitting now. The smart queue and
              best-time slots do the heavy lifting.&quot;
            </p>
            <div className="tst-who">
              <div className="tst-avatar">SK</div>
              <div>
                <div className="tst-name">Sana Kapoor</div>
                <div className="tst-role">Social Lead, Beacon</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== Pricing ===== */}
      <PricingTable />

      {/* ===== Final CTA ===== */}
      <section className="lp-section">
        <div className="final-cta">
          <div className="sticky-peek" />
          <div className="sticky-peek two" />
          <h2 className="t-display-l">Your next post is already nine posts.</h2>
          <p className="sub">Write the idea once. Let Postit make it native everywhere.</p>
          <Link href="/signup" className="btn btn-spark btn-lg">
            Start free
          </Link>
          <p className="reassure t-body-s">Free forever plan · No credit card · Connect in minutes.</p>
        </div>
      </section>

      {/* ===== Footer ===== */}
      <footer className="footer">
        <div className="footer-inner">
          <div className="footer-cols">
            <div className="footer-brand">
              <Link href="/" className="wordmark" style={{ fontSize: 22 }}>
                <span className="wm-text">Postit</span>
                <span className="wm-corner" />
              </Link>
              <p className="tagline">Write once. Post everywhere. Sound native on each.</p>
            </div>
            <div className="footer-col">
              <h4>Product</h4>
              <a href="#features">Features</a>
              <a href="#pricing">Pricing</a>
              <Link href="/app">Open app</Link>
              <a href="#">Changelog</a>
            </div>
            <div className="footer-col">
              <h4>Platforms</h4>
              <a href="#platforms">All networks</a>
              <a href="#">Integrations</a>
              <a href="#">API</a>
            </div>
            <div className="footer-col">
              <h4>Company</h4>
              <a href="#">About</a>
              <a href="#">Blog</a>
              <a href="#">Careers</a>
            </div>
            <div className="footer-col">
              <h4>Resources</h4>
              <a href="#">Help center</a>
              <a href="#">Privacy</a>
              <a href="#">Terms</a>
            </div>
          </div>
          <div className="footer-legal">
            <span>© 2026 Postit, Inc.</span>
            <span className="spacer" />
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
            <a href="#">Status</a>
          </div>
        </div>
      </footer>
    </>
  );
}
