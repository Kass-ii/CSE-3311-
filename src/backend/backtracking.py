from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import pandas as pd


@dataclass
class StopMatch:
    stop_id: str
    stop_name: str


@dataclass
class OutboundCandidate:
    route_id: str
    route_name: str
    outbound_trip_id: str
    start_stop_id: str
    start_stop_name: str
    dest_stop_id: str
    dest_stop_name: str
    depart_time: int
    arrive_dest_time: int
    start_sequence: int
    dest_sequence: int


@dataclass
class ReturnCandidate:
    return_trip_id: str
    depart_dest_time: int
    arrive_start_time: int


def time_to_seconds(time_str: str) -> int:
    parts = time_str.strip().split(":")
    if len(parts) != 3:
        raise ValueError(f"Invalid time format: {time_str}. Expected HH:MM:SS")
    hours, minutes, seconds = map(int, parts)
    return hours * 3600 + minutes * 60 + seconds


def seconds_to_time(total_seconds: int) -> str:
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def _safe_str(value: Any) -> str:
    return "" if pd.isna(value) else str(value)


def _get_route_name(route_row: pd.Series) -> str:
    short_name = _safe_str(route_row.get("route_short_name", ""))
    long_name = _safe_str(route_row.get("route_long_name", ""))

    if short_name and long_name:
        return f"{short_name} - {long_name}"
    if short_name:
        return short_name
    if long_name:
        return long_name
    return _safe_str(route_row.get("route_id", "Unknown Route"))


def find_matching_stops(stops: pd.DataFrame, query: str) -> List[StopMatch]:
    q = query.strip().lower()
    if not q:
        return []

    matches = stops[
        stops["stop_name"].astype(str).str.lower().str.contains(q, na=False)
    ].copy()

    result: List[StopMatch] = []
    for _, row in matches.iterrows():
        result.append(
            StopMatch(
                stop_id=_safe_str(row["stop_id"]),
                stop_name=_safe_str(row["stop_name"])
            )
        )
    return result


def choose_best_stop_match(matches: List[StopMatch], query: str) -> Optional[StopMatch]:
    if not matches:
        return None

    q = query.strip().lower()

    for match in matches:
        if match.stop_name.lower() == q:
            return match

    for match in matches:
        if match.stop_name.lower().startswith(q):
            return match

    return matches[0]


def prepare_stop_times(stop_times: pd.DataFrame) -> pd.DataFrame:
    df = stop_times.copy()

    df["trip_id"] = df["trip_id"].astype(str)
    df["stop_id"] = df["stop_id"].astype(str)
    df["stop_sequence"] = df["stop_sequence"].astype(int)

    df["arrival_secs"] = df["arrival_time"].apply(time_to_seconds)
    df["departure_secs"] = df["departure_time"].apply(time_to_seconds)

    return df


def prepare_trips(trips: pd.DataFrame) -> pd.DataFrame:
    df = trips.copy()
    df["trip_id"] = df["trip_id"].astype(str)
    df["route_id"] = df["route_id"].astype(str)
    return df


