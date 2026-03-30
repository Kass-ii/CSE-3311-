# This file is the Flask backend API for our ComfortRoute project.
# Its job is to receive requests from the frontend (React), compute a route using GTFS data, and return the result as JSON.

from flask import Flask, request, jsonify
from flask_cors import CORS

from gtfs_parser import load_gtfs
from routing import plan_backtrack_same_line

app = Flask(__name__)
CORS(app)

# Load GTFS once when server starts
stops, routes, trips, stop_times = load_gtfs()


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
    station_rows = stops.copy()

    # Keep rows with coordinates
    station_rows = station_rows[["stop_id", "stop_name", "stop_lat", "stop_lon"]].dropna()

    # Filter for likely rail stations by name
    rail_keywords = [
        "station",
        "rail",
        "tre",
        "dart rail",
        "green line",
        "red line",
        "blue line",
        "orange line"
    ]

    station_rows = station_rows[
        station_rows["stop_name"].str.lower().apply(
            lambda name: any(keyword in name for keyword in rail_keywords)
        )
    ]

    # Remove duplicates by station name + coordinates
    station_rows = station_rows.drop_duplicates(subset=["stop_name", "stop_lat", "stop_lon"])

    stations_data = []
    for _, row in station_rows.iterrows():
        stations_data.append({
            "stop_id": str(row["stop_id"]),
            "stop_name": row["stop_name"],
            "lat": float(row["stop_lat"]),
            "lng": float(row["stop_lon"])
        })

    return jsonify(stations_data)

@app.route("/transitCenters", methods=["GET"])
def getTransitCenters():
	"""" Data is hardcoded for now """
	transitCenters = [
		{'name': 'Addison Transit Center', 'stop_id': [33245, 33596]},
		{'name': 'Arapaho Center Station', 'stop_id': [33224, 26673]}, 
		{'name': 'Bernal/Singleton Transfer Location', 'stop_id': [30488, 33262]}, 
		{'name': 'CBD East Transfer Center', 'stop_id': [33242]}, 
		{'name': 'CBD West Transfer Center', 'stop_id': [33318]},
		{'name': 'CBD West Transfer Center', 'stop_id': [33318]}, 
		{'name': 'Cockrell Hill Transfer Location', 'stop_id': [33257]}, 
		{'name': 'Downtown Garland Station', 'stop_id': [26691]}, 
		{'name': 'Downtown Irving/Heritage Crossing Station', 'stop_id': [33229]}, 
		{'name': 'Hampton Station', 'stop_id': [33241]}, 
		{'name': 'Illinois Station', 'stop_id': [21030]}, 
		{'name': 'Jack Hatchell Transit Center', 'stop_id': [33233]}, 
		{'name': 'J.B. Jackson Transit Center', 'stop_id': [33310, 33312]}, 
		{'name': 'Lake June Station', 'stop_id': [33287, 29833]}, 
		{'name': 'Lake Ray Hubbard Transit Center', 'stop_id': [33234]}, 
		{'name': 'Ledbetter Station', 'stop_id': [33243, 23320]}, 
		{'name': 'Parker Road Station', 'stop_id': [26897, 33276]}, 
		{'name': 'Red Bird Transit Center', 'stop_id': [33228]}, 
		{'name': 'South Garland Transit Center', 'stop_id': [33221]}, 
		{'name': 'Westmoreland Station', 'stop_id': [15913, 33227]}
	]
	stopIDs = [33245, 33596, 33224, 26673, 30488, 33262, 33242, 33318, 33318, 33257, 26691, 33229, 33241, 21030, 33233, 33310, 33312, 33287, 29833, 33234, 33243, 23320, 26897, 33276, 33228, 33221, 15913, 33227]
	station_rows = stops.copy()
	station_rows = station_rows[["stop_id", "stop_name", "stop_lat", "stop_lon"]].dropna()
	station_rows = station_rows[
		station_rows["stop_id"].astype(str).isin([str(sid) for sid in stopIDs])
	]


	return jsonify(station_rows)

if __name__ == "__main__":
    app.run(debug=False)
	