import { createContext, useContext, useEffect, useState } from "react";

const STORAGE_KEY = "comfortroute-user-settings";

const defaultSettings = {
    highlightIndoorLobby: true,
    showStationHours: true,
};

const SettingsContext = createContext({
    settings: defaultSettings,
    setSettings: () => { },
});

export function SettingsProvider({ children }) {
    const [settings, setSettings] = useState(() => {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            return saved ? JSON.parse(saved) : defaultSettings;
        } catch {
            return defaultSettings;
        }
    });

    useEffect(() => {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    }, [settings]);

    return (
        <SettingsContext.Provider value={{ settings, setSettings }}>
            {children}
        </SettingsContext.Provider>
    );
}

export function useSettings() {
    return useContext(SettingsContext);
}