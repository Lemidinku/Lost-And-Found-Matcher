import type { MatchResult, ReportCreate, ReportRead } from "./types";

const BASE_URL = "http://localhost:8000";

/**
 * Extracts a human-readable message from a FastAPI error body.
 * Simple errors (404s, etc.) come back as `{"detail": "some message"}`.
 * Validation errors (422s) come back as `{"detail": [{"loc": [...], "msg": "...", ...}, ...]}`.
 */
function extractErrorMessage(body: unknown, fallback: string): string {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as { detail: unknown }).detail;
    if (typeof detail === "string") {
      return detail;
    }
    if (Array.isArray(detail)) {
      return detail
        .map((item) =>
          item && typeof item === "object" && "msg" in item
            ? String((item as { msg: unknown }).msg)
            : JSON.stringify(item)
        )
        .join("; ");
    }
    if (detail !== undefined) {
      return JSON.stringify(detail);
    }
  }
  return fallback;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: init?.body ? { "Content-Type": "application/json" } : undefined,
    ...init,
  });

  if (!response.ok) {
    let body: unknown;
    try {
      body = await response.json();
    } catch {
      body = undefined;
    }
    throw new Error(extractErrorMessage(body, `Request failed with status ${response.status}`));
  }

  // No content responses (unused today, but safe for future endpoints).
  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export function createReport(data: ReportCreate): Promise<ReportRead> {
  return request<ReportRead>("/reports", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function listReports(filters?: {
  reportType?: string;
  status?: string;
}): Promise<ReportRead[]> {
  const params = new URLSearchParams();
  if (filters?.reportType) {
    params.set("report_type", filters.reportType);
  }
  if (filters?.status) {
    params.set("status", filters.status);
  }
  const query = params.toString();
  return request<ReportRead[]>(`/reports${query ? `?${query}` : ""}`);
}

export function getReport(id: number): Promise<ReportRead> {
  return request<ReportRead>(`/reports/${id}`);
}

export function getMatches(id: number): Promise<MatchResult[]> {
  return request<MatchResult[]>(`/reports/${id}/matches`);
}

export function resolveReport(id: number): Promise<ReportRead> {
  return request<ReportRead>(`/reports/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ status: "resolved" }),
  });
}
