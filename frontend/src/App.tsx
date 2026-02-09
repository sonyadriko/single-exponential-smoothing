import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import AdminDashboard from './components/AdminDashboard';
import OwnerDashboard from './components/OwnerDashboard';

function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [userRole, setUserRole] = useState<string | null>(localStorage.getItem('role'));

  useEffect(() => {
    if (!token) {
      localStorage.removeItem('token');
      localStorage.removeItem('role');
    }
  }, [token]);

  const handleLogout = () => {
    setToken(null);
    setUserRole(null);
    localStorage.removeItem('token');
    localStorage.removeItem('role');
  }

  return (
    <Router>
      <div className="min-h-screen w-full bg-background text-foreground font-sans antialiased">
        <Routes>
          <Route
            path="/login"
            element={
              !token ? (
                <Login setToken={setToken} setUserRole={setUserRole} />
              ) : (
                <Navigate to={userRole === 'admin' ? '/admin' : '/owner'} replace />
              )
            }
          />
          <Route
            path="/admin"
            element={
              token && userRole === 'admin' ? (
                <AdminDashboard token={token} onLogout={handleLogout} />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/owner"
            element={
              token && userRole === 'owner' ? (
                <OwnerDashboard token={token} onLogout={handleLogout} />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route 
            path="/" 
            element={
              token ? (
                <Navigate to={userRole === 'admin' ? '/admin' : '/owner'} replace />
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
