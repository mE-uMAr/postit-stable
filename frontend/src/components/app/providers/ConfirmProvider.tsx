"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";

export interface ConfirmOptions {
  title: string;
  /** Supporting detail: what exactly will happen, and whether it's reversible. */
  body?: ReactNode;
  confirmLabel?: string;
  cancelLabel?: string;
  /** Red confirm button for destructive actions. */
  danger?: boolean;
}

type ConfirmFn = (opts: ConfirmOptions) => Promise<boolean>;

const ConfirmContext = createContext<ConfirmFn | null>(null);

export function ConfirmProvider({ children }: { children: ReactNode }) {
  const [opts, setOpts] = useState<ConfirmOptions | null>(null);
  const resolver = useRef<((v: boolean) => void) | null>(null);

  const confirm = useCallback<ConfirmFn>((o) => {
    setOpts(o);
    return new Promise<boolean>((resolve) => {
      resolver.current = resolve;
    });
  }, []);

  const close = useCallback((value: boolean) => {
    resolver.current?.(value);
    resolver.current = null;
    setOpts(null);
  }, []);

  // Esc cancels, Enter confirms while the dialog is open.
  useEffect(() => {
    if (!opts) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") close(false);
      if (e.key === "Enter") close(true);
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [opts, close]);

  return (
    <ConfirmContext.Provider value={confirm}>
      {children}
      {opts && (
        <div className="modal-overlay" onMouseDown={(e) => e.target === e.currentTarget && close(false)}>
          <div className="modal" role="alertdialog" aria-modal="true" aria-label={opts.title}>
            <div className="modal-head">
              <h3>{opts.title}</h3>
            </div>
            {opts.body && <div className="modal-body">{opts.body}</div>}
            <div className="modal-foot">
              <button className="btn btn-ghost" onClick={() => close(false)}>
                {opts.cancelLabel ?? "Cancel"}
              </button>
              <button
                className={"btn " + (opts.danger ? "btn-danger" : "btn-spark")}
                onClick={() => close(true)}
                autoFocus
              >
                {opts.confirmLabel ?? "Confirm"}
              </button>
            </div>
          </div>
        </div>
      )}
    </ConfirmContext.Provider>
  );
}

export function useConfirm(): ConfirmFn {
  const ctx = useContext(ConfirmContext);
  if (!ctx) throw new Error("useConfirm must be used within a ConfirmProvider");
  return ctx;
}
