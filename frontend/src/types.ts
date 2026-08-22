/**
 * TypeScript mirrors of the backend Pydantic schemas (backend/app/schemas.py,
 * backend/app/models.py). Keep field names and types in lockstep with those.
 */

export type ReportType = "lost" | "found";

export type Category =
  | "electronics"
  | "bag"
  | "clothing"
  | "accessory"
  | "documents"
  | "keys"
  | "other";

export type Status = "open" | "resolved";

/** Body for POST /reports. All Report fields except server-generated ones. */
export interface ReportCreate {
  report_type: ReportType;
  category: Category;
  title: string;
  description: string;
  color: string;
  location: string;
  occurred_at: string;
  reporter_name: string;
  reporter_contact: string;
}

/** Response shape for a Report: every field, including server-generated ones. */
export interface ReportRead {
  id: number;
  report_type: ReportType;
  category: Category;
  title: string;
  description: string;
  color: string;
  location: string;
  occurred_at: string;
  reporter_name: string;
  reporter_contact: string;
  status: Status;
  created_at: string;
}

/** Tier bucket assigned to a scored candidate match. */
export type MatchTier = "Strong" | "Possible" | "Weak" | "Hidden";

/** One scored candidate returned by GET /reports/{id}/matches. */
export interface MatchResult {
  report: ReportRead;
  score: number;
  tier: MatchTier;
  reason: string;
}
