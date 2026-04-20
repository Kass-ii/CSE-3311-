// @jsx h
import Settings from "./pages/Settings";
import { SettingsProvider } from "./context/SettingsContext";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { getCurrentUser } from "./api/auth";

import Login from "./pages/Login";
import SignUp from "./pages/SignUp";
import ForgotPassword from "./pages/ForgotPassword";
import MainMenu from "./pages/MainMenu";
import MapPage from "./pages/MapPage";
import Planner from "./pages/Planner";
import AccountSettings from "./pages/AccountSettings";
import UpdateEmail from "./pages/UpdateEmail";
import UpdatePassword from "./pages/UpdatePassword";
import "./App.css";

function ProtectedRoute({ user, children }) {
  if (!user) {
    return <Navigate to="/" replace />;
  }
  return children;
}

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      try {
        const data = await getCurrentUser();
        setUser(data.user);
      } catch (error) {
        console.error("Failed to load user:", error);
      } finally {
        setLoading(false);
      }
    }

    loadUser();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <SettingsProvider>
      <BrowserRouter>
        <Routes>
          <Route
            path="/"
            element={user ? <Navigate to="/menu" replace /> : <Login />}
          />
          <Route
            path="/signup"
            element={user ? <Navigate to="/menu" replace /> : <SignUp />}
          />
          <Route path="/forgot-password" element={<ForgotPassword />} />

          <Route
            path="/menu"
            element={
              <ProtectedRoute user={user}>
                <MainMenu />
              </ProtectedRoute>
            }
          />
          <Route
            path="/map"
            element={
              <ProtectedRoute user={user}>
                <MapPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/planner"
            element={
              <ProtectedRoute user={user}>
                <Planner />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute user={user}>
                <Settings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/account-settings"
            element={
              <ProtectedRoute user={user}>
                <AccountSettings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/update-email"
            element={
              <ProtectedRoute user={user}>
                <UpdateEmail />
              </ProtectedRoute>
            }
          />
          <Route
            path="/update-password"
            element={
              <ProtectedRoute user={user}>
                <UpdatePassword />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </SettingsProvider>
  );
}

export default App;