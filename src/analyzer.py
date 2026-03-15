from datetime import datetime


def sort_by_time(arr: list[dict]) -> list[dict]:
    return sorted(arr, key=lambda d: d.get("datetime") or "")


def analyzer(data_dicts: list[dict]) -> dict | None:
    if not isinstance(data_dicts, list):
        return None

    res = {
        "total_images": 0, "images_with_gps": 0, "images_with_datetime": 0,
        "unique_cameras": set(), "date_range": {"start": None, "end": None}, "insights": []
    }

    high_severity_count = 0
    military_targets = []
    night_photos_count = 0

    prev_filename, prev_camera, prev_time, prev_severity = None, None, None, 0
    data_dicts = sort_by_time(data_dicts)

    for dic in data_dicts:
        if not isinstance(dic, dict): continue

        curr_filename = dic.get("filename")
        curr_camera = f"{dic.get('camera_make') or ''} {dic.get('camera_model') or ''}".strip()
        curr_time = dic.get("datetime")
        has_gps = dic.get("has_gps")

        severity_score = dic.get("severity_score", 0)
        category = dic.get("category", "לא ידוע")

        res["total_images"] += 1
        if has_gps: res["images_with_gps"] += 1

        if curr_time:
            res["images_with_datetime"] += 1
            date_only = curr_time.split(" ")[0]
            if res["date_range"]["start"] is None: res["date_range"]["start"] = date_only
            res["date_range"]["end"] = date_only

            try:
                curr_dt_check = datetime.strptime(curr_time, "%Y-%m-%d %H:%M:%S")
                if curr_dt_check.hour >= 20 or curr_dt_check.hour <= 5:
                    night_photos_count += 1
            except ValueError:
                pass

        if curr_camera: res["unique_cameras"].add(curr_camera)

        if severity_score >= 8:
            high_severity_count += 1
            military_targets.append(category)
            res["insights"].append(f"⚠️ זוהתה מטרה בעצימות גבוהה: {category} (קובץ: {curr_filename})")

        if prev_camera and curr_camera and prev_camera != curr_camera:
            res["insights"].append(
                f"הסוכן החליף מכשיר בתאריך {curr_time}, מכשיר קודם: {prev_camera}, מכשיר חדש: {curr_camera}")

        if prev_time and curr_time:
            try:
                prev_dt = datetime.strptime(prev_time, "%Y-%m-%d %H:%M:%S")
                curr_dt = datetime.strptime(curr_time, "%Y-%m-%d %H:%M:%S")
                gap_seconds = (curr_dt - prev_dt).total_seconds()

                if (gap_seconds / 3600) > 12:
                    res["insights"].append(
                        f"נמצא פער זמן חריג של מעל 12 שעות בין התמונה {prev_filename} ל-{curr_filename}")

                if 0 < gap_seconds < 180 and severity_score >= 7 and prev_severity >= 7:
                    res["insights"].append(
                        f"👀 איסוף אינטנסיבי: תיעוד רציף של מטרות בעצימות גבוהה בהפרש של פחות מ-3 דקות (בסמוך ל-{curr_time}).")
            except ValueError:
                pass

        prev_filename, prev_camera, prev_time, prev_severity = curr_filename, curr_camera, curr_time, severity_score

    # שיניתי ל-2 מטרות כדי שיהיה קל יותר לראות את התובנה קופצת בבדיקות
    if high_severity_count >= 2:
        res["insights"].append(
            f"⚡ דפוס מבצעי: זוהה ריכוז מטרות צבאיות ({high_severity_count} פריטים). סוגי מטרות: {', '.join(set(military_targets))}.")

    if res["total_images"] >= 4 and ((res["total_images"] - res["images_with_gps"]) / res["total_images"]) >= 0.75:
        res["insights"].append(
            "🕵️‍♂️ מודעות ביטחונית (OPSEC): מעל 75% מהתמונות חסרות נתוני מיקום. ייתכן שניקוי המטא-דאטה מבוצע במכוון.")

    if night_photos_count >= 2:
        res["insights"].append(
            f"🌙 פעילות חשיכה: זוהו {night_photos_count} תמונות שצולמו בשעות הלילה. עשוי להעיד על פעילות חשאית.")

    if len(res["unique_cameras"]) > 1:
        res["insights"].append(f"נמצאו {len(res['unique_cameras'])} מכשירים שונים - ייתכן שהסוכן החליף מכשירים")

    res["unique_cameras"] = sorted(list(res["unique_cameras"]))
    return res