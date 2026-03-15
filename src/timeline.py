from datetime import datetime

FORMAT_DATE = "%Y-%m-%d %H:%M:%S"
GAP = 12  # שעות מינימום להצגת פער זמן

DAY_COLORS = [
    "#58a6ff", "#3fb950", "#d2a8ff", "#ffa657",
    "#ff7b72", "#79c0ff", "#56d364", "#e3b341"
]

ICON_SVG = {
    "apple": '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/></svg>',
    "iphone": '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/></svg>',
    "samsung": '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M17.523 15.3414c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993.0001.5511-.4482.9997-.9993.9997m-11.046 0c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993 0 .5511-.4482.9997-.9993.9997m11.4045-6.02l1.9973-3.4592a.416.416 0 00-.1521-.5676.416.416 0 00-.5676.1521l-2.0223 3.503C15.5902 8.2439 13.8533 7.8508 12 7.8508s-3.5902.3931-5.1367 1.0989L4.841 5.4467a.4161.4161 0 00-.5677-.1521.4157.4157 0 00-.1521.5676l1.9973 3.4592C3.4925 10.1514 1.8502 12.4508 1.8502 15.294h20.3c0-2.8433-1.6423-5.1426-4.2682-6.9726"/></svg>',
    "xiaomi": '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M17.523 15.3414c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993.0001.5511-.4482.9997-.9993.9997m-11.046 0c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993 0 .5511-.4482.9997-.9993.9997m11.4045-6.02l1.9973-3.4592a.416.416 0 00-.1521-.5676.416.416 0 00-.5676.1521l-2.0223 3.503C15.5902 8.2439 13.8533 7.8508 12 7.8508s-3.5902.3931-5.1367 1.0989L4.841 5.4467a.4161.4161 0 00-.5677-.1521.4157.4157 0 00-.1521.5676l1.9973 3.4592C3.4925 10.1514 1.8502 12.4508 1.8502 15.294h20.3c0-2.8433-1.6423-5.1426-4.2682-6.9726"/></svg>',
    "huawei": '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M17.523 15.3414c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993.0001.5511-.4482.9997-.9993.9997m-11.046 0c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993 0 .5511-.4482.9997-.9993.9997m11.4045-6.02l1.9973-3.4592a.416.416 0 00-.1521-.5676.416.416 0 00-.5676.1521l-2.0223 3.503C15.5902 8.2439 13.8533 7.8508 12 7.8508s-3.5902.3931-5.1367 1.0989L4.841 5.4467a.4161.4161 0 00-.5677-.1521.4157.4157 0 00-.1521.5676l1.9973 3.4592C3.4925 10.1514 1.8502 12.4508 1.8502 15.294h20.3c0-2.8433-1.6423-5.1426-4.2682-6.9726"/></svg>',
    "canon": '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8zm0-2a6 6 0 1 1 0 12A6 6 0 0 1 12 6zM2 8h2V6H2v2zm18-2v2h2V6h-2zM3 19h18v2H3v-2z"/></svg>',
    "gopro": '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M17 10.5V7a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-3.5l4 4v-11l-4 4z"/></svg>',
    "unknown": '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/></svg>'
}

