import { Link } from "react-router-dom";
import ReportForm from "../components/ReportForm";

function NewReportPage() {
  return (
    <div>
      <Link
        to="/"
        className="mb-6 inline-block text-sm text-ink/60 no-underline hover:text-stamp-green"
      >
        &larr; Back to reports
      </Link>

      <div className="mx-auto max-w-xl">
        <h1 className="mb-1 font-display text-3xl font-bold text-ink">New report</h1>
        <p className="mb-6 text-ink/60">
          Tell us what you lost or found — the more detail, the better a match.
        </p>

        <div className="rounded-lg border border-ink/10 bg-card p-6 shadow-sm">
          <ReportForm />
        </div>
      </div>
    </div>
  );
}

export default NewReportPage;
