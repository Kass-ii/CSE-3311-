## Domain Concepts
- router class
- Trip class
	- encapsulates trip directions
	- need to serialize to send to front end
- user class
- region class
	- holds metadata about the region, its transit agencies, GTFS links, and frequency to update
### GTFS concepts
- stops
- routes
- stations
- trips
- blocks
- shapes
- time

## Relationships
 - concept <relation> concept
### GTFS relationships
- trip (1) <stop_times> (n : (1,2)) stop, time
	- 1 trip has n stops, each stop has 2 times
- route (1) <trips> (n,1?) trip, shape
	- each route has n trips, all trips *should* have the same shape
		- need to verify whether shapes are constant
### App relationships
- Router (1) <generates> (n) Trip
- User (n) <queries> (1) Router