_CSS = """
<style>
  .tl-root {
    background: #0d1117;
    font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
    padding: 32px 20px 48px;
    border-radius: 12px;
    overflow-x: auto;
    direction: ltr;
  }
  .tl-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 36px;
    padding-bottom: 16px;
    border-bottom: 1px solid #21262d;
  }
  @keyframes tl-pulse {
    0%,100% { box-shadow: 0 0 0 0 rgba(88,166,255,0.4); }
    50%      { box-shadow: 0 0 0 6px rgba(88,166,255,0); }
  }
  .tl-header-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #58a6ff;
    animation: tl-pulse 2.5s infinite;
    flex-shrink: 0;
  }
  .tl-header-title {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #58a6ff;
  }
  .tl-header-count {
    margin-left: auto;
    font-size: 10px;
    color: #8b949e;
    background: #1c2128;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 4px;
    padding: 2px 8px;
    letter-spacing: 0.06em;
  }
  .tl-track {
    position: relative;
    max-width: 860px;
    margin: 0 auto;
  }
  .tl-track::before {
    content: '';
    position: absolute;
    left: 50%;
    top: 0; bottom: 0;
    width: 1px;
    background: linear-gradient(to bottom,
      transparent,
      #21262d 40px,
      #21262d calc(100% - 40px),
      transparent);
    transform: translateX(-50%);
  }
  @keyframes tl-fadein {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .tl-row {
    display: flex;
    justify-content: center;
    position: relative;
    margin-bottom: 6px;
    animation: tl-fadein 0.35s ease both;
  }
  .tl-slot {
    width: calc(50% - 28px);
    padding: 10px 0;
  }
  .tl-slot.left  { text-align: right; padding-right: 36px; }
  .tl-slot.right { text-align: left;  padding-left: 36px; }
  .tl-slot.left .tl-card  { margin-left: auto; }
  .tl-slot.right .tl-card { margin-right: auto; }
  .tl-node {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    width: 12px; height: 12px;
    border-radius: 50%;
    border: 2px solid #0d1117;
    z-index: 3;
    flex-shrink: 0;
  }
  .tl-card {
    background: #161b22;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 12px 14px;
    max-width: 280px;
    cursor: pointer;
    transition: border-color 0.2s, transform 0.2s, background 0.2s;
    position: relative;
    overflow: hidden;
  }
  .tl-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--card-accent);
    opacity: 0.8;
  }
  .tl-card:hover {
    border-color: rgba(255,255,255,0.18);
    background: #1c2128;
    transform: translateY(-2px);
  }
  .tl-card:hover .tl-extra {
    max-height: 80px;
    opacity: 1;
    margin-top: 10px;
  }
  .tl-card-icon {
    font-size: 10px;
    letter-spacing: 0.08em;
    color: #8b949e;
    text-transform: uppercase;
    margin-bottom: 5px;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .tl-slot.left .tl-card-icon { flex-direction: row-reverse; }
  .tl-card-icon svg { width: 14px; height: 14px; opacity: 0.7; flex-shrink: 0; }
  .tl-datetime {
    font-size: 12px;
    font-weight: 600;
    color: var(--card-accent);
    margin-bottom: 3px;
    font-variant-numeric: tabular-nums;
  }
  .tl-filename {
    font-size: 11px;
    color: #e6edf3;
    word-break: break-all;
    margin-bottom: 3px;
  }
  .tl-camera {
    font-size: 10px;
    color: #484f58;
    letter-spacing: 0.04em;
  }
  .tl-extra {
    max-height: 0;
    opacity: 0;
    overflow: hidden;
    transition: max-height 0.25s ease, opacity 0.25s ease, margin-top 0.25s;
    border-top: 1px solid #21262d;
    padding-top: 8px;
    font-size: 10px;
    color: #8b949e;
    line-height: 1.8;
  }
  @keyframes tl-gap-bounce {
    0%,100% { transform: translateY(0); }
    50%      { transform: translateY(-4px); }
  }
  .tl-gap {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 18px 0;
    position: relative;
    z-index: 2;
  }
  .tl-gap-line {
    flex: 1;
    height: 1px;
    background: #21262d;
    max-width: 140px;
    border: none;
  }
  .tl-gap-badge {
    background: #1a1000;
    border: 1px solid #e3b341;
    color: #e3b341;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 4px;
    animation: tl-gap-bounce 2s ease-in-out infinite;
  }
</style>
"""


