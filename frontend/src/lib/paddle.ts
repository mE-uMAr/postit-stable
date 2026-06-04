/* Loads Paddle.js (v2) on demand and opens the checkout overlay for a transaction. */

interface PaddleGlobal {
  Environment: { set: (env: string) => void };
  Initialize: (opts: { token: string }) => void;
  Checkout: { open: (opts: Record<string, unknown>) => void };
}

declare global {
  interface Window {
    Paddle?: PaddleGlobal;
  }
}

const SCRIPT_SRC = "https://cdn.paddle.com/paddle/v2/paddle.js";

let loadPromise: Promise<PaddleGlobal> | null = null;
let initialized = false;

function loadScript(): Promise<PaddleGlobal> {
  if (typeof window === "undefined") return Promise.reject(new Error("Paddle requires a browser."));
  if (window.Paddle) return Promise.resolve(window.Paddle);
  if (loadPromise) return loadPromise;

  loadPromise = new Promise<PaddleGlobal>((resolve, reject) => {
    const s = document.createElement("script");
    s.src = SCRIPT_SRC;
    s.async = true;
    s.onload = () => (window.Paddle ? resolve(window.Paddle) : reject(new Error("Paddle failed to load.")));
    s.onerror = () => reject(new Error("Couldn't load Paddle.js."));
    document.head.appendChild(s);
  });
  return loadPromise;
}

export async function openPaddleCheckout(opts: {
  transactionId: string;
  clientToken: string | null;
  environment: string;
  successUrl?: string;
}): Promise<void> {
  if (!opts.clientToken) {
    throw new Error("Paddle isn't configured (missing client token).");
  }
  const Paddle = await loadScript();
  if (!initialized) {
    Paddle.Environment.set(opts.environment === "production" ? "production" : "sandbox");
    Paddle.Initialize({ token: opts.clientToken });
    initialized = true;
  }
  Paddle.Checkout.open({
    transactionId: opts.transactionId,
    settings: opts.successUrl ? { successUrl: opts.successUrl, displayMode: "overlay" } : { displayMode: "overlay" },
  });
}
