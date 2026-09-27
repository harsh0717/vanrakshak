import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import DashboardPage from './components/Dashboard/DashboardPage';
import AlertsPage from './components/Alerts/AlertsPage';
import IncidentsPage from './components/Incidents/IncidentsPage';
import CompensationPage from './components/Compensation/CompensationPage';
import AgentsPage from './components/Agents/AgentsPage';
import DemoPage from './components/Demo/DemoPage';
import CitizenPage from './components/Citizen/CitizenPage';
import EmergencyAlertModal from './components/Citizen/EmergencyAlertModal';

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />
        <div className="app-main">
          <Header />
          <main className="app-content">
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/citizen" element={<CitizenPage />} />
              <Route path="/alerts" element={<AlertsPage />} />
              <Route path="/incidents" element={<IncidentsPage />} />
              <Route path="/compensation" element={<CompensationPage />} />
              <Route path="/agents" element={<AgentsPage />} />
              <Route path="/demo" element={<DemoPage />} />
            </Routes>
          </main>
        </div>
        <EmergencyAlertModal />
      </div>
    </BrowserRouter>
  );
}
