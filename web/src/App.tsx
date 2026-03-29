import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import ProtectedRoute from './components/ProtectedRoute';
import DashboardLayout from './pages/Dashboard';
import ApprovalQueue from './pages/ApprovalQueue';
import Campaigns from './pages/Campaigns';
import Devices from './pages/Devices';
import SeedingControl from './pages/SeedingControl';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/login" element={<Login />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<DashboardLayout />}>
            <Route index element={<Navigate to="/dashboard/approval" replace />} />
            <Route path="approval" element={<ApprovalQueue />} />
            <Route path="campaigns" element={<Campaigns />} />
            <Route path="devices" element={<Devices />} />
            <Route path="seeding" element={<SeedingControl />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
