from gtfs_parser import load_gtfs
from backtracking import find_multiple_backtrack_options


def main():
    stops, routes, trips, stop_times, shapes = load_gtfs()

    start = input("Start station (type part of name): ").strip()
    start_after = input("Start after time (HH:MM:SS): ").strip()
    return_by = input("Return by time (HH:MM:SS): ").strip()

    result = find_multiple_backtrack_options(
        start_query=start,
        return_by=return_by,
        start_after=start_after,
        stops=stops,
        routes=routes,
        trips=trips,
        stop_times=stop_times,
        limit=5
    )

    if "error" in result:
        print("\nError:")
        print(result["error"])
        return

    print(f"\nTop {result['option_count']} Trip Options:")
    for i, option in enumerate(result["options"], start=1):
        print(f"\nOption {i}")
        print(f"  Route: {option['route_name']}")
        print(f"  Start: {option['start_stop_name']}")
        print(f"  Destination: {option['destination_stop_name']}")
        print(f"  Outbound: {option['outbound_depart_time']} -> {option['outbound_arrive_time']}")
        print(f"  Return:   {option['return_depart_time']} -> {option['return_arrive_time']}")
        print(f"  Backtracking depth: {option['backtracking_depth']}")
        print(f"  Total trip minutes: {option['total_trip_minutes']}")
        print(f"  Summary: {option['comparison_summary']}")


if __name__ == "__main__":
    main()