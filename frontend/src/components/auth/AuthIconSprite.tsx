/** SVG symbol sprite for the auth pages (social glyphs + alert icon). */
export function AuthIconSprite() {
  return (
    <svg width="0" height="0" style={{ position: "absolute" }} aria-hidden="true">
      <symbol id="g-google" viewBox="0 0 24 24">
        <path fill="#4285F4" d="M22 12.2c0-.7-.06-1.4-.18-2.06H12v3.9h5.6a4.8 4.8 0 01-2.08 3.15v2.6h3.36C20.84 18 22 15.4 22 12.2z" />
        <path fill="#34A853" d="M12 22c2.8 0 5.16-.93 6.88-2.5l-3.36-2.6c-.93.62-2.12.99-3.52.99-2.7 0-5-1.82-5.82-4.27H2.7v2.68A10 10 0 0012 22z" />
        <path fill="#FBBC05" d="M6.18 13.62a6 6 0 010-3.84V7.1H2.7a10 10 0 000 9.2z" />
        <path fill="#EA4335" d="M12 5.5c1.52 0 2.88.52 3.96 1.55l2.96-2.96C17.16 2.42 14.8 1.5 12 1.5A10 10 0 002.7 7.1l3.48 2.68C7 7.32 9.3 5.5 12 5.5z" />
      </symbol>
      <symbol id="g-apple" viewBox="0 0 24 24">
        <path fill="currentColor" d="M16.4 12.6c0-2.2 1.8-3.3 1.9-3.36-1.04-1.5-2.65-1.72-3.22-1.74-1.37-.14-2.67.8-3.36.8-.7 0-1.76-.78-2.9-.76-1.49.02-2.87.87-3.64 2.2-1.55 2.7-.4 6.68 1.11 8.87.74 1.07 1.62 2.27 2.77 2.23 1.11-.05 1.53-.72 2.88-.72 1.34 0 1.72.72 2.9.7 1.2-.02 1.96-1.09 2.69-2.17.85-1.24 1.2-2.45 1.22-2.51-.03-.01-2.34-.9-2.36-3.57zM14.2 5.9c.6-.74 1.02-1.76.9-2.78-.88.04-1.94.59-2.57 1.32-.56.65-1.06 1.69-.93 2.69.98.08 1.99-.5 2.6-1.23z" />
      </symbol>
      <symbol id="i-alert" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="9" />
        <path d="M12 8v5M12 16h.01" />
      </symbol>
    </svg>
  );
}
