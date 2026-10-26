import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './layouts/Layout';
import { Dashboard } from './pages/Dashboard';
import { Incidents } from './pages/Incidents';
import { IncidentDetail } from './pages/IncidentDetail';
import { ReliefMap } from './pages/ReliefMap';
import { Resources } from './pages/Resources';
import { Personnel } from './pages/Personnel';
import { DemandPrediction } from './pages/DemandPrediction';
import { Allocations } from './pages/Allocations';
import { Missions } from './pages/Missions';
import { Reports } from './pages/Reports';
import { Settings } from './pages/Settings';
import { LoadingScreen } from './components/LoadingScreen';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="incidents" element={<Incidents />} />
        <Route path="incidents/:id" element={<IncidentDetail />} />
        <Route path="map" element={<ReliefMap />} />
        <Route path="resources" element={<Resources />} />
        <Route path="personnel" element={<Personnel />} />
        <Route path="predictions" element={<DemandPrediction />} />
        <Route path="allocations" element={<Allocations />} />
        <Route path="missions" element={<Missions />} />
        <Route path="reports" element={<Reports />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;