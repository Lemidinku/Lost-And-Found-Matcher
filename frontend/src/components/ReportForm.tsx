import { useState } from "react";
import type { FormEvent } from "react";
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

const inputClass =
  "w-full rounded-md border border-ink/15 bg-paper px-3 py-2 text-ink placeholder:text-ink/30 focus:border-stamp-green focus:outline-none focus:ring-2 focus:ring-stamp-green/40";
const labelClass = "mb-1.5 block font-medium text-ink";
const fieldClass = "mb-5";

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
    <form onSubmit={handleSubmit}>
      <div className={fieldClass}>
        <span className={labelClass}>Report type</span>
        <div role="radiogroup" aria-label="Report type" className="flex gap-2">
          {(["lost", "found"] as ReportType[]).map((value) => {
            const active = reportType === value;
            const activeColor =
              value === "lost"
                ? "border-stamp-red bg-stamp-red/10 text-stamp-red"
                : "border-stamp-green bg-stamp-green/10 text-stamp-green";
            return (
              <button
                key={value}
                type="button"
                role="radio"
                aria-checked={active}
                onClick={() => setReportType(value)}
                className={`flex-1 rounded-md border-2 px-4 py-2.5 font-display font-semibold capitalize transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stamp-green ${
                  active ? activeColor : "border-ink/15 text-ink/50 hover:border-ink/30"
                }`}
              >
                {value}
              </button>
            );
          })}
        </div>
      </div>

      <div className={fieldClass}>
        <label className={labelClass} htmlFor="category">
          Category
        </label>
        <select
          id="category"
          required
          value={category}
          onChange={(e) => setCategory(e.target.value as Category)}
          className={inputClass}
        >
          {CATEGORIES.map(({ value, label }) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </div>

      <div className={fieldClass}>
        <label className={labelClass} htmlFor="title">
          Title
        </label>
        <input
          id="title"
          type="text"
          required
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className={inputClass}
          placeholder="Black backpack"
        />
      </div>

      <div className={fieldClass}>
        <label className={labelClass} htmlFor="description">
          Description
        </label>
        <textarea
          id="description"
          required
          rows={4}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className={`${inputClass} resize-y`}
          placeholder="Black backpack containing a laptop charger. Lost around the library on Monday afternoon."
        />
      </div>

      <div className={fieldClass}>
        <label className={labelClass} htmlFor="color">
          Colour
        </label>
        <input
          id="color"
          type="text"
          required
          value={color}
          onChange={(e) => setColor(e.target.value)}
          className={inputClass}
          placeholder="Black"
        />
      </div>

      <div className={fieldClass}>
        <label className={labelClass} htmlFor="location">
          Location
        </label>
        <input
          id="location"
          type="text"
          required
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          className={inputClass}
          placeholder="Library"
        />
      </div>

      <div className={fieldClass}>
        <label className={labelClass} htmlFor="occurred_at">
          Date &amp; time
        </label>
        <input
          id="occurred_at"
          type="datetime-local"
          required
          value={occurredAt}
          onChange={(e) => setOccurredAt(e.target.value)}
          className={inputClass}
        />
      </div>

      <div className={fieldClass}>
        <label className={labelClass} htmlFor="reporter_name">
          Your name
        </label>
        <input
          id="reporter_name"
          type="text"
          required
          value={reporterName}
          onChange={(e) => setReporterName(e.target.value)}
          className={inputClass}
        />
      </div>

      <div className={fieldClass}>
        <label className={labelClass} htmlFor="reporter_contact">
          Contact info
        </label>
        <input
          id="reporter_contact"
          type="text"
          required
          value={reporterContact}
          onChange={(e) => setReporterContact(e.target.value)}
          className={inputClass}
          placeholder="you@university.edu"
        />
      </div>

      {error && (
        <p role="alert" className="mb-5 text-sm text-stamp-red">
          Couldn't submit: {error}
        </p>
      )}

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full rounded-md bg-stamp-green px-4 py-2.5 font-medium text-paper transition hover:opacity-90 disabled:cursor-default disabled:opacity-60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stamp-green"
      >
        {isSubmitting ? "Submitting…" : "Submit report"}
      </button>
    </form>
  );
}

export default ReportForm;
