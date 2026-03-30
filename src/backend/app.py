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
# list of stop_ids corresponding to transit centers and indoor stations.
indoorIDs = [33245, 33596, 33224, 26673, 30488, 33262, 33242, 33318, 33318, 33257, 26691, 33229, 33241, 21030, 33233, 33310, 33312, 33287, 29833, 33234, 33243, 23320, 26897, 33276, 33228, 33221, 15913, 33227, 22748, 26420]


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
	station_rows = station_rows.drop_duplicates(subset=["stop_name", "stop_lat", "stop_lon"]);
	station_rows["indoors"] = station_rows["stop_id"].astype(str).isin([str(sid) for sid in indoorIDs]).astype(int)
	stations_data = []
	for _, row in station_rows.iterrows():
		stations_data.append({
			"stop_id": str(row["stop_id"]),
			"stop_name": row["stop_name"],
			"lat": float(row["stop_lat"]),
			"lng": float(row["stop_lon"]),
			"indoors": int(row["indoors"]) 
		})
	#return stations_data
	return jsonify(stations_data, indent=2)

if __name__ == "__main__":
	app.run(debug=False)
	