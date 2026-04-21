import { useState } from "react";
import { useDartAlerts } from "../hooks/useDartAlerts";

export default function DartAlertsButton({ className }) {
  const { alerts, loading, error, fetchAlerts } = useDartAlerts();
  const [open, setOpen] = useState(false);

  function handleClick(e) {
    // Prevent the map from registering a click when we click the button
    e.stopPropagation();
    if (!open && alerts.length === 0) {
      fetchAlerts();
    }
    setOpen(!open);
  }

  return (
    <div className={className} style={{ position: "absolute", zIndex: 1001 }}>
      <button 
        onClick={handleClick} 
        className="map-ui-button"
      >
        🚨 DART Alerts
      </button>

      {open && (
        <div className="alerts-panel" onClick={(e) => e.stopPropagation()}>
          <h4>Recent Alerts</h4>

          {loading && <p>Loading alerts...</p>}
          {error && <p style={{ color: "red" }}>{error}</p>}

          {!loading && alerts.length === 0 && (
            <p>No recent alerts found.</p>
          )}

          <ul>
            {alerts.slice(0, 5).map((a, i) => (
              <li key={i}>
                <a href={a.link} target="_blank" rel="noreferrer">
                  {a.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}