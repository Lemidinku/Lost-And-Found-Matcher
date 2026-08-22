import { BrowserRouter, Route, Routes } from "react-router-dom";
import ReportListPage from "./pages/ReportListPage";
import NewReportPage from "./pages/NewReportPage";

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
