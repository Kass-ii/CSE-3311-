from gtfs_parser import load_gtfs
from routing import plan_backtrack_same_line


def main():
    stops, routes, trips, stop_times = load_gtfs()

    start = input("Start station (type part of name): ").strip()
    start_after = input("Start after time (HH:MM:SS): ").strip()
    return_by = input("Return by time (HH:MM:SS): ").strip()

    result = plan_backtrack_same_line(
        start_query=start,
        return_by=return_by,
        start_after=start_after,
        stops=stops,
        routes=routes,
        trips=trips,
        stop_times=stop_times
    )

    print("\nIteration 1 Plan:")
    print(result)


if __name__ == "__main__":
    main()
