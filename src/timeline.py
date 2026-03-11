from datetime import datetime

FORMAT_DATE = "%Y-%m-%d %H:%M:%S"  # תואם לפורמט שמחזיר extractor
GAP = 12  # שעות מינימום להצגת פער זמן

DAY_COLORS = [
    "#0077ff", "#e63946", "#2a9d8f", "#e9c46a",
    "#f4a261", "#8338ec", "#06d6a0", "#ff006e"
]

ICONS = {
    "apple": '<img class="device-icon" src="/icons/apple.png">',
    "iphone": '<img class="device-icon" src="/icons/apple.png">',
    "samsung": '<img class="device-icon" src="/icons/android2.png">',
    "xiaomi": '<img class="device-icon" src="/icons/android.png">',
    "huawei": '<img class="device-icon" src="/icons/android.png">',
    "canon": '<svg width="24" height="24" viewBox="0 0 24 24" fill="#555"><path d="M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8zm0-2a6 6 0 1 1 0 12A6 6 0 0 1 12 6zM2 8h2V6H2v2zm18-2v2h2V6h-2zM3 19h18v2H3v-2z"/></svg>',
    "gopro": '<svg width="24" height="24" viewBox="0 0 24 24" fill="#555"><path d="M17 10.5V7a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-3.5l4 4v-11l-4 4z"/></svg>',
    "unknown": "📷"
}


def create_timeline(images_data: list) -> str | None:
    """
    יוצר ציר זמן HTML מרשימת תמונות.

    :param images_data: רשימת מילונים מ-extractor.extract_all
    :type images_data: list
    :return: מחרוזת HTML להטמעה, או הודעה אם אין תמונות עם תאריך
    :rtype: str | None
    """
    if not images_data:
        return "<p>לא נמצאו תמונות להצגה</p>"

    dated_images = [img for img in images_data if img.get("datetime")]

    if not dated_images:
        return "<h3>לא נמצאו תמונות עם תאריך</h3>"

    try:
        dated_images.sort(
            key=lambda x: datetime.strptime(x["datetime"], FORMAT_DATE)
        )
    except ValueError:
        dated_images.sort(key=lambda x: x["datetime"])

    day_color = {}

    html = """
    <style>
        .timeline-wrapper {
            font-family: 'Inter', Arial, sans-serif;
            background: #f0f4f8;
            padding: 20px;
            border-radius: 10px;
            overflow-x: auto;
            overflow-y: hidden;
            direction: ltr;
        }

        .timeline-title {
            text-align: center;
            color: #333;
            margin-bottom: 40px;
        }

        .timeline {
            position: relative;
            max-width: 900px;
            min-width: 820px;
            margin: auto;
            padding-bottom: 20px;
        }

        .timeline::after {
            content: '';
            position: absolute;
            width: 4px;
            background: #444;
            top: 0;
            bottom: 0;
            left: 50%;
            margin-left: -2px;
        }

        .event {
            padding: 20px 28px;
            position: relative;
            width: 50%;
            box-sizing: border-box;
        }

        .left {
            left: 0;
            text-align: right;
            padding-right: 55px;
        }

        .right {
            left: 50%;
            text-align: left;
            padding-left: 55px;
        }

        .card {
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            width: 240px;
            max-width: 100%;
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
            position: relative;
            overflow-wrap: break-word;
            word-break: break-word;
        }

        .card:hover {
            transform: scale(1.04);
            box-shadow: 0 8px 24px rgba(0,0,0,0.22);
        }

        .card .extra {
            display: none;
            margin-top: 8px;
            font-size: 12px;
            color: #555;
            border-top: 1px solid #eee;
            padding-top: 6px;
        }

        .card:hover .extra {
            display: block;
        }

        .dot {
            position: absolute;
            top: 90px;
            transform: translateY(-50%);
            width: 14px;
            height: 14px;
            border-radius: 40%;
            border: 3px solid white;
            z-index: 2;
        }

        .left .dot {
            right: -10px;
        }

        .right .dot {
            left: -10px;
        }

        .time-gap {
            text-align: center;
            margin: 25px 0;
            position: relative;
            z-index: 2;
        }

        .gap-badge {
            background: #ffc107;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            display: inline-block;
        }

        .device-icon {
            width: 48px;
            height: 48px;
            transition: transform 0.2s;
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-8px); }
        }

        .gap-arrow {
            font-size: 24px;
            animation: bounce 1s infinite;
            display: block;
            margin-bottom: 4px;
        }

        .device-icon:hover {
            transform: scale(1.4);
        }

        .date {
            font-weight: bold;
            margin-bottom: 5px;
        }

        .icon {
            font-size: 22px;
            margin-bottom: 4px;
        }

        .camera {
            color: gray;
            font-size: 12px;
        }

        @media (max-width: 900px) {
            .timeline {
                min-width: 700px;
            }

            .card {
                width: 210px;
            }
        }
    </style>

    <div class="timeline-wrapper">
        <h1 class="timeline-title">📸 Photo Timeline</h1>
        <div class="timeline">
    """

    for i, img in enumerate(dated_images):
        if i > 0:
            gap = big_gap(dated_images[i - 1]["datetime"], img["datetime"])
            if gap > 0:
                html += f"""
                <div class="time-gap">
                    <span class="gap-arrow">⬇️</span>
                    <span class="gap-badge">⏱ עברו {int(gap)} שעות</span>
                    <span class="gap-arrow">⬆️</span>
                </div>
                """

        side = "left" if i % 2 == 0 else "right"

        cam_make = img.get("camera_make", "")
        cam_model = img.get("camera_model", "")
        cam_info = f"{cam_make} {cam_model}".strip() or "Unknown"

        color = get_day_color(img["datetime"], day_color)
        icon = get_device_icon(cam_make)

        lat = img.get("latitude")
        lon = img.get("longitude")
        size = img.get("file_size")

        extra_parts = []

        if lat is not None and lon is not None:
            extra_parts.append(f"📍 {lat:.4f}, {lon:.4f}")

        if size:
            extra_parts.append(f"💾 {size}")

        extra_html = "<br>".join(extra_parts) if extra_parts else "אין מידע נוסף"

        border = "border-right" if side == "left" else "border-left"

        html += f"""
        <div class="event {side}">
            <div class="dot" style="background:{color}; box-shadow: 0 0 0 2px {color};"></div>
            <div class="card" style="{border}: 7px solid {color}; background: {color}15;">
                <div class="icon">{icon}</div>
                <div class="date" style="color:{color};">{img.get('datetime')}</div>
                <div>{img.get('filename', 'Unknown')}</div>
                <div class="camera">{cam_info}</div>
                <div class="extra">{extra_html}</div>
            </div>
        </div>
        """

    html += """
        </div>
    </div>
    """

    return html


