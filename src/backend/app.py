# This file is the Flask backend API for our ComfortRoute project.
# Its job is to receive requests from the frontend (React), compute a route using GTFS data, and return the result as JSON.

from flask import Flask, request, jsonify
from flask_cors import CORS

from gtfs_parser import load_gtfs
from routing import plan_backtrack_same_line
import pandas as pd

app = Flask(__name__)
CORS(app)

# Load GTFS once when server starts
stops, routes, trips, stop_times, shapes = load_gtfs()
# list of stop_ids corresponding to transit centers and indoor stations.
indoorIDs = [33245, 33596, 33224, 26673, 30488, 33262, 33242, 33318, 33318, 33257, 26691, 33229, 33241, 21030,
             33233, 33310, 33312, 33287, 29833, 33234, 33243, 23320, 26897, 33276, 33228, 33221, 15913, 33227, 22748, 26420]
# Rendering information for route shape file
DART_LINE_ORDER = ["Green", "Orange", "Red",
                   "Blue", "Silver", "TRE", "Streetcar"]
DART_LINE_KEYWORDS = {
    "Green":     ["green line"],
    "Orange":    ["orange line"],
    "Red":       ["red line"],
    "Blue":      ["blue line"],
    "Silver":    ["silver line", "silver"],
    "TRE":       ["trinity railway", "tre"],
    "Streetcar": ["streetcar", "dallas street"],
}
DART_LINE_OFFSETS = {
    "Green":     0,
    "Orange":    1,
    "Red":       2,
    "Blue":      3,
    "Silver":    4,
    "TRE":       4,
    "Streetcar": 4,
}
OFFSET_STEP = 0.00015


@app.route("/")
def home():
    return jsonify({"message": "ComfortRoute backend is running"})


@app.route("/plan-iter1", methods=["POST"])
def plan_iter1():
    data = request.get_json()

    start_query = data.get("start_query", "").strip()
    start_after = data.get("start_after", "").strip()
    return_by = data.get("return_by", "").strip()

    if not start_query or not start_after or not return_by:
        return jsonify({"error": "Missing required fields"}), 400

    result = plan_backtrack_same_line(
        start_query=start_query,
        start_after=start_after,
        return_by=return_by,
        stops=stops,
        routes=routes,
        trips=trips,
        stop_times=stop_times
    )

    return jsonify(result)


@app.route("/stations", methods=["GET"])
def get_stations():
    # Get stop_ids that are served by rail routes (route_type 0 = light rail, 2 = commuter rail)
    rail_route_ids = routes[routes["route_type"].isin([0, 2])]["route_id"]
    rail_trip_ids = trips[trips["route_id"].isin(rail_route_ids)]["trip_id"]
    rail_stop_ids = stop_times[stop_times["trip_id"].isin(
        rail_trip_ids)]["stop_id"].unique()

    station_rows = stops.copy()
    station_rows = station_rows[["stop_id",
                                 "stop_name", "stop_lat", "stop_lon"]].dropna()
    station_rows = station_rows[station_rows["stop_id"].isin(rail_stop_ids)]
    station_rows = station_rows.drop_duplicates(
        subset=["stop_name", "stop_lat", "stop_lon"])
    station_rows["indoors"] = station_rows["stop_id"].astype(str).isin(
        [str(sid) for sid in indoorIDs]
    ).astype(int)

    stations_data = []
    for _, row in station_rows.iterrows():
        stations_data.append({
            "stop_id": str(row["stop_id"]),
            "stop_name": row["stop_name"],
            "lat": float(row["stop_lat"]),
            "lng": float(row["stop_lon"]),
            "indoors": int(row["indoors"])
        })

    return jsonify(stations_data)


@app.route("/rail-shapes", methods=["GET"])
def rail_shapes():
    rail_routes = routes[routes["route_type"].isin([0, 1, 2])].copy()

    def get_line_name(row):
        name = str(row["route_long_name"]).lower()
        short = str(row["route_short_name"]).lower()
        combined = name + " " + short
        for line, keywords in DART_LINE_KEYWORDS.items():
            if any(kw in combined for kw in keywords):
                return line
        return None

    rail_routes["line_name"] = rail_routes.apply(get_line_name, axis=1)
    rail_routes = rail_routes.dropna(subset=["line_name"])
    # Use the color directly from GTFS, ensure it has a # prefix
    rail_routes["hex_color"] = rail_routes["route_color"].apply(
        lambda c: f"#{c}" if pd.notna(c) and not str(
            c).startswith("#") else str(c)
    )

    shape_to_line = (
        trips[trips["route_id"].isin(rail_routes["route_id"])]
        .merge(rail_routes[["route_id", "line_name", "hex_color"]], on="route_id")
        [["shape_id", "line_name", "hex_color"]]
        .drop_duplicates()
    )
    shapes_sorted = shapes.sort_values(["shape_id", "shape_pt_sequence"])

    features = []
    for _, row in shape_to_line.iterrows():
        shape_id = row["shape_id"]
        line_name = row["line_name"]
        offset_index = DART_LINE_ORDER.index(line_name)
        offset = (DART_LINE_OFFSETS[line_name] - 1.5) * OFFSET_STEP

        pts = shapes_sorted[shapes_sorted["shape_id"] == shape_id][
            ["shape_pt_lon", "shape_pt_lat"]
        ].values.tolist()
        print(pts[:3])  # Should look like [[-96.xxx, 32.xxx], ...]
        if len(pts) < 2:
            continue

        offset = (offset_index - 1.5) * OFFSET_STEP
        pts_offset = [[lon, lat + offset] for lon, lat in pts]

        features.append({
            "type": "Feature",
            "properties": {
                "line_name": line_name,
                "color": row["hex_color"],
                "order": offset_index,
            },
            "geometry": {
                "type": "LineString",
                "coordinates": pts_offset,
            }
        })

    features.sort(key=lambda f: -f["properties"]["order"])
    import json
    return jsonify({"type": "FeatureCollection", "features": features}) 


@app.route("/plan-iter3", methods=["POST"])
def plan_iter3():
    data = request.get_json()

    origin = data.get("origin", "").strip()
    destination = data.get("destination", "").strip()
    depart_time = data.get("depart_time", "").strip()

    if not origin or not destination or not depart_time:
        return jsonify({"error": "Missing required fields"}), 400

    result = {
        "origin": origin,
        "destination": destination,
        "route_summary": f"{origin} → Bell Station → {destination}",
        "legs": [
            {
                "from_stop": origin,
                "to_stop": "Bell Station",
                "depart_time": "10:00:00",
                "arrive_time": "10:07:00",
                "route_name": "TRE"
            },
            {
                "from_stop": "Bell Station",
                "to_stop": destination,
                "depart_time": "10:10:00",
                "arrive_time": "10:22:00",
                "route_name": "DART Green"
            }
        ],
        "metrics": {
            "total_ride_minutes": 19,
            "total_wait_minutes": 3,
            "comfort_score": 0.84
        }
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=False)
