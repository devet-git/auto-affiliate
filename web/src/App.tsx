import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import ProtectedRoute from './components/ProtectedRoute';
import DashboardLayout from './pages/Dashboard';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/login" element={<Login />} />
        
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<DashboardLayout />}>
            <Route index element={
              <div className="p-6 border border-zinc-800 rounded-lg bg-zinc-900/50">
                <h1 className="text-2xl font-bold mb-2">Welcome Admin</h1>
                <p className="text-zinc-400">Select a module from the sidebar (Coming in Phase 05-02)</p>
              </div>
            } />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
