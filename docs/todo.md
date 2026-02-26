## Immediate
- [x] Identify routes that serve a stop
- [x] Find next departure from stop along routes
- Calculate maximum trip along one line, returning to the origin at a specific time
	- start with first departure
## Medium
- Generate visual representation of a suggested trip
	- path of a route defined in `shapes.txt` and related to `trips.txt` by `shape_id`
## Long term
- Identify stations with indoor facilities from OSM data
	- add operating hours to stops table
## Misc
- remove unneeded packages
- convert tuple queries to dict queries
- mix of object and string datetimes, need to standardize on objects
---
- in class exercise
# Requirements
- App will generate route in under 10 seconds
- App must generate a visual representation of trip
- Algorithm must minimize time spent outdoors
	- Request directions from other directions app and calculate the time spent outdoors to compare to our output.
	- Compare output to rider behavior to identify any missed opportunities for optimization.
- Constrain algorithm to generate trips under certain classes of fare 
	- 3 hour pass, 
	- do not cross regional fare boundary etc
- Allow user to specify comfortable transfer times
- UI must be intuitive to users
	- Measure time it takes for users to generate directions
	- Create survey about layout of the app
		- Users will be friends who use public transit