def build_trip_to_rows(stop_times: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    trip_to_rows: Dict[str, pd.DataFrame] = {}
    for trip_id, group in stop_times.groupby("trip_id", sort=False):
        trip_to_rows[str(trip_id)] = group.sort_values("stop_sequence").copy()
    return trip_to_rows


def get_start_trip_rows(
    stop_times: pd.DataFrame,
    trips: pd.DataFrame,
    start_stop_id: str,
    start_after_secs: int
) -> pd.DataFrame:
    start_stop_id = str(start_stop_id)

    start_rows = stop_times[
        (stop_times["stop_id"] == start_stop_id) &
        (stop_times["departure_secs"] >= start_after_secs)
    ].copy()

    if start_rows.empty:
        return start_rows

    merged = start_rows.merge(
        trips[["trip_id", "route_id"]],
        on="trip_id",
        how="left"
    )
    return merged.sort_values("departure_secs")


def build_outbound_candidates(
    start_rows: pd.DataFrame,
    stop_times: pd.DataFrame,
    stops: pd.DataFrame,
    routes: pd.DataFrame,
    trip_to_rows: Dict[str, pd.DataFrame]
) -> List[OutboundCandidate]:
    stop_name_map: Dict[str, str] = {
        _safe_str(row["stop_id"]): _safe_str(row["stop_name"])
        for _, row in stops.iterrows()
    }

    route_name_map: Dict[str, str] = {}
    for _, row in routes.iterrows():
        route_name_map[_safe_str(row["route_id"])] = _get_route_name(row)

    candidates: List[OutboundCandidate] = []

    for _, start_row in start_rows.iterrows():
        trip_id = _safe_str(start_row["trip_id"])
        route_id = _safe_str(start_row["route_id"])
        start_stop_id = _safe_str(start_row["stop_id"])
        start_sequence = int(start_row["stop_sequence"])
        depart_time = int(start_row["departure_secs"])

        trip_stop_rows = trip_to_rows.get(trip_id)
        if trip_stop_rows is None or trip_stop_rows.empty:
            continue

        downstream_rows = trip_stop_rows[trip_stop_rows["stop_sequence"] > start_sequence]

        for _, dest_row in downstream_rows.iterrows():
            dest_stop_id = _safe_str(dest_row["stop_id"])
            dest_sequence = int(dest_row["stop_sequence"])
            arrive_dest_time = int(dest_row["arrival_secs"])

            if dest_stop_id == start_stop_id:
                continue

            candidates.append(
                OutboundCandidate(
                    route_id=route_id,
                    route_name=route_name_map.get(route_id, route_id),
                    outbound_trip_id=trip_id,
                    start_stop_id=start_stop_id,
                    start_stop_name=stop_name_map.get(start_stop_id, start_stop_id),
                    dest_stop_id=dest_stop_id,
                    dest_stop_name=stop_name_map.get(dest_stop_id, dest_stop_id),
                    depart_time=depart_time,
                    arrive_dest_time=arrive_dest_time,
                    start_sequence=start_sequence,
                    dest_sequence=dest_sequence
                )
            )

    return candidates


def find_return_candidate(
    outbound: OutboundCandidate,
    trips: pd.DataFrame,
    return_by_secs: int,
    trip_to_rows: Dict[str, pd.DataFrame]
) -> Optional[ReturnCandidate]:
    route_trip_ids = trips.loc[
        trips["route_id"] == str(outbound.route_id),
        "trip_id"
    ].unique()

    if len(route_trip_ids) == 0:
        return None

    best_return: Optional[ReturnCandidate] = None

    dest_stop_id = str(outbound.dest_stop_id)
    start_stop_id = str(outbound.start_stop_id)

    for trip_id in route_trip_ids:
        trip_id = str(trip_id)

        if trip_id == str(outbound.outbound_trip_id):
            continue

        same_trip_rows = trip_to_rows.get(trip_id)
        if same_trip_rows is None or same_trip_rows.empty:
            continue

        possible_dest_rows = same_trip_rows[
            (same_trip_rows["stop_id"] == dest_stop_id) &
            (same_trip_rows["departure_secs"] >= outbound.arrive_dest_time) &
            (same_trip_rows["departure_secs"] <= return_by_secs)
        ].copy()

        if possible_dest_rows.empty:
            continue

        for _, dest_row in possible_dest_rows.iterrows():
            dest_sequence = int(dest_row["stop_sequence"])
            depart_dest_time = int(dest_row["departure_secs"])

            possible_start_rows = same_trip_rows[
                (same_trip_rows["stop_id"] == start_stop_id) &
                (same_trip_rows["stop_sequence"] > dest_sequence) &
                (same_trip_rows["arrival_secs"] <= return_by_secs)
            ].copy()

            if possible_start_rows.empty:
                continue

            earliest_valid = possible_start_rows.sort_values("arrival_secs").iloc[0]

            return_candidate = ReturnCandidate(
                return_trip_id=trip_id,
                depart_dest_time=depart_dest_time,
                arrive_start_time=int(earliest_valid["arrival_secs"])
            )

            if (
                best_return is None or
                return_candidate.depart_dest_time > best_return.depart_dest_time
            ):
                best_return = return_candidate

    return best_return


def _build_plan_dict(
    outbound: OutboundCandidate,
    ret: ReturnCandidate
) -> Dict[str, Any]:
    stop_distance = outbound.dest_sequence - outbound.start_sequence
    layover_secs = ret.depart_dest_time - outbound.arrive_dest_time
    ride_outbound_secs = outbound.arrive_dest_time - outbound.depart_time
    ride_return_secs = ret.arrive_start_time - ret.depart_dest_time
    total_trip_secs = ret.arrive_start_time - outbound.depart_time

    return {
        "route_id": outbound.route_id,
        "route_name": outbound.route_name,
        "start_stop_id": outbound.start_stop_id,
        "start_stop_name": outbound.start_stop_name,
        "destination_stop_id": outbound.dest_stop_id,
        "destination_stop_name": outbound.dest_stop_name,
        "outbound_trip_id": outbound.outbound_trip_id,
        "return_trip_id": ret.return_trip_id,
        "outbound_depart_time": seconds_to_time(outbound.depart_time),
        "outbound_arrive_time": seconds_to_time(outbound.arrive_dest_time),
        "return_depart_time": seconds_to_time(ret.depart_dest_time),
        "return_arrive_time": seconds_to_time(ret.arrive_start_time),
        "backtracking_depth": stop_distance,
        "layover_minutes": round(layover_secs / 60, 1),
        "outbound_ride_minutes": round(ride_outbound_secs / 60, 1),
        "return_ride_minutes": round(ride_return_secs / 60, 1),
        "total_trip_minutes": round(total_trip_secs / 60, 1),
        "comparison_summary": (
            f"{outbound.start_stop_name} -> {outbound.dest_stop_name} via {outbound.route_name} | "
            f"depart {seconds_to_time(outbound.depart_time)} | return {seconds_to_time(ret.depart_dest_time)} | "
            f"depth {stop_distance}"
        ),
    }


def find_multiple_backtrack_options(
    start_query: str,
    return_by: str,
    start_after: str,
    stops: pd.DataFrame,
    routes: pd.DataFrame,
    trips: pd.DataFrame,
    stop_times: pd.DataFrame,
    limit: int = 5
) -> Dict[str, Any]:
    try:
        start_after_secs = time_to_seconds(start_after)
        return_by_secs = time_to_seconds(return_by)
    except ValueError as exc:
        return {"error": f"Invalid time input: {exc}"}

    if return_by_secs <= start_after_secs:
        return {"error": "Return-by time must be later than start-after time."}

    stop_times_prepped = prepare_stop_times(stop_times)
    trips_prepped = prepare_trips(trips)
    trip_to_rows = build_trip_to_rows(stop_times_prepped)

    stop_matches = find_matching_stops(stops, start_query)
    if not stop_matches:
        return {"error": f'No stop found matching "{start_query}".'}

    start_stop = choose_best_stop_match(stop_matches, start_query)
    if start_stop is None:
        return {"error": f'No usable stop found matching "{start_query}".'}

    print(f"[DEBUG] selected start stop: {start_stop.stop_name} ({start_stop.stop_id})")

    start_rows = get_start_trip_rows(
        stop_times=stop_times_prepped,
        trips=trips_prepped,
        start_stop_id=start_stop.stop_id,
        start_after_secs=start_after_secs
    )

    if start_rows.empty:
        return {
            "error": f'No trips leave from "{start_stop.stop_name}" after {start_after}.'
        }

    print(f"[DEBUG] candidate start rows: {len(start_rows)}")

    outbound_candidates = build_outbound_candidates(
        start_rows=start_rows,
        stop_times=stop_times_prepped,
        stops=stops,
        routes=routes,
        trip_to_rows=trip_to_rows
    )

    if not outbound_candidates:
        return {
            "error": f'No downstream stops found from "{start_stop.stop_name}" after {start_after}.'
        }

    print(f"[DEBUG] outbound candidates: {len(outbound_candidates)}")

    valid_plans: List[Dict[str, Any]] = []
    seen = set()

    for i, outbound in enumerate(outbound_candidates, start=1):
        if i % 250 == 0:
            print(f"[DEBUG] processed {i}/{len(outbound_candidates)} outbound candidates")

        ret = find_return_candidate(
            outbound=outbound,
            trips=trips_prepped,
            return_by_secs=return_by_secs,
            trip_to_rows=trip_to_rows
        )
        if ret is None:
            continue

        key = (
            outbound.route_id,
            outbound.start_stop_id,
            outbound.dest_stop_id,
            outbound.depart_time,
            ret.depart_dest_time
        )
        if key in seen:
            continue
        seen.add(key)

        valid_plans.append(_build_plan_dict(outbound, ret))

    if not valid_plans:
        return {
            "error": (
                f'No valid same-line backtracking trip was found from '
                f'"{start_stop.stop_name}" that returns by {return_by}.'
            )
        }

    valid_plans.sort(
        key=lambda p: (
            -p["backtracking_depth"],
            p["total_trip_minutes"],
            p["outbound_depart_time"]
        )
    )

    return {
        "start_stop": {
            "stop_id": start_stop.stop_id,
            "stop_name": start_stop.stop_name
        },
        "criteria": {
            "start_after": start_after,
            "return_by": return_by,
            "ranking": "deeper backtracking first, then shorter total trip, then earlier departure"
        },
        "option_count": min(limit, len(valid_plans)),
        "options": valid_plans[:limit]
    }


def plan_backtrack_same_line(
    start_query: str,
    return_by: str,
    start_after: str,
    stops: pd.DataFrame,
    routes: pd.DataFrame,
    trips: pd.DataFrame,
    stop_times: pd.DataFrame
) -> str:
    """
    Compatibility wrapper for your old main.py / old route behavior.
    Returns the top option as a formatted string.
    """
    result = find_multiple_backtrack_options(
        start_query=start_query,
        return_by=return_by,
        start_after=start_after,
        stops=stops,
        routes=routes,
        trips=trips,
        stop_times=stop_times,
        limit=1
    )

    if "error" in result:
        return result["error"]

    best = result["options"][0]
    return (
        f"Start stop: {best['start_stop_name']}\n"
        f"Route: {best['route_name']}\n\n"
        f"Outbound:\n"
        f"  Trip ID: {best['outbound_trip_id']}\n"
        f"  Leave {best['start_stop_name']} at {best['outbound_depart_time']}\n"
        f"  Arrive {best['destination_stop_name']} at {best['outbound_arrive_time']}\n\n"
        f"Return:\n"
        f"  Trip ID: {best['return_trip_id']}\n"
        f"  Leave {best['destination_stop_name']} at {best['return_depart_time']}\n"
        f"  Arrive {best['start_stop_name']} at {best['return_arrive_time']}\n\n"
        f"Backtracking depth: {best['backtracking_depth']} stop(s)\n"
        f"Layover at destination: {best['layover_minutes']} minute(s)"
    )


if __name__ == "__main__":
    from gtfs_parser import load_gtfs
    import datetime

    stops, routes, trips, stop_times, shapes = load_gtfs()
    start_after = datetime.datetime.now().strftime("%H:%M:%S")

    result = plan_backtrack_same_line(
        start_query="SMU/MOCKINGBIRD STATION",
        start_after=start_after,
        return_by="23:00:00",
        stops=stops,
        routes=routes,
        trips=trips,
        stop_times=stop_times
    )
    print(result)