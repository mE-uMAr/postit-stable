// import type { Metadata } from "next";
// import type { ReactNode } from "react";

// import "@/styles/tokens.css";
// import "@/styles/components.css";
// import "@/styles/globals.css";
// import "@/styles/enhancements.css";

// export const metadata: Metadata = {
//   title: "Postit - Write it once. Postit everywhere.",
//   description:
//     "One idea in, nine native posts out. Postit's AI rewrites and reformats your post for every platform - then publishes on your schedule.",
//   icons: {
//     icon: "/icon.svg",
//     shortcut: "/icon.svg",
//     apple: "/icon.svg",
//   },
//   openGraph: {
//     title: "Postit - Write it once. Postit everywhere.",
//     description:
//       "One idea in, nine native posts out. Postit's AI rewrites and reformats your post for every platform - then publishes on your schedule.",
//     images: ["/logo.svg"],
//   },
// };

// export default function RootLayout({ children }: { children: ReactNode }) {
//   return (
//     <html lang="en">
//       <body>
//         {/* Fonts: General Sans (Fontshare), Inter + JetBrains Mono (Google).
//             Rendered here and hoisted into <head> by React. */}
//         <link rel="preconnect" href="https://fonts.googleapis.com" />
//         <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
//         <link
//           rel="stylesheet"
//           href="https://fonts.googleapis.com/css2?family=Inter:wght@400;450;500;600;700&family=JetBrains+Mono:wght@500&display=swap"
//         />
//         <link
//           rel="stylesheet"
//           href="https://api.fontshare.com/v2/css?f[]=general-sans@400,500,600,700&display=swap"
//         />
//         {children}
//       </body>
//     </html>
//   );
// }






import type { Metadata } from "next";
import type { ReactNode } from "react";

import "@/styles/tokens.css";
import "@/styles/components.css";
import "@/styles/globals.css";
import "@/styles/enhancements.css";

