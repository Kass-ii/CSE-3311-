## Immediate
- Identify routes that serve a stop
- Find next departure from stop along routes
- Calculate maximum trip along one line, returning to the origin at a specific time
	- start with first departure
## Medium
- 
## Long term
- Identify stations with indoor facilities from OSM data
## Misc
- remove unneeded packages
- convert tuple queries to dict queries
- mix of object and string datetimes, need to standardize on objects

# Requirements
- App will generate route in under 10 seconds
- App must generate a visual representation of trip
- Algorithm must minimize time spent outdoors
- Constrain algorithm to generate trips under certain classes of fare 
	- 3 hour pass, 
	- do not cross regional fare boundary etc
- Allow user to specify comfortable transfer times