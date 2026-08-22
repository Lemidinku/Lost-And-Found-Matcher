import { Link } from "react-router-dom";
import ReportForm from "../components/ReportForm";

function NewReportPage() {
  return (
    <div style={{ padding: "24px", textAlign: "left" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "20px",
          gap: "16px",
          flexWrap: "wrap",
        }}
      >
        <h1 style={{ fontSize: "32px", margin: 0 }}>New report</h1>
        <Link
          to="/"
          style={{ color: "var(--accent)", textDecoration: "none", whiteSpace: "nowrap" }}
        >
          Back to reports
        </Link>
      </div>

      <ReportForm />
    </div>
  );
}

export default NewReportPage;
