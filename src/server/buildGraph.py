import sqlite3
from pathlib import Path
import csv
#import json
from collections import defaultdict
"""
Script to construct graph structure from GTFS DB
graph[stop_id] = [(neighbor_stop_id, departure_time, arrival_time, trip_id, cost), ...]

Graph = {stop_id : {stop_id : [ { departure_time:, arrival_time:, trip_id:, clost:}, .... ] } }
"""

def queryDB(self, query, parameters=None):
		databasePath = f"{os.getcwd()}/gtfs/gtfs.sqlite"
		conn = sqlite3.connect(databasePath)
		cur = conn.cursor()
		if parameters == None:
			cur.execute(query)
		else:
			cur.execute(query, parameters)
		rows = cur.fetchall()	
		conn.close()

		return rows

# def checkSameRoute(trip1, trip2):
# 	query = """
# 	SELECT route_id
# 	FROM trips
# 	WHERE trip_id == ?
# 	"""
# 	return queryDB(query, trip1) == queryDB(query, trip2)

if __name__ == "__main__":
	gtfsDumpPath = Path(__file__).parent.parent.parent / "gtfs" / "dump"
	print(gtfsDumpPath / "stop_times.txt")

	Graph = defaultdict(lambda: defaultdict(list))

	with open(gtfsDumpPath / "stop_times.txt") as file:
		reader = csv.DictReader(file, delimiter=",")
		
		prevRow = None
		counter = 0
		for row in reader:
			if prevRow == None:
				pass
			# simply appends on the next stop in a route
			elif row['trip_id'] == prevRow["trip_id"]:
				Graph[prevRow["stop_id"]][row["stop_id"]].append(
					{
						"departure_time": row["departure_time"],
						"arrival_time"	: row["arrival_time"],
						"trip_id"		: row["trip_id"],
						"cost"			: None
					}
				)
			prevRow = row

		#print(json.dumps(Graph, sort_keys=True, indent=4))