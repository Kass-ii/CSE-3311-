// @jsx h
import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import "../App.css";

function Planner() {
  const [searchParams] = useSearchParams();
  const [startQuery, setStartQuery] = useState("");
  const [startAfter, setStartAfter] = useState("");
  const [returnBy, setReturnBy] = useState("");

  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const stationFromMap = searchParams.get("start");
    if (stationFromMap) {
      setStartQuery(stationFromMap);
    }
  }, [searchParams]);

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

    if (!startQuery.trim()) {
      setError("Please enter a start station.");
      return;
    }

    if (!startAfter) {
      setError("Please choose a start-after time.");
      return;
    }

    if (!returnBy) {
      setError("Please choose a return-by time.");
      return;
    }

    if (returnBy <= startAfter) {
      setError("Return-by time must be later than start-after time.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:5000/plan-iter1", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          start_query: startQuery,
          start_after: startAfter,
          return_by: returnBy,
        }),
      });

      const data = await response.json();

      if (!response.ok || data.error) {
        setError(data.error || "Something went wrong.");
        return;
      }

      setResult(data);
    } catch (err) {
      setError("Could not connect to the backend. Error:\n"+err.message);
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
            <p>Find a route that keeps you inside the train longer.</p>
            <p className="helper-text">
              Try a station like “centreport” or “downtown”.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="trip-form">
            <label>
              Start Station
              <input
                type="text"
                value={startQuery}
                onChange={(e) => setStartQuery(e.target.value)}
                placeholder="ex: Centreport"
              />
            </label>

            <label>
              Start After Time
              <input
                type="time"
                step="1"
                value={startAfter}
                onChange={(e) => setStartAfter(e.target.value)}
              />
            </label>

            <label>
              Return By Time
              <input
                type="time"
                step="1"
                value={returnBy}
                onChange={(e) => setReturnBy(e.target.value)}
              />
            </label>

            <button type="submit" disabled={loading}>
              {loading ? "Finding Route..." : "Find Comfortable Route"}
            </button>
          </form>

          {error && <div className="error-box">{error}</div>}
        </div>

        <div className="right-panel">
          {!result && !loading && !error && (
            <div className="empty-state">
              <h2>Your route will appear here</h2>
              <p>
                Enter a station and time window to generate a comfort-based trip.
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
                ComfortRoute found a trip on the {result.route_name || result.route_id} line
                that keeps you on the train for {result.metrics.total_ride_minutes} minutes
                and gets you back by {formatTo12Hour(result.leg2.arrive_back)}.
              </p>

              <div className="info-grid">
                <div className="info-box">
                  <h3>Route Summary</h3>
                  <p><strong>Line:</strong> {result.route_name || "N/A"}</p>
                  <p><strong>Total Time on Train:</strong> {result.metrics.total_ride_minutes} minutes</p>
                  <p><strong>Wait at Turn Stop:</strong> {result.metrics.turn_wait_minutes} minutes</p>
                </div>

                <div className="info-box">
                  <h3>Outbound Trip</h3>
                  <p><strong>Leave Start Station:</strong> {formatTo12Hour(result.leg1.depart_start)}</p>
                  <p><strong>Turn Stop:</strong> {result.leg1.turn_stop_name || result.leg1.turn_stop_id}</p>
                  <p><strong>Arrive at Turn Stop:</strong> {formatTo12Hour(result.leg1.arrive_turn)}</p>
                  <p><strong>Time on Train:</strong> {result.leg1.ride_minutes} minutes</p>
                </div>

                <div className="info-box">
                  <h3>Return Trip</h3>
                  <p><strong>Leave Turn Stop:</strong> {formatTo12Hour(result.leg2.depart_turn)}</p>
                  <p><strong>Return to Start Station:</strong> {formatTo12Hour(result.leg2.arrive_back)}</p>
                  <p><strong>Time on Train:</strong> {result.leg2.ride_minutes} minutes</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Planner;
