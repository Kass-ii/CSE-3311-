#!/usr/bin/env python3

#import gtfs_kit as gk
import os
import sqlite3
import datetime

class Router:

	def __init__(self):
		self.userStop = 22748

	def query(self, query, parameters=None):
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
	def getRoutesServingStop(self, stop_id = None):
		if stop_id == None:
			stop_id = self.userStop
		trips = f"""
			SELECT DISTINCT r.route_id
			FROM routes r
			JOIN trips t      ON r.route_id = t.route_id
			JOIN stop_times s ON t.trip_id = s.trip_id
			WHERE s.stop_id = ?;
		"""
		rows=self.query(trips,[stop_id])
		routes = [row[0] for row in rows]
		return routes

	def getNDepartures(self, N, stop_id=None, timeStamp=None):
		"""
		Fetches the next N departures from stop_id, after timeStamp
		Where timeStamp is a string fromated "HH:MM:SS"
		"""
		if timeStamp == None:
			now = datetime.datetime.now()
			timeStamp = now.strftime("%H:%M:%S")
		if stop_id==None:
			stop_id = self.userStop

		query = f"""
		SELECT stop_times.*
		FROM stop_times
		WHERE stop_id == ? AND stop_times.departure_time > ?
		limit ?
		"""
		
		rows=self.query(query, [stop_id, timeStamp, N])
		
		return rows

	def findOutAndBack(self, deadline, startTime=None, stop_id=None):
		""""
		Method name pending
		"""
		departures = getNDepartures(3, stop_id, startTime)

		#if departures[0]

if __name__ == "__main__":
	#print(gk.list_feed(f"{os.getcwd()}/gtfs/DART.zip"))
	router = Router()
	
	for depart in router.getRoutesServingStop():
		print(depart)
	for depart in router.getNDepartures(5):
		print(depart)