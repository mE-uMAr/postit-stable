import Link from "next/link";

export function LandingFooter() {
  return (
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
            <Link href="/#features">Features</Link>
            <Link href="/pricing">Pricing</Link>
            <Link href="/app">Open app</Link>
          </div>
          <div className="footer-col">
            <h4>Company</h4>
            <Link href="/login">Log in</Link>
            <Link href="/signup">Sign up</Link>
          </div>
          <div className="footer-col">
            <h4>Legal</h4>
            <Link href="/privacy">Privacy Policy</Link>
            <Link href="/terms">Terms of Service</Link>
          </div>
        </div>
        <div className="footer-legal">
          <span>© {new Date().getFullYear()} Postit, Inc. All rights reserved.</span>
          <span className="spacer" />
          <Link href="/privacy">Privacy</Link>
          <Link href="/terms">Terms</Link>
        </div>
      </div>
    </footer>
  );
}
