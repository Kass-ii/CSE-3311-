#!/usr/bin/env python3

#import gtfs_kit as gk
import os
import sqlite3

def getRoutesServingStop(stop_id = 22748):
	databasePath = f"{os.getcwd()}/gtfs/gtfs.sqlite"
	conn = sqlite3.connect(databasePath)
	cur = conn.cursor()
	trips = f"""
		SELECT DISTINCT r.*
		FROM routes r
		JOIN trips t      ON r.route_id = t.route_id
		JOIN stop_times s ON t.trip_id = s.trip_id
		WHERE s.stop_id = '{stop_id}';
	"""
	cur.execute(trips)
	rows = cur.fetchall()
	for row in rows:
		print(row)


if __name__ == "__main__":
	#print(gk.list_feed(f"{os.getcwd()}/gtfs/DART.zip"))
	getRoutesServingStop()