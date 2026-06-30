import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Spin } from 'antd';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import AppLayout from './layouts/AppLayout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import TransactionsPage from './pages/TransactionsPage';
import AgentsPage from './pages/AgentsPage';
import MissionsPage from './pages/MissionsPage';
import StockPage from './pages/StockPage';
import MachinesPage from './pages/MachinesPage';
import MotosPage from './pages/MotosPage';
import ReportsPage from './pages/ReportsPage';
import AnomaliesPage from './pages/AnomaliesPage';
import './i18n';

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <Spin style={{ display: 'block', margin: '40vh auto' }} />;
  return user ? <>{children}</> : <Navigate to="/login" />;
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/" element={<PrivateRoute><AppLayout /></PrivateRoute>}>
              <Route index element={<DashboardPage />} />
              <Route path="transactions" element={<TransactionsPage />} />
              <Route path="agents" element={<AgentsPage />} />
              <Route path="missions" element={<MissionsPage />} />
              <Route path="stock" element={<StockPage />} />
              <Route path="machines" element={<MachinesPage />} />
              <Route path="motos" element={<MotosPage />} />
              <Route path="reports" element={<ReportsPage />} />
              <Route path="anomalies" element={<AnomaliesPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}
