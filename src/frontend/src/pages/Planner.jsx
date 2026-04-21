import { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import "../App.css";
import { useSettings } from "../context/SettingsContext";

function Planner() {
  const [searchParams] = useSearchParams();

  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [departTime, setDepartTime] = useState("");

  const [originQuery, setOriginQuery] = useState("");
  const [destinationQuery, setDestinationQuery] = useState("");

  const [showOriginList, setShowOriginList] = useState(false);
  const [showDestinationList, setShowDestinationList] = useState(false);

  const [stations, setStations] = useState([]);

  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { settings } = useSettings();

  // Load stations
  useEffect(() => {
    async function fetchStations() {
      try {
        const res = await fetch("http://127.0.0.1:5000/stations");
        const data = await res.json();
        setStations(data || []);
      } catch (err) {
        console.error("Failed to load stations:", err);
      }
    }

    fetchStations();
  }, []);

  // Prefill from URL params
  useEffect(() => {
    const o = searchParams.get("origin");
    const d = searchParams.get("destination");

    if (o) {
      setOrigin(o);
      setOriginQuery(o);
    }

    if (d) {
      setDestination(d);
      setDestinationQuery(d);
    }
  }, [searchParams]);

  function formatTo12Hour(timeString) {
    if (!timeString) return "";

    const [h, m] = timeString.split(":");
    let hour = parseInt(h, 10);

    const period = hour >= 12 ? "PM" : "AM";
    hour = hour % 12;
    if (hour === 0) hour = 12;

    return `${hour}:${m} ${period}`;
  }

  function handleNow() {
    const now = new Date();
    const hh = String(now.getHours()).padStart(2, "0");
    const mm = String(now.getMinutes()).padStart(2, "0");
    const ss = String(now.getSeconds()).padStart(2, "0");
    setDepartTime(`${hh}:${mm}:${ss}`);
  }

  function sanitize(val) {
    return val.replace(/-/g, "0");
  }

  function handleKeyDown(e) {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSubmit(e);
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setResult(null);

    const cleanOrigin = sanitize(origin);
    const cleanDestination = sanitize(destination);
    const cleanTime = sanitize(departTime);

    if (!cleanOrigin) {
      setError("Please select an origin station.");
      return;
    }

    if (!cleanDestination) {
      setError("Please select a destination station.");
      return;
    }

    if (!cleanTime) {
      setError("Please choose a departure time.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:5000/plan-iter3", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          origin: cleanOrigin,
          destination: cleanDestination,
          depart_time: cleanTime,
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
      setError("Backend error:\n" + err.message);
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
            <p>Find optimized transit routes with comfort scoring.</p>
          </div>

          <form className="trip-form" onSubmit={handleSubmit}>

            {/* ORIGIN */}
            <label style={{ position: "relative" }}>
              Origin Station

              <input
                type="text"
                value={originQuery}
                placeholder="Search origin station..."
                onChange={(e) => {
                  setOriginQuery(e.target.value);
                  setShowOriginList(true);
                }}
                onFocus={() => setShowOriginList(true)}
                onKeyDown={handleKeyDown}
              />

              {showOriginList && (
                <div className="typeahead-panel">
                  {stations
                    .filter((s) =>
                      s.stop_name
                        .toLowerCase()
                        .includes(originQuery.toLowerCase())
                    )
                    .slice(0, 8)
                    .map((s) => (
                      <div
                        key={s.stop_id}
                        className="typeahead-item"
                        onMouseDown={() => {
                          setOrigin(s.stop_name);
                          setOriginQuery(s.stop_name);
                          setShowOriginList(false);
                        }}
                      >
                        {s.stop_name}
                      </div>
                    ))}
                </div>
              )}
            </label>

            {/* DESTINATION */}
            <label style={{ position: "relative" }}>
              Destination Station

              <input
                type="text"
                value={destinationQuery}
                placeholder="Search destination station..."
                onChange={(e) => {
                  setDestinationQuery(e.target.value);
                  setShowDestinationList(true);
                }}
                onFocus={() => setShowDestinationList(true)}
                onKeyDown={handleKeyDown}
              />

              {showDestinationList && (
                <div className="typeahead-panel">
                  {stations
                    .filter((s) =>
                      s.stop_name
                        .toLowerCase()
                        .includes(destinationQuery.toLowerCase())
                    )
                    .slice(0, 8)
                    .map((s) => (
                      <div
                        key={s.stop_id}
                        className="typeahead-item"
                        onMouseDown={() => {
                          setDestination(s.stop_name);
                          setDestinationQuery(s.stop_name);
                          setShowDestinationList(false);
                        }}
                      >
                        {s.stop_name}
                      </div>
                    ))}
                </div>
              )}
            </label>

            {/* TIME */}
            <label>
              Departure Time

              <div style={{ display: "flex", gap: "8px" }}>
                <input
                  type="time"
                  step="1"
                  value={departTime}
                  onChange={(e) => setDepartTime(e.target.value)}
                  onKeyDown={handleKeyDown}
                />

                <button type="button" onClick={handleNow}>
                  Now
                </button>
              </div>
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
              <p>Enter origin, destination, and departure time.</p>
            </div>
          )}

          {loading && (
            <div className="empty-state">
              <h2>Finding best route...</h2>
            </div>
          )}

          {result && (
            <div className="result-card">
              <h2>Best Route Found</h2>

              <p className="summary">
                Route: {result.route_summary}
              </p>

              <div className="info-grid">
                {result.legs?.map((leg, i) => (
                  <div key={i} className="info-box">
                    <h3>Leg {i + 1}</h3>
                    <p>{leg.from_stop} → {leg.to_stop}</p>
                    <p>
                      {formatTo12Hour(leg.depart_time)} →{" "}
                      {formatTo12Hour(leg.arrive_time)}
                    </p>
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