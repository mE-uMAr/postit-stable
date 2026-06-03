"use client";

import { useEffect, useState } from "react";
import { Sparkle } from "@/components/Sparkle";
import { PlatformLogo } from "@/components/PlatformLogo";
import { prefersReducedMotion } from "@/lib/motion";
import type { PlatformKey } from "@/lib/types";

const IDEA = "Launching our spring collection 🌷";

interface DemoVariant {
  pf: PlatformKey;
  cls: string;
  name: string;
  handle: string;
  /** May contain inline markup (tags, <br>) — rendered as HTML. */
  body: string;
}

const VARIANTS: DemoVariant[] = [
  {
    pf: "x", cls: "pf-x", name: "X", handle: "@maplehome",
    body: 'Spring just dropped. 🌷 New collection live now — fresh palettes, lighter layers, zero compromise. <span class="tag">#SpringDrop #NewArrivals</span>',
  },
  {
    pf: "linkedin", cls: "pf-linkedin", name: "Maple & Co", handle: "Home goods · 1d",
    body: "We're thrilled to launch our Spring Collection today. Months of design work, lighter materials, and a palette built for longer days — now available to everyone.",
  },
  {
    pf: "instagram", cls: "pf-instagram", name: "maple.home", handle: "Original audio",
    body: "spring is here 🌷✨<br>our new collection just landed<br><br>tap the link in bio to shop early →",
  },
  {
    pf: "threads", cls: "pf-threads", name: "maple.home", handle: "2m",
    body: "ok our spring collection is finally live and we could not be more obsessed 🌷 which piece are you grabbing first?",
  },
];

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

interface GenState {
  show: boolean;
  label: string;
  shimmer: boolean;
}

export function HeroDemo() {
  const [typed, setTyped] = useState("");
  const [caret, setCaret] = useState(false);
  const [gen, setGen] = useState<GenState>({ show: false, label: "", shimmer: false });
  const [shownCount, setShownCount] = useState(0);
  const [fade, setFade] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function run() {
      if (prefersReducedMotion()) {
        setTyped(IDEA);
        setShownCount(VARIANTS.length);
        return;
      }

      while (!cancelled) {
        // reset
        setShownCount(0);
        setGen({ show: false, label: "", shimmer: false });
        setFade(false);
        setTyped("");

        // type the idea
        setCaret(true);
        for (let i = 0; i < IDEA.length && !cancelled; i++) {
          setTyped(IDEA.slice(0, i + 1));
          await sleep(38 + Math.random() * 40);
        }
        await sleep(500);
        if (cancelled) return;
        setCaret(false);

        // generate
        setGen({ show: true, label: "Generating platform versions…", shimmer: true });
        await sleep(1400);
        if (cancelled) return;
        setGen({ show: true, label: "Generated 4 native posts", shimmer: false });

        // fan out the cards, 60ms stagger
        for (let i = 0; i < VARIANTS.length && !cancelled; i++) {
          setShownCount(i + 1);
          await sleep(60);
        }

        await sleep(4200);
        if (cancelled) return;
        // fade out and loop
        setFade(true);
        await sleep(600);
      }
    }

    run();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="demo" id="demo">
      <div className="demo-compose">
        <div className="dc-label">Your idea</div>
        <div className="dc-text" id="demoText">
          {typed}
          {caret && <span className="demo-caret" />}
        </div>
      </div>

      {gen.show && (
        <div className={"demo-genbar" + (gen.shimmer ? " shimmer" : "")} id="genbar">
          <Sparkle size={16} /> <span id="genlabel">{gen.label}</span>
        </div>
      )}

      <div
        className="demo-cards"
        id="demoCards"
        style={{ transition: "opacity .5s ease", opacity: fade ? 0 : 1 }}
      >
        {VARIANTS.slice(0, shownCount).map((v) => (
          <div key={v.pf} className="demo-card in">
            <div className="demo-card-head">
              <span className={"pf " + v.cls} style={{ width: 24, height: 24, borderRadius: 7, fontSize: 11 }}>
                <PlatformLogo platform={v.pf} />
              </span>
              <span className="nm">{v.name}</span>
              <span className="hd">{v.handle}</span>
            </div>
            <div className="demo-card-body" dangerouslySetInnerHTML={{ __html: v.body }} />
          </div>
        ))}
      </div>
    </div>
  );
}
