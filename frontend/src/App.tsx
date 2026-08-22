import { BrowserRouter, Route, Routes } from "react-router-dom";

function ReportListPage() {
  return <p>Report list page (Task 8).</p>;
}

function NewReportPage() {
  return <p>New report form (Task 9).</p>;
}

function ReportDetailPage() {
  return <p>Report detail page (Task 10).</p>;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ReportListPage />} />
        <Route path="/new" element={<NewReportPage />} />
        <Route path="/reports/:id" element={<ReportDetailPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
