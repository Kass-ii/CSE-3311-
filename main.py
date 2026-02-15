#!/usr/bin/env python3

import gtfs_kit as gk
import os


if __name__ == "__main__":
	print(gk.list_feed(f"{os.getcwd()}/gtfs/DART.zip"))