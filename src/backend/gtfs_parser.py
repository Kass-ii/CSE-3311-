import os
import pandas as pd


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data")




def load_gtfs():
   stops = pd.read_csv(os.path.join(DATA_PATH, "stops.txt"))
   routes = pd.read_csv(os.path.join(DATA_PATH, "routes.txt"))
   trips = pd.read_csv(os.path.join(DATA_PATH, "trips.txt"))
   stop_times = pd.read_csv(os.path.join(DATA_PATH, "stop_times.txt"))
   shapes = pd.read_csv(os.path.join(DATA_PATH, "shapes.txt"))


   print("Stops loaded:", len(stops))
   print("Routes loaded:", len(routes))
   print("Trips loaded:", len(trips))
   print("Stop Times loaded:", len(stop_times))
   print("Route Shapes loaded:", len(shapes))


   return stops, routes, trips, stop_times, shapes




if __name__ == "__main__":
   load_gtfs()
