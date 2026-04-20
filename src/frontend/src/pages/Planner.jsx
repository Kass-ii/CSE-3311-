// @jsx h
import { useState, useEffect, useRef } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { MapContainer, TileLayer, Polyline, CircleMarker, Tooltip, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "../App.css";
import { useSettings } from "../context/SettingsContext";

// Fits map bounds to all route coordinates whenever they change
function MapFitter({ bounds }) {
  const map = useMap();
  useEffect(() => {
    if (bounds && bounds.length > 0) {
      map.fitBounds(bounds, { padding: [30, 30] });
    }
  }, [bounds, map]);
  return null;
}

function Planner() {
  const [searchParams] = useSearchParams();
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [departTime, setDepartTime] = useState("");

  const [result, setResult] = useState(null);
  const [geoData, setGeoData] = useState(null);   // ← GeoJSON from /visualize-route
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeLeg, setActiveLeg] = useState(null);

  const [stations, setStations] = useState([]);
  const { settings } = useSettings();

  useEffect(() => {
    const originFromMap = searchParams.get("origin");
    const destinationFromMap = searchParams.get("destination");
    if (originFromMap) setOrigin(originFromMap);
    if (destinationFromMap) setDestination(destinationFromMap);
    setStations(settings.stations || []);
  }, [searchParams, settings]);

  function formatTo12Hour(timeString) {
    if (!timeString) return "";
    const [hourStr, minuteStr] = timeString.split(":");
    let hour = parseInt(hourStr, 10);
    const period = hour >= 12 ? "PM" : "AM";
    hour = hour % 12 || 12;
    return `${hour}:${minuteStr} ${period}`;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setResult(null);
    setGeoData(null);
    setActiveLeg(null);

    if (!origin.trim()) { setError("Please enter an origin station."); return; }
    if (!destination.trim()) { setError("Please enter a destination station."); return; }
    if (!departTime) { setError("Please choose a departure time."); return; }

    setLoading(true);

    try {
      // Step 1: get the route plan
      const planRes = await fetch("http://127.0.0.1:5000/plan-iter3", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ origin, destination, depart_time: departTime, settings }),
      });
      const planData = await planRes.json();
      if (!planRes.ok || planData.error) { setError(planData.error || "Something went wrong."); return; }
      setResult(planData);

      // Step 2: fetch GeoJSON for map visualization
      const geoRes = await fetch("http://127.0.0.1:5000/visualize-route", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ legs: planData.legs }),
      });
      const geoJson = await geoRes.json();
      setGeoData(geoJson);

    } catch (err) {
      setError("Could not connect to the backend. Error:\n" + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Build flat [lat, lng] bounds array for MapFitter
  const allBounds = geoData?.features?.flatMap(feat =>
    feat.geometry.coordinates.map(([lng, lat]) => [lat, lng])
  ) ?? [];

  // Collect unique stop markers from result legs
  const stopMarkers = (() => {
    if (!result?.legs || !geoData) return [];
    const seen = new Set();
    const markers = [];
    result.legs.forEach((leg, i) => {
      const color = geoData.features?.[i]?.properties?.color ?? "#888";
      [
        { name: leg.from_stop_name, id: leg.from_stop_id },
        { name: leg.to_stop_name,   id: leg.to_stop_id   },
      ].forEach(({ name, id }) => {
        if (!name || seen.has(name)) return;
        seen.add(name);
        // find coordinates from the GeoJSON endpoint coordinates
        // (your /visualize-route returns per-stop coords in the future;
        //  for now we pull from the first/last point of each leg's feature)
        const feat = geoData.features[i];
        if (!feat) return;
        const coords = feat.geometry.coordinates;
        const isFrom = name === leg.from_stop_name;
        const [lng, lat] = isFrom ? coords[0] : coords[coords.length - 1];
        markers.push({ name, lat, lng, color });
      });
    });
    return markers;
  })();

  return (
    <div className="page">
      <div className="app-shell">
        {/* ── Left panel: form + results ── */}
        <div className="left-panel">
          <div className="brand-box">
            <h1>ComfortRoute</h1>
            <p>Find a full route between two stations using comfort-based routing.</p>
            <p className="helper-text">Try a station like "centreport" or "downtown".</p>
          </div>

          <form onSubmit={handleSubmit} className="trip-form">
            <label>
              Origin Station
              <input type="text" value={origin} onChange={e => setOrigin(e.target.value)} placeholder="ex: Centreport Station" />
            </label>
            <label>
              Destination Station
              <input type="text" value={destination} onChange={e => setDestination(e.target.value)} placeholder="ex: West End Station" />
            </label>
            <label>
              Departure Time
              <input type="time" step="1" value={departTime} onChange={e => setDepartTime(e.target.value)} />
            </label>
            <button type="submit" disabled={loading}>
              {loading ? "Finding Route..." : "Find Route"}
            </button>
          </form>

          {error && <div className="error-box">{error}</div>}

          {/* Leg list — appears after a result is found */}
          {result && (
            <div className="leg-list">
              <p className="leg-list-heading">Legs — click to zoom</p>
              {result.legs.map((leg, i) => {
                const color = geoData?.features?.[i]?.properties?.color ?? "#888";
                return (
                  <div
                    key={i}
                    className={`leg-card ${activeLeg === i ? "active" : ""}`}
                    onClick={() => setActiveLeg(activeLeg === i ? null : i)}
                  >
                    <span className="leg-dot" style={{ background: color }} />
                    <div>
                      <strong>{leg.route_name}</strong>
                      <p>{leg.from_stop_name} → {leg.to_stop_name}</p>
                      <p>{formatTo12Hour(leg.depart_time)} – {formatTo12Hour(leg.arrive_time)}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* ── Right panel: map + summary ── */}
        <div className="right-panel">
          {!result && !loading && !error && (
            <div className="empty-state">
              <h2>Your route will appear here</h2>
              <p>Enter an origin, destination, and departure time to generate a route.</p>
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
                {result.route_summary} — {result.metrics?.total_ride_minutes ?? "N/A"} min ride,{" "}
                {result.metrics?.total_wait_minutes ?? "N/A"} min wait.
                {result.legs?.length > 0 && (
                  <> Arrives at {formatTo12Hour(result.legs.at(-1).arrive_time)}.</>
                )}
              </p>

              {/* ── Map ── */}
              {geoData && (
                <div className="map-container" style={{ height: 360, borderRadius: 10, overflow: "hidden", marginTop: 12 }}>
                  <MapContainer
                    center={[32.78, -96.97]}   // DFW fallback; MapFitter overrides
                    zoom={11}
                    style={{ width: "100%", height: "100%" }}
                    zoomControl={true}
                  >
                    <TileLayer
                      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                      attribution="© OpenStreetMap contributors"
                    />

                    <MapFitter
                      bounds={
                        activeLeg !== null
                          ? geoData.features[activeLeg]?.geometry.coordinates.map(([lng, lat]) => [lat, lng])
                          : allBounds
                      }
                    />

                    {/* Route polylines */}
                    {geoData.features.map((feat, i) => {
                      const coords = feat.geometry.coordinates.map(([lng, lat]) => [lat, lng]);
                      const color = feat.properties.color ?? "#888";
                      const isActive = activeLeg === i;
                      return (
                        <>
                          {/* White outline for contrast */}
                          <Polyline
                            key={`shadow-${i}`}
                            positions={coords}
                            pathOptions={{ color: "#fff", weight: 8, opacity: 0.6 }}
                          />
                          <Polyline
                            key={`line-${i}`}
                            positions={coords}
                            pathOptions={{
                              color,
                              weight: isActive ? 7 : 5,
                              opacity: activeLeg === null || isActive ? 1 : 0.35,
                            }}
                            eventHandlers={{ click: () => setActiveLeg(i) }}
                          />
                        </>
                      );
                    })}

                    {/* Stop circle markers */}
                    {stopMarkers.map((s, i) => (
                      <CircleMarker
                        key={i}
                        center={[s.lat, s.lng]}
                        radius={6}
                        pathOptions={{ color: s.color, weight: 3, fillColor: "#fff", fillOpacity: 1 }}
                      >
                        <Tooltip direction="top" offset={[0, -8]} permanent={false}>
                          {s.name}
                        </Tooltip>
                      </CircleMarker>
                    ))}
                  </MapContainer>
                </div>
              )}

              {/* Metrics row */}
              <div className="info-grid" style={{ marginTop: 12 }}>
                <div className="info-box">
                  <h3>Summary</h3>
                  <p><strong>Ride time:</strong> {result.metrics.total_ride_minutes} min</p>
                  <p><strong>Wait time:</strong> {result.metrics.total_wait_minutes} min</p>
                  {result.metrics.comfort_score && (
                    <p><strong>Comfort score:</strong> {Math.round(result.metrics.comfort_score * 100)}%</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <Link to="/menu" className="menu-button back-main-center">← Back to Main Menu</Link>
    </div>
  );
}

export default Planner;