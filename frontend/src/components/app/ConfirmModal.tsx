"use client";

import { Sparkle } from "@/components/Sparkle";
import { PlatformLogo } from "@/components/PlatformLogo";
import { PF } from "@/lib/platforms";
import type { PlatformKey } from "@/lib/types";

export type ConfirmMode = "post" | "schedule";

interface ConfirmModalProps {
  mode: ConfirmMode;
  platforms: PlatformKey[];
  onClose: () => void;
  onConfirm: () => void;
}

export function ConfirmModal({ mode, platforms, onClose, onConfirm }: ConfirmModalProps) {
  const isSchedule = mode === "schedule";
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h3>{isSchedule ? "Schedule this post?" : "Ready to publish?"}</h3>
          <p>
            {isSchedule
              ? "Postit will queue these for the suggested best time. Nothing posts until then."
              : "This will publish immediately to every platform below."}
          </p>
        </div>
        <div className="modal-body">
          {platforms.map((k) => (
            <div key={k} className="modal-pf-line">
              <span className={"pf " + PF[k].cls} style={{ width: 28, height: 28 }}>
                <PlatformLogo platform={k} />
              </span>
              <span className="nm">{PF[k].name}</span>
              <span className="st">{isSchedule ? "Tomorrow · 9:00 AM" : "Post now"}</span>
            </div>
          ))}
          {isSchedule && (
            <div
              style={{
                marginTop: 14,
                display: "flex",
                alignItems: "center",
                gap: 10,
                padding: "12px",
                background: "var(--ai-tint)",
                borderRadius: 10,
                fontSize: 13,
                color: "var(--ai)",
              }}
            >
              <Sparkle size={15} /> Best time suggested by Postit: <strong>Tomorrow, 9:00 AM</strong>
            </div>
          )}
        </div>
        <div className="modal-foot">
          <button className="btn btn-ghost" onClick={onClose}>
            Cancel
          </button>
          <button className="btn btn-spark" onClick={onConfirm}>
            {isSchedule ? "Schedule post" : "Publish now"}
          </button>
        </div>
      </div>
    </div>
  );
}