export const metadata: Metadata = {
  title: "Postit - Write it once. Postit everywhere.",
  description:
    "One idea in, nine native posts out. Postit's AI rewrites and reformats your post for every platform - then publishes on your schedule.",
  icons: {
    icon: "/icon.svg",
    shortcut: "/icon.svg",
    apple: "/icon.svg",
  },
  openGraph: {
    title: "Postit - Write it once. Postit everywhere.",
    description:
      "One idea in, nine native posts out. Postit's AI rewrites and reformats your post for every platform - then publishes on your schedule.",
    images: ["/logo.svg"],
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Service Suspended — Hosting Renewal Required</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700;800&display=swap');

  :root {
    --bg: #0B0E11;
    --panel: #12161B;
    --border: #232A32;
    --text-primary: #E6E9EC;
    --text-muted: #7C8891;
    --status-down: #E5484D;
    --status-down-dim: #4A2224;
    --status-up: #3DD68C;
    --accent: #F2A544;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
    background-image:
      radial-gradient(circle at 15% 10%, rgba(229,72,77,0.06), transparent 40%),
      radial-gradient(circle at 85% 90%, rgba(61,214,140,0.03), transparent 40%);
  }

  .card {
    width: 100%;
    max-width: 560px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 40px 80px -20px rgba(0,0,0,0.6);
  }

  /* Top bar mimicking a terminal / status console */
  .console-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 18px;
    background: #0E1216;
    border-bottom: 1px solid var(--border);
  }

  .console-dots { display: flex; gap: 7px; }
  .console-dots span {
    width: 10px; height: 10px; border-radius: 50%;
    background: #2A323A;
  }

  .console-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--text-muted);
    letter-spacing: 0.04em;
  }

  .status-log {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12.5px;
    line-height: 1.9;
    padding: 20px 24px;
    background: #0E1216;
    border-bottom: 1px solid var(--border);
  }

  .status-log .line { color: var(--text-muted); }
  .status-log .ok { color: var(--status-up); }
  .status-log .fail { color: var(--status-down); font-weight: 700; }
  .status-log .dim { color: #4A535C; }

  .body-content {
    padding: 36px 32px 32px;
  }

  .status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    border-radius: 100px;
    background: var(--status-down-dim);
    border: 1px solid rgba(229,72,77,0.35);
    font-family: 'JetBrains Mono', monospace;
    font-size: 11.5px;
    font-weight: 500;
    color: var(--status-down);
    letter-spacing: 0.03em;
    text-transform: uppercase;
    margin-bottom: 22px;
  }

  .status-pill .dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--status-down);
    box-shadow: 0 0 0 3px rgba(229,72,77,0.2);
  }

  h1 {
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -0.01em;
    line-height: 1.25;
    margin-bottom: 10px;
  }

  .subtext {
    color: var(--text-muted);
    font-size: 14.5px;
    line-height: 1.6;
    margin-bottom: 28px;
    max-width: 46ch;
  }

  .invoice-panel {
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 28px;
  }

  .invoice-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 18px;
    font-size: 13.5px;
  }

  .invoice-row + .invoice-row {
    border-top: 1px solid var(--border);
  }

  .invoice-row .k { color: var(--text-muted); }
  .invoice-row .v { font-weight: 500; }
  .invoice-row .v.mono { font-family: 'JetBrains Mono', monospace; }

  .invoice-row.total {
    background: #161B21;
  }

  .invoice-row.total .k { color: var(--text-primary); font-weight: 600; }
  .invoice-row.total .v {
    font-family: 'JetBrains Mono', monospace;
    font-size: 18px;
    font-weight: 700;
    color: var(--accent);
  }

  .cta {
    display: block;
    width: 100%;
    text-align: center;
    background: var(--accent);
    color: #1A1300;
    font-weight: 700;
    font-size: 15px;
    padding: 15px;
    border-radius: 8px;
    text-decoration: none;
    border: none;
    cursor: pointer;
    transition: filter 0.15s ease, transform 0.15s ease;
  }

  .cta:hover { filter: brightness(1.08); transform: translateY(-1px); }
  .cta:focus-visible { outline: 2px solid #fff; outline-offset: 3px; }

  .fine-print {
    margin-top: 16px;
    font-size: 12px;
    color: #566069;
    text-align: center;
    line-height: 1.6;
  }

  .fine-print a { color: var(--text-muted); text-decoration: underline; }

  @media (max-width: 480px) {
    h1 { font-size: 22px; }
    .body-content { padding: 28px 22px 26px; }
  }

  @media (prefers-reduced-motion: no-preference) {
    .status-pill .dot { animation: pulse 1.8s ease-in-out infinite; }
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }
</style>
</head>
<body>

  <div class="card">
    <div class="console-bar">
      <div class="console-dots"><span></span><span></span><span></span></div>
      <div class="console-label">svc-status // hosting.uptime</div>
    </div>

    <div class="status-log">
      <div class="line">[boot] checking service <span class="dim">web-01, db-01, mail-01</span></div>
      <div class="line ok">[ok] all systems nominal — 179 days uptime</div>
      <div class="line fail">[fail] billing cycle ended — service held for renewal</div>
      <div class="line dim">[info] awaiting payment to resume</div>
    </div>

    <div class="body-content">
      <div class="status-pill"><span class="dot"></span>Hosting expired</div>

      <h1>Your hosting plan has expired.</h1>
      <p class="subtext">
        Your site and its services are currently paused. Renew now to bring everything back online — nothing changes on your end once payment clears.
      </p>

      <div class="invoice-panel">
        <div class="invoice-row">
          <span class="k">Plan</span>
          <span class="v">Standard Hosting — 6 months</span>
        </div>
        <div class="invoice-row">
          <span class="k">Status</span>
          <span class="v mono" style="color: var(--status-down);">EXPIRED</span>
        </div>
        <div class="invoice-row total">
          <span class="k">Amount due</span>
          <span class="v">Rs 4,500</span>
        </div>
      </div>

      <a href="#" class="cta">Pay Rs 4,500 to renew for 6 months</a>
      <p class="fine-print">Service resumes automatically within minutes of payment confirmation.<br>Questions about this invoice? <a href="#">Contact support</a></p>
    </div>
  </div>

</body>
</html>
);
}
