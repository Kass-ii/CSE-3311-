#!/usr/bin/env python3

import sqlite3
import datetime
from pathlib import Path

def strToDate(str):
	return datetime.strptime(str, "%H:%M:%S")

class Router:

	def __init__(self):
		# default to union station
		self.userStop = 22748

	def queryDict(self, query, parameters=None):
		""" Python wrapper to send SQL requests to GTFS DB """
		databasePath = Path(__file__).parent.parent.parent / "gtfs" / "gtfs.sqlite"
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
			
		trips = """
			SELECT DISTINCT r.route_id
			FROM routes r
			JOIN trips t      ON r.route_id = t.route_id
			JOIN stop_times s ON t.trip_id = s.trip_id
			WHERE s.stop_id = ?;
		"""
		rows=self.queryDict(trips,[stop_id])
		routes = [row[0] for row in rows]
		return routes
	
	def getNDeparturesPerLinePerDirection(self, N, stop_id=None, timeStamp=None):
		"""
		Fetches the next N departures from stop_id, after timeStamp, per line, per direction (asssumed to only be two)
		returns: route_short_name, route_id, direction_id, trip_id, stop_id, arrival_time, departure_time, stop_sequence
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
		Algorithm to find max station loop time
		Currently only supports same line navigation, !!does not support interlining!! 
		"""
		def checkReturnTrip(row, direction_id):
			""" Helper function to evaluate pivots"""
			departures = self.getNDeparturesPerLinePerDirection(4, row["stop_id"], row["arrival_time"])
			for option in departures:
				nextStops = self.getNextNStops(trip_id=option[trip_id], stop_sequence=option[stop_sequence], N = 5)
				for stop in nextStops:
					if stop["stop_id"] == stop_id and strToDate(stop["arrival_time"]) < deadline:
						return True
			return False

		# loop over immediate departures from origin
		departures = getNDeparturesPerLinePerDirection(1, stop_id, startTime)
		for option in departures:
<<<<<<< Updated upstream
			outdoorTime = deadline - strToDate(option["departure_time"])
			indoorTime = 0
			nextStops = self.getNextNStops(trip_id=option[trip_id], stop_sequence=option[stop_sequence], N = 5)

			for turnaround in nextStops:
				returnTrips = self.getNDeparturesPerLinePerDirection(self,4,turnaround["arrival_time"])
				selectedTrip = None
				# find earliest return trip back along same line
				for trip in returnTrips:
					if (trip["route_id"] == option["route_id"]) and (trip["direction_id"] != option["direction_id"]):
						# check if an earlier trip has already been found
						if selectedTrip != None and trip["departure_time"] > selectedTrip["departure_time"]:
							continue
						elif selectedTrip != None and trip["departure_time"] < selectedTrip["departure_time"]:
							selectedTrip = trip
						elif selectedTrip == None:
							selectedTrip = trip
				returnStops = self.getNextNStops(trip["trip_id"], trip["stop_sequence"])

				for stop in returnStops:
					if stop["stop_id"] == stop_id:
						if stop["arrival_time"] < deadline:
							pass

				
=======
			nextStops = self.getNextNStops(trip_id=option[trip_id], stop_sequence=option[stop_sequence], N = 5)	
			
			maxPivot = None
			for pivot in nextStops:
				# Find furtherest stop you can reach and return to the origin before deadline
				# TODO improve selection criteria
				if checkReturnTrip(pivot, option["direction_id"]):
					maxPivot = pivot
				else:
					break
>>>>>>> Stashed changes
		
		
if __name__ == "__main__":
	router = Router()
	# for line in router.getNDeparturesPerLinePerDirection(2):
	# 	for departure in line:
	# 		print(' | '.join(departure))