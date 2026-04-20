import Settings from "./pages/Settings";
import { SettingsProvider } from "./context/SettingsContext";
import { BrowserRouter, Routes, Route } from "react-router-dom";
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

function App() {
  return (
    <SettingsProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/menu" element={<MainMenu />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/planner" element={<Planner />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/account-settings" element={<AccountSettings />} />
          <Route path="/update-email" element={<UpdateEmail />} />
          <Route path="/update-password" element={<UpdatePassword />} />
        </Routes>
      </BrowserRouter>
    </SettingsProvider>
  );
}

export default App;