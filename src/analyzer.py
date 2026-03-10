from datetime import datetime


def sort_by_time(arr: list[dict]) -> list[dict]:
    """Sort a list of image metadata dictionaries by datetime."""
    return sorted(arr, key=lambda d: d.get("datetime") or "")


def analyzer(data_dicts: list[dict]) -> dict | None:
    """
    Analyze a list of image metadata dictionaries and return summary statistics
    and insights.

    :param data_dicts: List of dictionaries containing image metadata
    :type data_dicts: list[dict]
    :return: Summary dictionary, or None if input is not a list
    :rtype: dict | None
    """

    if not isinstance(data_dicts, list):
        return None

    res = {
        "total_images": 0,
        "images_with_gps": 0,
        "images_with_datetime": 0,
        "unique_cameras": set(),
        "date_range": {"start": None, "end": None},
        "insights": []
    }

    prev_filename = None
    prev_camera = None
    prev_time = None

    data_dicts = sort_by_time(data_dicts)

    for dic in data_dicts:
        if not isinstance(dic, dict):
            continue

        curr_filename = dic.get("filename")

        make = dic.get("camera_make") or ""
        model = dic.get("camera_model") or ""
        curr_camera = f"{make} {model}".strip()

        curr_time = dic.get("datetime")
        has_gps = dic.get("has_gps")

        res["total_images"] += 1

        if has_gps:
            res["images_with_gps"] += 1

        if curr_time:
            res["images_with_datetime"] += 1

            date_only = curr_time.split(" ")[0]

            if res["date_range"]["start"] is None:
                res["date_range"]["start"] = date_only

            res["date_range"]["end"] = date_only

        if curr_camera:
            res["unique_cameras"].add(curr_camera)

        # Insight 1: camera changed
        if prev_camera and curr_camera and prev_camera != curr_camera:
            insight = (
                f"הסוכן החליף מכשיר בתאריך {curr_time}, "
                f"מכשיר קודם: {prev_camera}, מכשיר חדש: {curr_camera}"
            )
            res["insights"].append(insight)

        # Insight 2: unusual time gap
        if prev_time is not None and curr_time is not None:
            try:
                prev_dt = datetime.strptime(prev_time, "%Y-%m-%d %H:%M:%S")
                curr_dt = datetime.strptime(curr_time, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                prev_filename = curr_filename
                prev_camera = curr_camera
                prev_time = curr_time
                continue

            gap_hours = (curr_dt - prev_dt).total_seconds() / 3600

            if gap_hours > 12:
                insight = (
                    f"נמצא פער זמן חריג של מעל 12 שעות בין התמונה "
                    f"{prev_filename if prev_filename else 'unknown'} "
                    f"לתמונה {curr_filename if curr_filename else 'unknown'}"
                )
                res["insights"].append(insight)

        prev_filename = curr_filename
        prev_camera = curr_camera
        prev_time = curr_time

    # Insight 3: multiple different cameras used
    n = len(res["unique_cameras"])
    if n > 1:
        res["insights"].append(
            f"נמצאו {n} מכשירים שונים - ייתכן שהסוכן החליף מכשירים")

    res["unique_cameras"] = sorted(res["unique_cameras"])

    return res