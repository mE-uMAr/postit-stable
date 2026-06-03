/* Browser-side API client. All calls go through the same-origin Next.js proxy
   (`/api/proxy/*`), which attaches the httpOnly access token + workspace header
   server-side and transparently refreshes on expiry. */

export class ApiError extends Error {
  status: number;
  code?: string;
  details?: unknown;

  constructor(status: number, message: string, code?: string, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

type Json = Record<string, unknown> | unknown[] | null;

async function request<T>(method: string, path: string, body?: Json): Promise<T> {
  const res = await fetch(`/api/proxy/${path.replace(/^\//, "")}`, {
    method,
    headers: body !== undefined ? { "Content-Type": "application/json" } : undefined,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    cache: "no-store",
  });

  if (res.status === 204) return undefined as T;

  let data: unknown = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!res.ok) {
    const err = (data as { error?: { message?: string; code?: string; details?: unknown } })?.error;
    throw new ApiError(
      res.status,
      err?.message || `Request failed (${res.status})`,
      err?.code,
      err?.details,
    );
  }
  return data as T;
}

export const api = {
  get: <T>(path: string) => request<T>("GET", path),
  post: <T>(path: string, body?: Json) => request<T>("POST", path, body ?? {}),
  put: <T>(path: string, body?: Json) => request<T>("PUT", path, body ?? {}),
  patch: <T>(path: string, body?: Json) => request<T>("PATCH", path, body ?? {}),
  del: <T>(path: string) => request<T>("DELETE", path),
};