def big_gap(old_time: str, new_time: str) -> float:
    """
    בודק אם עבר פער זמן גדול בין שתי תמונות.

    :param old_time: תאריך התמונה הקודמת
    :type old_time: str
    :param new_time: תאריך התמונה הנוכחית
    :type new_time: str
    :return: מספר השעות שעברו אם >= GAP, אחרת 0
    :rtype: float
    """
    try:
        format_old = datetime.strptime(old_time, FORMAT_DATE)
        format_new = datetime.strptime(new_time, FORMAT_DATE)
        diff = format_new - format_old
        gap = diff.total_seconds() / 3600
        return gap if gap >= GAP else 0
    except ValueError as e:
        print(f"Warning: bad date format – {e}")
        return 0


def get_day_color(date_str: str, day_color: dict):
    """
    מחזיר צבע ייחודי לכל יום.

    :param date_str: מחרוזת תאריך
    :type date_str: str
    :param day_color: מילון של צבע לכל יום
    :type day_color: dict
    :return: צבע עבור אותו יום
    :rtype: str
    """
    try:
        day = date_str[:10]
        if day not in day_color:
            idx = len(day_color) % len(DAY_COLORS)
            day_color[day] = DAY_COLORS[idx]
        return day_color[day]
    except (IndexError, TypeError) as e:
        print(f"Warning: bad date format in get_day_color – {e}")
        return DAY_COLORS[0]


def get_device_icon(camera_make: str):
    """
    מחזיר אייקון לפי סוג המכשיר.

    :param camera_make: יצרן המכשיר
    :type camera_make: str
    :return: HTML של אייקון מתאים
    :rtype: str
    """
    if not camera_make:
        return ICONS["unknown"]

    make = camera_make.lower()
    for key, icon in ICONS.items():
        if key in make:
            return icon

    return ICONS["unknown"]