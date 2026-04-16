import { Link } from "react-router-dom";
import { useSettings } from "../context/SettingsContext";

function Settings() {
    const { settings, setSettings } = useSettings();

    const toggle = (key) => (e) => setSettings((prev) => ({ ...prev, [key]: e.target.checked }));

    return (
        <div className="page">
            <h1>Settings</h1>
            <div className="settings-grid">
                <label>
                    <input type="checkbox" checked={settings.highlightIndoorLobby} onChange={toggle("highlightIndoorLobby")} />
                    Highlight stations with indoor lobbies
                </label>
                <label>
                    <input type="checkbox" checked={settings.showStationHours} onChange={toggle("showStationHours")} />
                    Show hours of operation
                </label>
            </div>
            <Link to="/menu" className="menu-button">Back to Main Menu</Link>
        </div>
    );
}

export default Settings;