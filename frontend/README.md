# Postit

> Write it once. Postit everywhere, an AI social cross-posting product UI.

This is a [Next.js](https://nextjs.org) (App Router + TypeScript) application, converted
from a static HTML/CSS + in-browser-Babel React prototype into a fully structured project.

## Getting started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Scripts

| Script          | Description                          |
| --------------- | ------------------------------------ |
| `npm run dev`   | Start the dev server (Turbopack/Webpack) |
| `npm run build` | Production build                     |
| `npm run start` | Serve the production build           |
| `npm run lint`  | Run ESLint (`next/core-web-vitals`)  |

## Routes

| Path                 | What it is                                         |
| -------------------- | -------------------------------------------------- |
| `/`                  | Marketing landing page (animated hero demo, pricing) |
| `/login`             | Log in                                             |
| `/signup`            | Create account                                     |
| `/app`               | Redirects to `/app/compose`                        |
| `/app/compose`       | The composer + live multi-platform preview         |
| `/app/calendar`      | Scheduling calendar / queue                        |
| `/app/posts`         | Post history                                       |
| `/app/connections`   | Connected platform accounts                        |
| `/app/analytics`     | Reach & engagement                                 |
| `/app/settings`      | Profile, team, brand voice, billing, notifications |

The auth forms are mock — submitting either one navigates to `/app/compose`.

## Project structure

```
src/
├── app/
│   ├── layout.tsx              # Root layout: <html>, fonts, global CSS, metadata
│   ├── page.tsx                # Landing page (/)
│   ├── login/page.tsx
│   ├── signup/page.tsx
│   └── app/
│       ├── layout.tsx          # Dashboard shell: Theme + Toast providers, no-flash script
│       ├── page.tsx            # Redirects to /app/compose
│       ├── compose/page.tsx
│       ├── calendar/page.tsx
│       ├── posts/page.tsx
│       ├── connections/page.tsx
│       ├── analytics/page.tsx
│       └── settings/page.tsx
├── components/
│   ├── Icon.tsx                # Inline-path icon set
│   ├── Sparkle.tsx
│   ├── landing/                # LandingNav, HeroDemo, PricingTable, icon sprite
│   ├── auth/                   # AuthForm (login + signup), icon sprite
│   └── app/                    # AppShell, Sidebar, Topbar, the 6 views, providers
├── lib/
│   ├── types.ts                # Platform / domain types
│   ├── platforms.ts            # PLATFORMS, PF lookup, eligibility()
│   ├── rewrite.ts              # Heuristic per-platform rewrite engine
│   ├── icons.ts                # Icon path data
│   └── motion.ts               # prefersReducedMotion()
└── styles/                     # Design tokens + component/page CSS (verbatim from prototype)
```

## Notes

- **Theming** (light/dark) is app-only, persisted to `localStorage` (`postit-theme`) and
  applied via a small no-flash `<head>` script in the dashboard layout.
- The "AI" rewrite is a deterministic heuristic in `src/lib/rewrite.ts` — there is no real model call.
