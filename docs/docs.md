## Setup
- A virtual environment is recommended to manage dependencies, but not included in the repository. Create one with the command:
	- `python3 -m venv .venv`
	- and use the command `source .venv/bin/activate` to launch it
	- use deactivate to stop it
- generate requirements.txt with `.venv/bin/pip freeze > requirements.txt`
- execute `main.py` in the venv with `.venv/bin/python -m main`
- 

## Libraries
- gtfs kit [repo](https://github.com/araichev/gtfs_kit)
- use `buildDB.py` to build GTFS DB	


## GTFS
- DART GTFS [source](https://www.dart.org/about/about-dart/fixed-route-schedule)
	- latest [url](https://www.dart.org/transitdata/latest/google_transit.zip)
- GTFS [documentation](https://gtfs.org/documentation/schedule/reference/)