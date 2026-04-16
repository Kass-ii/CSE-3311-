import math
DART_LINE_ORDER = ["Green", "Orange", "Red",
                   "Blue", "Silver", "TRE", "Streetcar"]
DART_LINE_KEYWORDS = {
    "Green":     ["green line"],
    "Orange":    ["orange line"],
    "Red":       ["red line"],
    "Blue":      ["blue line"],
    "Silver":    ["silver line", "silver"],
    "TRE":       ["trinity railway", "tre"],
    "Streetcar": ["streetcar", "dallas street"],
}
DART_LINE_OFFSETS = {
    "Green":     0,
    "Orange":    1,
	"Red":       2,
    "Blue":      3,
    "Silver":    4,
    "TRE":       4,
    "Streetcar": 4,
}
OFFSET_STEP = 0.00015

def _compute_perpendicular_offset(coords, offset):
    """
    Apply perpendicular offset to a LineString.
    Uses first segment to approximate direction.
    """
    if len(coords) < 2 or offset == 0:
        return coords

    (lon1, lat1), (lon2, lat2) = coords[0], coords[1]

    dx = lon2 - lon1
    dy = lat2 - lat1
    length = math.hypot(dx, dy)

    if length == 0:
        return coords

    # unit perpendicular vector
    nx = -dy / length
    ny = dx / length

    return [[lon + nx * offset, lat + ny * offset] for lon, lat in coords]


def apply_line_style_and_offset(coords, line_name, color, bundle_index=0):
    """
    Combines:
    - line-level offset
    - bundle separation
    - perpendicular geometry offset
    """
    if not line_name or line_name not in DART_LINE_ORDER:
        return coords, color, None

    base_index = DART_LINE_ORDER.index(line_name)

    # base line separation
    base_offset = (base_index - 1.5) * OFFSET_STEP

    # bundle separation (smaller spacing)
    bundle_offset = bundle_index * (OFFSET_STEP * 0.6)

    total_offset = base_offset + bundle_offset

    coords = _compute_perpendicular_offset(coords, total_offset)

    return coords, color, base_index

def get_segment_geojson(route_id, trip_id, stop_id_a, stop_id_b):
    # Get shape_id for this trip
    trip_row = trips[trips["trip_id"] == trip_id]
    if trip_row.empty:
        return None
    shape_id = trip_row.iloc[0]["shape_id"]

    # Get stop sequences for the two stops on this trip
    trip_stop_times = stop_times[stop_times["trip_id"] == trip_id].sort_values("stop_sequence")
    stop_a_row = trip_stop_times[trip_stop_times["stop_id"] == stop_id_a]
    stop_b_row = trip_stop_times[trip_stop_times["stop_id"] == stop_id_b]

    if stop_a_row.empty or stop_b_row.empty:
        return None

    seq_a = stop_a_row.iloc[0]["stop_sequence"]
    seq_b = stop_b_row.iloc[0]["stop_sequence"]

    # Ensure a comes before b
    if seq_a > seq_b:
        seq_a, seq_b = seq_b, seq_a

    # Get shape points for this shape, sorted by sequence
    shape_pts = shapes[shapes["shape_id"] == shape_id].sort_values("shape_pt_sequence")

    # Get the shape_dist_traveled for both stops if available, otherwise approximate by sequence ratio
    if "shape_dist_traveled" in trip_stop_times.columns:
        dist_a = stop_a_row.iloc[0]["shape_dist_traveled"]
        dist_b = stop_b_row.iloc[0]["shape_dist_traveled"]
        if pd.notna(dist_a) and pd.notna(dist_b):
            segment_pts = shape_pts[
                (shape_pts["shape_dist_traveled"] >= min(dist_a, dist_b)) &
                (shape_pts["shape_dist_traveled"] <= max(dist_a, dist_b))
            ]
        else:
            segment_pts = _fallback_by_sequence(shape_pts, seq_a, seq_b, len(trip_stop_times))
    else:
        segment_pts = _fallback_by_sequence(shape_pts, seq_a, seq_b, len(trip_stop_times))

    coords = segment_pts[["shape_pt_lon", "shape_pt_lat"]].values.tolist()

    if len(coords) < 2:
        return None

    return {
        "type": "Feature",
        "properties": {
            "route_id": str(route_id),
            "trip_id": str(trip_id),
            "from_stop_id": str(stop_id_a),
            "to_stop_id": str(stop_id_b),
        },
        "geometry": {
            "type": "LineString",
            "coordinates": coords,
        }
    }


def _fallback_by_sequence(shape_pts, seq_a, seq_b, total_stops):
    """Approximate shape slice by stop sequence ratio when shape_dist_traveled is unavailable."""
    total_shape_pts = len(shape_pts)
    idx_a = int((seq_a / total_stops) * total_shape_pts)
    idx_b = int((seq_b / total_stops) * total_shape_pts)
    return shape_pts.iloc[idx_a:idx_b + 1]