def create_timeline(images_data: list) -> str | None:
    """
    יוצר ציר זמן HTML מרשימת תמונות — עיצוב מודיעיני (dark ops).

    :param images_data: רשימת מילונים מ-extractor.extract_all
    :type images_data: list
    :return: מחרוזת HTML להטמעה, או הודעה אם אין תמונות עם תאריך
    :rtype: str | None
    """
    if not images_data:
        return "<p style='color:#8b949e;font-family:monospace'>לא נמצאו תמונות להצגה</p>"

    dated_images = [img for img in images_data if img.get("datetime")]

    if not dated_images:
        return "<h3 style='color:#8b949e;font-family:monospace'>לא נמצאו תמונות עם תאריך</h3>"

    try:
        dated_images.sort(
            key=lambda x: datetime.strptime(x["datetime"], FORMAT_DATE)
        )
    except ValueError:
        dated_images.sort(key=lambda x: x["datetime"])

    day_color: dict[str, str] = {}

    html = _CSS + '<div class="tl-root">'
    html += f"""
    <div class="tl-header">
      <div class="tl-header-dot"></div>
      <span class="tl-header-title">Photo Intel &middot; Timeline</span>
      <span class="tl-header-count">{len(dated_images)} events</span>
    </div>
    <div class="tl-track">
    """

    for i, img in enumerate(dated_images):
        # פער זמן
        if i > 0:
            gap = big_gap(dated_images[i - 1]["datetime"], img["datetime"])
            if gap > 0:
                html += f"""
                <div class="tl-gap">
                  <hr class="tl-gap-line">
                  <span class="tl-gap-badge">+ {int(gap)}h gap</span>
                  <hr class="tl-gap-line">
                </div>
                """

        side = "left" if i % 2 == 0 else "right"
        color = get_day_color(img["datetime"], day_color)
        icon_html = get_device_icon(img.get("camera_make", ""))
        cam_make = img.get("camera_make", "") or ""
        cam_model = img.get("camera_model", "") or ""
        cam_info = f"{cam_make} {cam_model}".strip() or "Unknown device"

        lat = img.get("latitude")
        lon = img.get("longitude")
        size = img.get("file_size")

        extra_parts = []
        if lat is not None and lon is not None:
            extra_parts.append(f"&#128205; {lat:.4f}, {lon:.4f}")
        if size:
            extra_parts.append(f"&#128190; {size}")

        extra_html = (
            f'<div class="tl-extra">' + "<br>".join(extra_parts) + "</div>"
            if extra_parts else ""
        )

        delay = i * 60

        card_html = f"""
        <div class="tl-card" style="--card-accent:{color}; animation-delay:{delay}ms">
          <div class="tl-card-icon">{icon_html} <span>{cam_make or 'Unknown'}</span></div>
          <div class="tl-datetime">{img.get('datetime', '—')}</div>
          <div class="tl-filename">{img.get('filename', '—')}</div>
          <div class="tl-camera">{cam_info}</div>
          {extra_html}
        </div>
        """

        if side == "left":
            left_content = card_html
            right_content = ""
        else:
            left_content = ""
            right_content = card_html

        html += f"""
        <div class="tl-row" style="animation-delay:{delay}ms">
          <div class="tl-slot left">{left_content}</div>
          <div class="tl-node" style="background:{color}; box-shadow:0 0 0 3px {color}22"></div>
          <div class="tl-slot right">{right_content}</div>
        </div>
        """

    html += "</div></div>"
    return html


def big_gap(old_time: str, new_time: str) -> float:
    """
    בודק אם עבר פער זמן גדול בין שתי תמונות.

    :param old_time: תאריך התמונה הקודמת
    :param new_time: תאריך התמונה הנוכחית
    :return: מספר השעות שעברו אם >= GAP, אחרת 0
    """
    try:
        t1 = datetime.strptime(old_time, FORMAT_DATE)
        t2 = datetime.strptime(new_time, FORMAT_DATE)
        hours = (t2 - t1).total_seconds() / 3600
        return hours if hours >= GAP else 0
    except ValueError as e:
        print(f"Warning: bad date format – {e}")
        return 0


def get_day_color(date_str: str, day_color: dict) -> str:
    """
    מחזיר צבע ייחודי לכל יום.

    :param date_str: מחרוזת תאריך
    :param day_color: מילון צבע לכל יום
    :return: צבע hex
    """
    try:
        day = date_str[:10]
        if day not in day_color:
            day_color[day] = DAY_COLORS[len(day_color) % len(DAY_COLORS)]
        return day_color[day]
    except (IndexError, TypeError) as e:
        print(f"Warning: bad date in get_day_color – {e}")
        return DAY_COLORS[0]


def get_device_icon(camera_make: str) -> str:
    """
    מחזיר SVG אייקון לפי יצרן המכשיר.

    :param camera_make: יצרן המכשיר
    :return: HTML של אייקון inline SVG
    """
    if not camera_make:
        return ICON_SVG["unknown"]

    make = camera_make.lower()
    for key, icon in ICON_SVG.items():
        if key in make:
            return icon

    return ICON_SVG["unknown"]