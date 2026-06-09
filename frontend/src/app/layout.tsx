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
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        {/* Fonts: General Sans (Fontshare), Inter + JetBrains Mono (Google).
            Rendered here and hoisted into <head> by React. */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;450;500;600;700&family=JetBrains+Mono:wght@500&display=swap"
        />
        <link
          rel="stylesheet"
          href="https://api.fontshare.com/v2/css?f[]=general-sans@400,500,600,700&display=swap"
        />
        {children}
      </body>
    </html>
  );
}
