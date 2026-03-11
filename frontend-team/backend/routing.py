import pandas as pd


def time_to_seconds(t: str) -> int:
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


def seconds_to_time(sec: int) -> str:
    h = sec // 3600
    sec %= 3600
    m = sec // 60
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def plan_backtrack_same_line(start_query, start_after, return_by,
                             stops, routes, trips, stop_times):

    # Find start station stop_ids (partial match)
    start_matches = stops[
        stops["stop_name"].str.lower().str.contains(
            start_query.lower(), na=False)
    ]
    if start_matches.empty:
        return {"error": "Start stop not found"}

    start_ids = start_matches["stop_id"].unique()

    start_after_sec = time_to_seconds(start_after)
    return_by_sec = time_to_seconds(return_by)

    # Pick a route serving this stop (most common route among trips that stop here)
    trips_at_start = stop_times[stop_times["stop_id"].isin(
        start_ids)][["trip_id"]].drop_duplicates()
    trips_at_start = trips_at_start.merge(
        trips[["trip_id", "route_id", "direction_id"]], on="trip_id", how="inner")

    if trips_at_start.empty:
        return {"error": "No trips serve this stop"}

    route_id = trips_at_start["route_id"].value_counts().index[0]

    route_row = routes[routes["route_id"] == route_id]
    route_name = None
    if not route_row.empty:
        route_name = route_row.iloc[0].get(
            "route_short_name") or route_row.iloc[0].get("route_long_name")

    # Filter to this route only
    route_trips = trips[trips["route_id"] ==
                        route_id][["trip_id", "direction_id"]]
    route_stop_times = stop_times.merge(route_trips, on="trip_id", how="inner")

    # Candidate departures from start after start_after
    dep = route_stop_times[route_stop_times["stop_id"].isin(start_ids)][
        ["trip_id", "departure_time", "stop_sequence", "direction_id", "stop_id"]
    ].copy()
    dep["dep_sec"] = dep["departure_time"].apply(time_to_seconds)
    dep = dep[(dep["dep_sec"] >= start_after_sec)
              & (dep["dep_sec"] <= return_by_sec)]

    if dep.empty:
        return {"error": "No departures found in time window", "route_id": str(route_id), "route_name": route_name}

    dep = dep.sort_values("dep_sec").head(80)

    best = None

    for _, leg1 in dep.iterrows():
        trip1 = leg1["trip_id"]
        dir1 = leg1["direction_id"]
        dep1 = int(leg1["dep_sec"])
        start_seq = leg1["stop_sequence"]

        # Stops after the start on trip1 are possible turn-around points
        trip1_stops = route_stop_times[route_stop_times["trip_id"] == trip1][
            ["stop_id", "arrival_time", "stop_sequence"]
        ].copy()
        trip1_stops["arr_sec"] = trip1_stops["arrival_time"].apply(
            time_to_seconds)
        trip1_stops = trip1_stops[trip1_stops["stop_sequence"] > start_seq].sort_values(
            "stop_sequence").head(25)

        for _, turn in trip1_stops.iterrows():
            turn_stop = turn["stop_id"]
            arr_turn = int(turn["arr_sec"])

            # Prefer opposite direction for return if direction_id exists
            if pd.notna(dir1):
                cand = route_stop_times[route_stop_times["direction_id"] != dir1]
            else:
                cand = route_stop_times

            # Depart from turn_stop after arriving there
            ret_dep = cand[cand["stop_id"] == turn_stop][
                ["trip_id", "departure_time", "stop_sequence"]
            ].copy()
            if ret_dep.empty:
                continue

            ret_dep["dep2_sec"] = ret_dep["departure_time"].apply(
                time_to_seconds)
            ret_dep = ret_dep[ret_dep["dep2_sec"] >=
                              arr_turn].sort_values("dep2_sec").head(10)

            for _, leg2 in ret_dep.iterrows():
                trip2 = leg2["trip_id"]
                dep2 = int(leg2["dep2_sec"])
                turn_seq = leg2["stop_sequence"]

                # Find arrival back at start stop after the turn point
                trip2_stops = cand[cand["trip_id"] == trip2][
                    ["stop_id", "arrival_time", "stop_sequence"]
                ].copy()
                trip2_stops["arr2_sec"] = trip2_stops["arrival_time"].apply(
                    time_to_seconds)

                back = trip2_stops[
                    (trip2_stops["stop_id"].isin(start_ids)) &
                    (trip2_stops["stop_sequence"] > turn_seq)
                ].sort_values("stop_sequence")

                if back.empty:
                    continue

                arr_back = int(back.iloc[0]["arr2_sec"])
                if arr_back > return_by_sec:
                    continue

                ride1 = arr_turn - dep1
                ride2 = arr_back - dep2
                total_ride = ride1 + ride2
                wait_turn = dep2 - arr_turn

                # Look up turn stop name
                turn_stop_row = stops[stops["stop_id"] == turn_stop]
                turn_stop_name = None
                if not turn_stop_row.empty:
                    turn_stop_name = turn_stop_row.iloc[0]["stop_name"]

                plan = {
                    "route_id": str(route_id),
                    "route_name": route_name,
                    "leg1": {
                        "trip_id": int(trip1),
                        "depart_start": seconds_to_time(dep1),
                        "turn_stop_id": str(turn_stop),
                        "turn_stop_name": turn_stop_name,
                        "arrive_turn": seconds_to_time(arr_turn),
                        "ride_minutes": round(ride1 / 60, 1)
                    },
                    "leg2": {
                        "trip_id": int(trip2),
                        "depart_turn": seconds_to_time(dep2),
                        "arrive_back": seconds_to_time(arr_back),
                        "ride_minutes": round(ride2 / 60, 1)
                    },
                    "metrics": {
                        "total_ride_minutes": round(total_ride / 60, 1),
                        "turn_wait_minutes": round(wait_turn / 60, 1)
                    }
                }

                if best is None:
                    best = plan
                else:
                    if plan["metrics"]["total_ride_minutes"] > best["metrics"]["total_ride_minutes"]:
                        best = plan
                    elif plan["metrics"]["total_ride_minutes"] == best["metrics"]["total_ride_minutes"]:
                        if plan["metrics"]["turn_wait_minutes"] < best["metrics"]["turn_wait_minutes"]:
                            best = plan

    if best is None:
        return {
            "error": "No out-and-back plan found on this single route in the time window.",
            "route_id": str(route_id),
            "route_name": route_name
        }

    return best
