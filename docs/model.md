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
- trip <stop_times> stop, time
- route <trips> trip, shape
### App relationships
- Router <generates> Trip
- User <queries> Router