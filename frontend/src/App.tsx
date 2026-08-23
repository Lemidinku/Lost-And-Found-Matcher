import { BrowserRouter, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import ReportListPage from "./pages/ReportListPage";
import NewReportPage from "./pages/NewReportPage";
import ReportDetailPage from "./pages/ReportDetailPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<ReportListPage />} />
          <Route path="/new" element={<NewReportPage />} />
          <Route path="/reports/:id" element={<ReportDetailPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
