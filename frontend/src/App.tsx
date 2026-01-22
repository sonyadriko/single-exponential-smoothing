import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Login from './components/Login';

function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [userRole, setUserRole] = useState<string | null>(localStorage.getItem('role'));

  useEffect(() => {
    // Optional: Validate token on mount
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
                <Navigate to="/dashboard" replace />
              )
            }
          />
          <Route
            path="/dashboard"
            element={
              token ? (
                <Dashboard userRole={userRole} onLogout={handleLogout} token={token} />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
