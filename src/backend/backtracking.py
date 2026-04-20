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
        raise ValueError(f"Invalid time format: {time_str}. Expected Hour: minutes:Seconds")

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

    matches = stops[stops["stop_name"].str.lower().str.contains(q, na=False)].copy()

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

    df["arrival_secs"] = df["arrival_time"].apply(time_to_seconds)
    df["departure_secs"] = df["departure_time"].apply(time_to_seconds)

    return df



def get_start_trip_rows(
    stop_times: pd.DataFrame,
    trips: pd.DataFrame,
    start_stop_id: str,
    start_after_secs: int
) -> pd.DataFrame:
    

    start_rows = stop_times[
        (stop_times["stop_id"].astype(str) == str(start_stop_id)) &
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
    routes: pd.DataFrame
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

        trip_stop_rows = stop_times[stop_times["trip_id"].astype(str) == trip_id].copy()
        trip_stop_rows = trip_stop_rows.sort_values("stop_sequence")

        downstream_rows = trip_stop_rows[trip_stop_rows["stop_sequence"] > start_sequence]

        for _, dest_row in downstream_rows.iterrows():
            dest_stop_id = _safe_str(dest_row["stop_id"])
            dest_sequence = int(dest_row["stop_sequence"])
            arrive_dest_time = int(dest_row["arrival_secs"])

            # skip weird duplicates / same stop names if desired
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
    stop_times: pd.DataFrame,
    trips: pd.DataFrame,
    return_by_secs: int
) -> Optional[ReturnCandidate]:
   


    route_trips = trips[trips["route_id"].astype(str) == outbound.route_id].copy()
    if route_trips.empty:
        return None

    route_trip_ids = set(route_trips["trip_id"].astype(str))

    dest_rows = stop_times[
        (stop_times["trip_id"].astype(str).isin(route_trip_ids)) &
        (stop_times["stop_id"].astype(str) == outbound.dest_stop_id) &
        (stop_times["departure_secs"] >= outbound.arrive_dest_time)
    ].copy()

    if dest_rows.empty:
        return None

    best_return: Optional[ReturnCandidate] = None

    for _, dest_row in dest_rows.iterrows():
        trip_id = _safe_str(dest_row["trip_id"])
        dest_sequence = int(dest_row["stop_sequence"])
        depart_dest_time = int(dest_row["departure_secs"])

        same_trip_rows = stop_times[stop_times["trip_id"].astype(str) == trip_id].copy()
        same_trip_rows = same_trip_rows.sort_values("stop_sequence")

        possible_start_rows = same_trip_rows[
            (same_trip_rows["stop_id"].astype(str) == outbound.start_stop_id) &
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

      
        if best_return is None:
            best_return = return_candidate
        else:
            if return_candidate.depart_dest_time > best_return.depart_dest_time:
                best_return = return_candidate

    return best_return


def choose_best_backtrack_plan(
    outbound_candidates: List[OutboundCandidate],
    stop_times: pd.DataFrame,
    trips: pd.DataFrame,
    return_by_secs: int
) -> Optional[Dict[str, Any]]:
 

    valid_plans: List[Dict[str, Any]] = []

    for outbound in outbound_candidates:
        return_candidate = find_return_candidate(
            outbound=outbound,
            stop_times=stop_times,
            trips=trips,
            return_by_secs=return_by_secs
        )

        if return_candidate is None:
            continue

        stop_distance = outbound.dest_sequence - outbound.start_sequence
        layover = return_candidate.depart_dest_time - outbound.arrive_dest_time

        valid_plans.append({
            "outbound": outbound,
            "return": return_candidate,
            "stop_distance": stop_distance,
            "layover_secs": layover
        })

    if not valid_plans:
        return None

    valid_plans.sort(
        key=lambda p: (
            p["stop_distance"],
            p["outbound"].depart_time,
            p["return"].depart_dest_time
        ),
        reverse=True
    )

    return valid_plans[0]



def plan_backtrack_same_line(
    start_query: str,
    return_by: str,
    start_after: str,
    stops: pd.DataFrame,
    routes: pd.DataFrame,
    trips: pd.DataFrame,
    stop_times: pd.DataFrame
) -> str:


    try:
        start_after_secs = time_to_seconds(start_after)
        return_by_secs = time_to_seconds(return_by)
    except ValueError as exc:
        return f"Invalid time input: {exc}"

    if return_by_secs <= start_after_secs:
        return "Return-by time must be later than start-after time."

    # Clean stop_times first
    stop_times_prepped = prepare_stop_times(stop_times)

    # Find station
    stop_matches = find_matching_stops(stops, start_query)
    if not stop_matches:
        return f'No stop found matching "{start_query}".'

    start_stop = choose_best_stop_match(stop_matches, start_query)
    if start_stop is None:
        return f'No usable stop found matching "{start_query}".'

    # Get all possible trip starts
    start_rows = get_start_trip_rows(
        stop_times=stop_times_prepped,
        trips=trips,
        start_stop_id=start_stop.stop_id,
        start_after_secs=start_after_secs
    )

    if start_rows.empty:
        return (
            f'No trips leave from "{start_stop.stop_name}" '
            f'after {start_after}.'
        )

    # Build outbound candidates
    outbound_candidates = build_outbound_candidates(
        start_rows=start_rows,
        stop_times=stop_times_prepped,
        stops=stops,
        routes=routes
    )

    if not outbound_candidates:
        return (
            f'No downstream stops found from "{start_stop.stop_name}" '
            f'after {start_after}.'
        )

    # Pick best valid round trip
    best_plan = choose_best_backtrack_plan(
        outbound_candidates=outbound_candidates,
        stop_times=stop_times_prepped,
        trips=trips,
        return_by_secs=return_by_secs
    )

    if best_plan is None:
        return (
            f'No valid same-line backtracking trip was found from '
            f'"{start_stop.stop_name}" that returns by {return_by}.'
        )

    outbound: OutboundCandidate = best_plan["outbound"]
    ret: ReturnCandidate = best_plan["return"]



    return (
        f"Start stop: {outbound.start_stop_name}\n"
        f"Route: {outbound.route_name}\n\n"
        f"Outbound:\n"
        f"  Trip ID: {outbound.outbound_trip_id}\n"
        f"  Leave {outbound.start_stop_name} at {seconds_to_time(outbound.depart_time)}\n"
        f"  Arrive {outbound.dest_stop_name} at {seconds_to_time(outbound.arrive_dest_time)}\n\n"
        f"Return:\n"
        f"  Trip ID: {ret.return_trip_id}\n"
        f"  Leave {outbound.dest_stop_name} at {seconds_to_time(ret.depart_dest_time)}\n"
        f"  Arrive {outbound.start_stop_name} at {seconds_to_time(ret.arrive_start_time)}\n\n"
        f"Backtracking depth: {best_plan['stop_distance']} stop(s)\n"
        f"Layover at destination: {seconds_to_time(best_plan['layover_secs'])}"
    )