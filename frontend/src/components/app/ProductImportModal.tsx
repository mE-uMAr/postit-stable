"use client";

import { useEffect, useRef, useState } from "react";
import { SiAlibabadotcom, SiAliexpress } from "react-icons/si";
import { Icon } from "@/components/Icon";
import { api } from "@/lib/api/client";
import { errorMessage } from "@/lib/api/useApi";
import type { ProductCard, ProductDetail, ProductSearchResult, ProductSourceId } from "@/lib/api/types";
import { useToast } from "./providers/ToastProvider";

const SOURCE_META: Record<ProductSourceId, { name: string; Logo: typeof SiAliexpress; color: string }> = {
  alibaba: { name: "Alibaba", Logo: SiAlibabadotcom, color: "#FF6A00" },
  aliexpress: { name: "AliExpress", Logo: SiAliexpress, color: "#E62E04" },
};

interface ProductImportModalProps {
  source: ProductSourceId;
  onClose: () => void;
  onImport: (detail: ProductDetail) => Promise<void>;
}

export function ProductImportModal({ source, onClose, onImport }: ProductImportModalProps) {
  const pushToast = useToast();
  const meta = SOURCE_META[source];
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<ProductCard[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [importingId, setImportingId] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !importingId) onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose, importingId]);

  const runSearch = async () => {
    const q = query.trim();
    if (!q || loading) return;
    setLoading(true);
    setSearched(true);
    try {
      const res = await api.get<ProductSearchResult>(
        `products/${source}/search?q=${encodeURIComponent(q)}`,
      );
      setResults(res.items);
    } catch (e) {
      setResults([]);
      pushToast(errorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  const importProduct = async (card: ProductCard) => {
    if (importingId || !card.url) return;
    setImportingId(card.product_id);
    try {
      const detail = await api.get<ProductDetail>(
        `products/${source}/detail?url=${encodeURIComponent(card.url)}`,
      );
      await onImport(detail);
      onClose();
    } catch (e) {
      pushToast(errorMessage(e));
      setImportingId(null);
    }
  };

  const Logo = meta.Logo;

  return (
    <div className="pim-overlay" onClick={() => !importingId && onClose()}>
      <div className="pim-modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
        <div className="pim-head">
          <span className="pim-brand" style={{ background: meta.color }}>
            <Logo />
          </span>
          <div className="pim-title">Import from {meta.name}</div>
          <button className="pim-close" onClick={onClose} disabled={!!importingId} aria-label="Close">
            <Icon name="x" size={18} />
          </button>
        </div>

        <div className="pim-search">
          <Icon name="search" size={16} />
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && runSearch()}
            placeholder={`Search ${meta.name} products by keyword…`}
          />
          <button className="btn btn-spark" onClick={runSearch} disabled={loading || !query.trim()}>
            {loading ? <span className="spin" /> : "Search"}
          </button>
        </div>

        <div className="pim-body">
          {loading && (
            <div className="pim-grid">
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="pim-card pim-skel" />
              ))}
            </div>
          )}

          {!loading && results.length > 0 && (
            <div className="pim-grid">
              {results.map((p) => {
                const busy = importingId === p.product_id;
                return (
                  <button
                    key={p.product_id}
                    className={"pim-card" + (busy ? " is-busy" : "")}
                    onClick={() => importProduct(p)}
                    disabled={!!importingId}
                    title={p.title}
                  >
                    <div className="pim-thumb">
                      {p.image ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={p.image} alt="" loading="lazy" />
                      ) : (
                        <Icon name="image" size={22} />
                      )}
                      {busy && (
                        <div className="pim-busy">
                          <span className="spin" /> Importing…
                        </div>
                      )}
                    </div>
                    <div className="pim-card-title">{p.title}</div>
                    {p.price && (
                      <div className="pim-card-price">
                        {p.currency ? `${p.currency} ` : ""}
                        {p.price}
                      </div>
                    )}
                    <span className="pim-card-cta">
                      <Icon name="plus" size={13} /> Add to post
                    </span>
                  </button>
                );
              })}
            </div>
          )}

          {!loading && searched && results.length === 0 && (
            <div className="pim-empty">No products found. Try another keyword.</div>
          )}
          {!loading && !searched && (
            <div className="pim-empty">
              Search {meta.name} to pull a product&apos;s images, video and affiliate link straight into
              your post.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
