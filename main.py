#!/usr/bin/env python3

#import gtfs_kit as gk
import os
import sqlite3
import datetime

def strToDate(str):
	return datetime.strptime(str, "%H:%M:%S")

class Router:

	def __init__(self):
		self.userStop = 22748

	def queryDict(self, query, parameters=None):
		""" Python wrapper to send SQL requests to GTFS DB """
		databasePath = f"{os.getcwd()}/gtfs/gtfs.sqlite"
		conn = sqlite3.connect(databasePath)
		with conn:
			conn.row_factory = sqlite3.Row
			cur = conn.cursor()
			if parameters == None:
				cur.execute(query)
			else:
				cur.execute(query, parameters)
			rows = cur.fetchall()	
		

		return rows
	def getRoutesServingStop(self, stop_id = None):
		"""" identifies routes serving selected stop_id """
		if stop_id == None:
			stop_id = self.userStop
			
		trips = f"""
			SELECT DISTINCT r.route_id
			FROM routes r
			JOIN trips t      ON r.route_id = t.route_id
			JOIN stop_times s ON t.trip_id = s.trip_id
			WHERE s.stop_id = ?;
		"""
		rows=self.queryDict(trips,[stop_id])
		routes = [row[0] for row in rows]
		print(routes)
		return routes
	
	def getNDeparturesPerLinePerDirection(self, N, stop_id=None, timeStamp=None):
		"""
		Fetches the next N departures from stop_id, after timeStamp, per line, per direction (asssumed to only be two)
		"""
		if timeStamp == None:
			timeStamp = datetime.datetime.now().strftime("%H:%M:%S")
		if stop_id==None:
			stop_id = self.userStop

		routes = self.getRoutesServingStop()
		rows = []
		for route in routes:
			# number of directions for DART GTFS does not exceed 0/1, cannot assume for other agencies
			for direction in (0,1):
				query = """
				SELECT r.route_short_name, t.route_id, t.direction_id, st.trip_id, st.stop_id, st.arrival_time, st.departure_time, st.stop_sequence
				FROM stop_times AS st, trips AS t, routes AS r
				WHERE st.stop_id == ? AND st.departure_time > ?  AND t.trip_id == st.trip_id AND t.route_id == ? AND t.route_id == r.route_id AND t.direction_id == ?
				limit ?
				"""
				rows.append(self.queryDict(query, [stop_id, timeStamp, route, direction, N]))
		return rows
		
	def getNextNStops(self, trip_id, stop_sequence, N):
		""" Calculate next N stops on a trip"""
		query = """
		SELECT *
		FROM stop_times
		WHERE trip_id == ? AND stop_sequence > ?
		LIMIT ?
		"""

		return queryDict(query, [trip_id, stop_sequence, N])

	def findOutAndBack(self, deadline, startTime=None, stop_id=None):
		""""
		Method name pending
		"""
		departures = getNDeparturesPerLine(3, stop_id, startTime)

		if departures[0][2] >= deadline:
			# need to develop better heurestic
			return
		
		
if __name__ == "__main__":
	#print(gk.list_feed(f"{os.getcwd()}/gtfs/DART.zip"))
	router = Router()
	
	for line in router.getNDeparturesPerLinePerDirection(2):
		for departure in line:
			print(' | '.join(departure))