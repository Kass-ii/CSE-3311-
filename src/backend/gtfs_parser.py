import pandas as pd

# our transit data files live here
DATA_PATH = "../data/"

# function to load all the GTFS (transit schedule) files into pandas DataFrames


def load_gtfs():
	# Load each GTFS file into a DataFrame
	stops = pd.read_csv(DATA_PATH + "stops.txt")
	routes = pd.read_csv(DATA_PATH + "routes.txt")
	trips = pd.read_csv(DATA_PATH + "trips.txt")
	stop_times = pd.read_csv(DATA_PATH + "stop_times.txt")
	shapes = pd.read_csv(DATA_PATH + "shapes.txt")
	# printing out how many records we loaded from each file
	print("Stops loaded:", len(stops))
	print("Routes loaded:", len(routes))
	print("Trips loaded:", len(trips))
	print("Stop Times loaded:", len(stop_times))
	print("Route Shapes loaded:", len(shapes))

	# return all loaded data
	return stops, routes, trips, stop_times, shapes

if __name__ == "__main__":
	load_gtfs()
