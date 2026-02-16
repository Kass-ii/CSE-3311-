#!/usr/bin/env python3

#import gtfs_kit as gk
import os
import sqlite3
import datetime
class Router:

	def __init__():
		self.userStop = 22748

	def getRoutesServingStop(self, stop_id = self.userStop):
		databasePath = f"{os.getcwd()}/gtfs/gtfs.sqlite"
		conn = sqlite3.connect(databasePath)
		cur = conn.cursor()
		trips = f"""
			SELECT DISTINCT r.route_id
			FROM routes r
			JOIN trips t      ON r.route_id = t.route_id
			JOIN stop_times s ON t.trip_id = s.trip_id
			WHERE s.stop_id = '{stop_id}';
		"""
		cur.execute(trips)
		rows = cur.fetchall()	
		conn.close()
		routes = [row[0] for row in rows]
		return routes

	def getNDeparture(self, N, stop_id=self.userStop, timeStamp=None):
		"""
		Fetches the next N departures from stop_id, after timeStamp
		Where timeStamp is a string fromated "HH:MM:SS"
		"""
		if timeStamp == None:
			now = datetime.datetime.now()
			timeStamp = now.strftime("%H:%M:%S")

		databasePath = f"{os.getcwd()}/gtfs/gtfs.sqlite"
		conn = sqlite3.connect(databasePath)
		cur = conn.cursor()

		query = f"""
		SELECT stop_times.*
		FROM stop_times
		WHERE stop_id == ? AND stop_times.departure_time > ?
		limit ?
		"""
		cur.execute(query, [stop_id, timeStamp, N])
		rows = cur.fetchall()
		conn.close()
		return rows


if __name__ == "__main__":
	#print(gk.list_feed(f"{os.getcwd()}/gtfs/DART.zip"))
	routr = Router()
	
	for depart in departures:
		print(depart)