import { useSettings } from "../context/SettingsContext";
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { MapContainer, TileLayer, Marker, Popup, Circle, Polyline } from "react-leaflet";

import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix default marker icons in React Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
    iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});
const indoorIcon = new L.Icon({
    iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
});

function MapPage() {
    const { settings } = useSettings();
    const [stations, setStations] = useState([]);
    const [userLocation, setUserLocation] = useState(null);
    const [error, setError] = useState("");
    const [railLines, setRailLines] = useState([]);
    const [selectedOrigin, setSelectedOrigin] = useState("");
    const [selectedDestination, setSelectedDestination] = useState("");
    const navigate = useNavigate();

    useEffect(() => {
        fetch("http://127.0.0.1:5000/stations")
            .then((r) => r.json())
            .then((data) =>
                setStations(data.map((s) => ({
                    ...s,
                    hours: s.hours || "05:00-23:00",
                })))
            )
            .catch(() => { });
    }, []);
    useEffect(() => {
        fetch("http://127.0.0.1:5000/rail-shapes")
            .then((res) => res.json())
            .then((data) => setRailLines(data.features))
            .catch(() => setError("Could not load rail lines."));
    }, []);

    const LINE_RENDER_ORDER = { Green: 0, Orange: 1, Red: 2, Blue: 3, Silver: 4, TRE: 5, Streetcar: 6 };
	const sortedLines = [...railLines].sort(
		(a, b) => LINE_RENDER_ORDER[a.properties.line_name] - LINE_RENDER_ORDER[b.properties.line_name]
	);
    function locate() {
        if (!navigator.geolocation) {
            setError("Geolocation is not supported by your browser.");
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                setUserLocation({
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                });
            },
            () => {
                setError("Could not get your current location.");
            }
        );
    }

    function distanceInKm(lat1, lng1, lat2, lng2) {
        const toRad = (value) => (value * Math.PI) / 180;
        const R = 6371;

        const dLat = toRad(lat2 - lat1);
        const dLng = toRad(lng2 - lng1);

        const a =
            Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(toRad(lat1)) *
            Math.cos(toRad(lat2)) *
            Math.sin(dLng / 2) *
            Math.sin(dLng / 2);

        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return R * c;
    }

    const nearbyStations = userLocation
        ? stations.filter(
            (station) =>
                distanceInKm(userLocation.lat, userLocation.lng, station.lat, station.lng) <= 3
        )
        : [];

    const userIcon = new L.Icon({
        iconUrl: "https://cdn-icons-png.flaticon.com/512/64/64113.png",
        iconSize: [28, 28],
        iconAnchor: [14, 14]
    });

    const mapCenter = userLocation
        ? [userLocation.lat, userLocation.lng]
        : [32.82, -96.80];

    function openPlannerWithSelection() {
        if (!selectedOrigin || !selectedDestination) {
            setError("Please select both an origin and a destination station.");
            return;
        }

        navigate(
            `/planner?origin=${encodeURIComponent(selectedOrigin)}&destination=${encodeURIComponent(selectedDestination)}`
        );
    }

    return (
        <div className="map-page">
            <div className="map-full-layout">
                <div className="map-main-column">
                    {error && <div className="error-box">{error}</div>}

                    <div className="map-wrapper">

                        <button className="map-location-btn" onClick={locate}>
                            📍 My Location
                        </button>

                        <MapContainer
                            center={mapCenter}
                            zoom={12}
                            style={{ height: "100%", width: "100%" }}
                        >
                            <TileLayer
                                attribution="&copy; OpenStreetMap contributors"
                                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            />

                            {userLocation && (
                                <>
                                    <Marker position={[userLocation.lat, userLocation.lng]} icon={userIcon}>
                                        <Popup>Your current location</Popup>
                                    </Marker>
                                    <Circle
                                        center={[userLocation.lat, userLocation.lng]}
                                        radius={3000}
                                        pathOptions={{ color: "blue", fillColor: "#3b82f6", fillOpacity: 0.1 }}
                                    />
                                </>
                            )}

                            {sortedLines.map((feature, i) => (
                                <Polyline
                                    key={i}
                                    positions={feature.geometry.coordinates.map(([lng, lat]) => [lat, lng])}
                                    pathOptions={{
                                        color: feature.properties.color,
                                        weight: 4,
                                        opacity: 0.85,
                                    }}
                                >
                                    <Popup>{feature.properties.line_name} Line</Popup>
                                </Polyline>
                            ))}

                            {stations.map((station) => {
                                const isNearby = nearbyStations.some((s) => s.stop_id === station.stop_id);
                                const isIndoor = station.indoors === 1;

                                return (
                                    <Marker
                                        key={station.stop_id}
                                        position={[station.lat, station.lng]}
                                        icon={
                                            settings.highlightIndoorLobby && station.indoors === 1
                                                ? indoorIcon
                                                : new L.Icon.Default()
                                        }
                                    >
                                        <Popup>
                                            <strong>{station.stop_name}</strong>
                                            <br />
                                            {isNearby ? "Nearby station" : "Station"}
                                            {isIndoor && (
                                                <>
                                                    <br />
                                                    <span style={{ color: "green" }}>🏠 Indoor shelter available</span>
                                                </>
                                            )}
                                            {station.indoors === 1 ? (
                                                <div>Indoor lobby available</div>
                                            ) : (
                                                <div>No indoor lobby</div>
                                            )}
                                            {settings.showStationHours && <div>Hours: {station.hours}</div>}
                                            <br />

                                            <button
                                                onClick={() => setSelectedOrigin(station.stop_name)}
                                                style={{ marginRight: "8px" }}
                                            >
                                                Set as Origin
                                            </button>

                                            <button
                                                onClick={() => setSelectedDestination(station.stop_name)}
                                            >
                                                Set as Destination
                                            </button>
                                        </Popup>
                                    </Marker>
                                );
                            })}
                        </MapContainer>
                    </div>

                    <Link to="/menu" className="back-link map-back-link">
                        ← Back to Main Menu
                    </Link>
                </div>

                <div className="map-side-column">
                    <div className="selection-box">
                        <h3>Selected Trip</h3>
                        <p><strong>Origin:</strong> {selectedOrigin || "Not selected"}</p>
                        <p><strong>Destination:</strong> {selectedDestination || "Not selected"}</p>

                        <button
                            className="menu-button"
                            onClick={openPlannerWithSelection}
                            disabled={!selectedOrigin || !selectedDestination}
                        >
                            Open Planner with Selection
                        </button>
                    </div>

                    {userLocation && nearbyStations.length > 0 && (
                        <div className="selection-box">
                            <h3>Nearby Rail Stations</h3>
                            <ul style={{ paddingLeft: "20px", margin: 0 }}>
                                {nearbyStations.map((station) => (
                                    <li key={station.stop_id} style={{ marginBottom: "8px" }}>
                                        {station.stop_name}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default MapPage;
