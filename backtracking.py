def backtrack_same_line(current_index, trip_stops, current_path, visited, return_by, best_plan_holder):

    current_row = trip_stops[current_index]
    current_time = current_row.get("arrival_time")

    if current_time is not None and current_time > return_by:
        return

   
    if valid_out_and_back(current_path):
        if better_plan(current_path, best_plan_holder[0]):
            best_plan_holder[0] = current_path.copy()

    next_index = current_index + 1

    if next_index >= len(trip_stops):
        return

    next_row = trip_stops[next_index]
    next_stop_id = next_row.get("stop_id")

    if next_stop_id not in visited:
        current_path.append(next_stop_id)
        visited.add(next_stop_id)

        backtrack_same_line(
            next_index,
            trip_stops,
            current_path,
            visited,
            return_by,
            best_plan_holder
        )

       
        current_path.pop()
        visited.remove(next_stop_id)


def backtracking(start_query, start_after, return_by, stops, routes, trips, stop_times):
    
    matching_stops = all_matching_stops(start_query, stops)

    if matching_stops is None or len(matching_stops) == 0:
        return None

    best_plan_holder = [None]

    for one_stop in matching_stops:
        start_stop_id = one_stop.get("stop_id")

        candidate_rows = find_candidate_trips(start_stop_id, start_after, stop_times)

        for row in candidate_rows:
            trip_id = row.get("trip_id")

            trip_stops = get_trip_stop_sequence(trip_id, stop_times)

            start_index = None
            for i in range(len(trip_stops)):
                if trip_stops[i].get("stop_id") == start_stop_id:
                    start_index = i
                    break

            if start_index is None:
                continue

            current_path = [start_stop_id]
            visited = {start_stop_id}

            backtrack_same_line(
                start_index,
                trip_stops,
                current_path,
                visited,
                return_by,
                best_plan_holder
            )

    return best_plan_holder[0]