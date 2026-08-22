import { useState } from "react";
import type { CSSProperties, FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { createReport } from "../api";
import type { Category, ReportType } from "../types";

const CATEGORIES: { value: Category; label: string }[] = [
  { value: "electronics", label: "Electronics" },
  { value: "bag", label: "Bag" },
  { value: "clothing", label: "Clothing" },
  { value: "accessory", label: "Accessory" },
  { value: "documents", label: "Documents" },
  { value: "keys", label: "Keys" },
  { value: "other", label: "Other" },
];

const inputStyle: CSSProperties = {
  width: "100%",
  padding: "10px 12px",
  borderRadius: "6px",
  border: "1px solid var(--border)",
  background: "var(--bg)",
  color: "var(--text-h)",
  font: "inherit",
  boxSizing: "border-box",
};

const labelStyle: CSSProperties = {
  display: "block",
  marginBottom: "6px",
  fontWeight: 500,
  color: "var(--text-h)",
};

const fieldWrapStyle: CSSProperties = {
  marginBottom: "18px",
};

/**
 * Converts a `datetime-local` input value (e.g. "2024-01-15T14:30", no
 * seconds, no timezone) into a full ISO-8601 string with seconds so the
 * backend's Pydantic `datetime` field parses it unambiguously.
 */
function toIsoWithSeconds(datetimeLocalValue: string): string {
  // datetime-local gives "YYYY-MM-DDTHH:mm" or "YYYY-MM-DDTHH:mm:ss".
  return datetimeLocalValue.length === 16 ? `${datetimeLocalValue}:00` : datetimeLocalValue;
}

function ReportForm() {
  const navigate = useNavigate();

  const [reportType, setReportType] = useState<ReportType>("lost");
  const [category, setCategory] = useState<Category>("electronics");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [color, setColor] = useState("");
  const [location, setLocation] = useState("");
  const [occurredAt, setOccurredAt] = useState("");
  const [reporterName, setReporterName] = useState("");
  const [reporterContact, setReporterContact] = useState("");

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const created = await createReport({
        report_type: reportType,
        category,
        title,
        description,
        color,
        location,
        occurred_at: toIsoWithSeconds(occurredAt),
        reporter_name: reporterName,
        reporter_contact: reporterContact,
      });
      navigate(`/reports/${created.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit report.");
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate={false}>
      <div style={fieldWrapStyle}>
        <span style={labelStyle}>Report type</span>
        <div role="radiogroup" aria-label="Report type" style={{ display: "flex", gap: "8px" }}>
          {(["lost", "found"] as ReportType[]).map((value) => (
            <button
              key={value}
              type="button"
              aria-pressed={reportType === value}
              onClick={() => setReportType(value)}
              style={{
                padding: "10px 20px",
                borderRadius: "6px",
                border: "1px solid var(--border)",
                background: reportType === value ? "var(--accent-bg)" : "transparent",
                color: reportType === value ? "var(--accent)" : "var(--text)",
                fontWeight: reportType === value ? 600 : 400,
                cursor: "pointer",
              }}
            >
              {value === "lost" ? "Lost" : "Found"}
            </button>
          ))}
        </div>
      </div>

      <div style={fieldWrapStyle}>
        <label style={labelStyle} htmlFor="category">
          Category
        </label>
        <select
          id="category"
          required
          value={category}
          onChange={(e) => setCategory(e.target.value as Category)}
          style={inputStyle}
        >
          {CATEGORIES.map(({ value, label }) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </div>

      <div style={fieldWrapStyle}>
        <label style={labelStyle} htmlFor="title">
          Title
        </label>
        <input
          id="title"
          type="text"
          required
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          style={inputStyle}
        />
      </div>

      <div style={fieldWrapStyle}>
        <label style={labelStyle} htmlFor="description">
          Description
        </label>
        <textarea
          id="description"
          required
          rows={4}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          style={{ ...inputStyle, resize: "vertical" }}
        />
      </div>

      <div style={fieldWrapStyle}>
        <label style={labelStyle} htmlFor="color">
          Color
        </label>
        <input
          id="color"
          type="text"
          required
          value={color}
          onChange={(e) => setColor(e.target.value)}
          style={inputStyle}
        />
      </div>

      <div style={fieldWrapStyle}>
        <label style={labelStyle} htmlFor="location">
          Location
        </label>
        <input
          id="location"
          type="text"
          required
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          style={inputStyle}
        />
      </div>

      <div style={fieldWrapStyle}>
        <label style={labelStyle} htmlFor="occurred_at">
          Date &amp; time
        </label>
        <input
          id="occurred_at"
          type="datetime-local"
          required
          value={occurredAt}
          onChange={(e) => setOccurredAt(e.target.value)}
          style={inputStyle}
        />
      </div>

      <div style={fieldWrapStyle}>
        <label style={labelStyle} htmlFor="reporter_name">
          Your name
        </label>
        <input
          id="reporter_name"
          type="text"
          required
          value={reporterName}
          onChange={(e) => setReporterName(e.target.value)}
          style={inputStyle}
        />
      </div>

      <div style={fieldWrapStyle}>
        <label style={labelStyle} htmlFor="reporter_contact">
          Contact info
        </label>
        <input
          id="reporter_contact"
          type="text"
          required
          value={reporterContact}
          onChange={(e) => setReporterContact(e.target.value)}
          style={inputStyle}
        />
      </div>

      {error && (
        <p role="alert" style={{ color: "#d33", marginBottom: "18px" }}>
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={isSubmitting}
        style={{
          padding: "10px 20px",
          borderRadius: "6px",
          border: "none",
          background: "var(--accent)",
          color: "var(--text-h)",
          fontWeight: 500,
          cursor: isSubmitting ? "default" : "pointer",
          opacity: isSubmitting ? 0.7 : 1,
        }}
      >
        {isSubmitting ? "Submitting…" : "Submit report"}
      </button>
    </form>
  );
}

export default ReportForm;
