import { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import "../App.css";
import { useSettings } from "../context/SettingsContext";

function Planner() {
  const [searchParams] = useSearchParams();
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [departTime, setDepartTime] = useState("");

  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [stations, setStations] = useState([]);
  const { settings } = useSettings();

  useEffect(() => {
    const originFromMap = searchParams.get("origin");
    const destinationFromMap = searchParams.get("destination");

    if (originFromMap) {
      setOrigin(originFromMap);
    }

    if (destinationFromMap) {
      setDestination(destinationFromMap);
    }

    setStations(settings.stations || []);
  }, [searchParams, settings]);

  function formatTo12Hour(timeString) {
    if (!timeString) return "";

    const [hourStr, minuteStr] = timeString.split(":");
    let hour = parseInt(hourStr, 10);

    const period = hour >= 12 ? "PM" : "AM";
    hour = hour % 12;
    if (hour === 0) hour = 12;

    return `${hour}:${minuteStr} ${period}`;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setResult(null);

    if (!origin.trim()) {
      setError("Please enter an origin station.");
      return;
    }

    if (!destination.trim()) {
      setError("Please enter a destination station.");
      return;
    }

    if (!departTime) {
      setError("Please choose a departure time.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:5000/plan-iter3", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          origin,
          destination,
          depart_time: departTime,
          settings,
        }),
      });

      const data = await response.json();

      if (!response.ok || data.error) {
        setError(data.error || "Something went wrong.");
        return;
      }

      setResult(data);
    } catch (err) {
      setError("Could not connect to the backend. Error:\n" + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="app-shell">
        <div className="left-panel">
          <div className="brand-box">
            <h1>ComfortRoute</h1>
            <p>Find a full route between two stations using comfort-based routing.</p>
            <p className="helper-text">
              Try a station like “centreport” or “downtown”.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="trip-form">
            <label>
              Origin Station
              <input
                type="text"
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
                placeholder="ex: Centreport Station"
              />
            </label>

            <label>
              Destination Station
              <input
                type="text"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                placeholder="ex: West End Station"
              />
            </label>

            <label>
              Departure Time
              <input
                type="time"
                step="1"
                value={departTime}
                onChange={(e) => setDepartTime(e.target.value)}
              />
            </label>

            <button type="submit" disabled={loading}>
              {loading ? "Finding Route..." : "Find Route"}
            </button>
          </form>

          {error && <div className="error-box">{error}</div>}
        </div>

        <div className="right-panel">
          {!result && !loading && !error && (
            <div className="empty-state">
              <h2>Your route will appear here</h2>
              <p>
                Enter an origin, destination, and departure time to generate a route.
              </p>
            </div>
          )}

          {loading && (
            <div className="empty-state">
              <h2>Finding best route...</h2>
              <p>Please wait while we check the schedule.</p>
            </div>
          )}

          {result && (
            <div className="result-card">
              <h2>Best Route Found</h2>

              <p className="summary">
                ComfortRoute found a route on {result.route_summary} that keeps you on the train for {result.metrics?.total_ride_minutes ?? "N/A"} minutes.
                {result.legs && result.legs.length > 1 && (
                  <> You arrive at {formatTo12Hour(result.legs[result.legs.length - 1].arrive_time)}.</>
                )}
              </p>

              <div className="info-grid">
                <div className="info-box">
                  <h3>Route Summary</h3>
                  <p><strong>Route:</strong> {result.route_summary}</p>
                  <p><strong>Total Time on Train:</strong> {result.metrics.total_ride_minutes} minutes</p>
                  <p><strong>Total Wait Time:</strong> {result.metrics.total_wait_minutes} minutes</p>
                </div>

                {result.legs && result.legs.map((leg, index) => (
                  <div key={index} className="info-box">
                    <h3>{`Leg ${index + 1}`}</h3>
                    <p><strong>From:</strong> {leg.from_stop}</p>
                    <p><strong>To:</strong> {leg.to_stop}</p>
                    <p><strong>Depart:</strong> {formatTo12Hour(leg.depart_time)}</p>
                    <p><strong>Arrive:</strong> {formatTo12Hour(leg.arrive_time)}</p>
                    <p><strong>Route:</strong> {leg.route_name}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <Link to="/menu" className="menu-button back-main-center">
        ← Back to Main Menu
      </Link>
    </div>
  );
}

export default Planner;
