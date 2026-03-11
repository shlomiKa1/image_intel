import html as html_module
from datetime import datetime


def create_report(images_data, map_html, timeline_html, analysis):
    analysis = analysis or {}
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    insights = analysis.get("insights") or []
    unique_cameras = analysis.get("unique_cameras") or []

    # תובנות
    insights_html = ""
    for insight in insights:
        insights_html += f"<li>{html_module.escape(str(insight))}</li>"

    if not insights_html:
        insights_html = "<li>לא נמצאו תובנות להצגה</li>"

    # מכשירים
    cameras_html = ""
    for cam in list(unique_cameras):
        cameras_html += f"<span class='badge'>{html_module.escape(str(cam))}</span> "

    if not cameras_html:
        cameras_html = "<p>לא נמצאו מכשירים להצגה</p>"

    # טבלת תמונות
    images_table_html = ""
    for image in (images_data or []):
        filename = html_module.escape(str(image.get("filename", "לא ידוע")))
        make = image.get("camera_make", "")
        model = image.get("camera_model", "")
        camera = f"{make} {model}".strip() or "לא ידוע"
        camera = html_module.escape(camera)
        dt = html_module.escape(str(image.get("datetime", "לא ידוע")))
        has_gps = "כן" if image.get("has_gps") else "לא"

        images_table_html += f"""
        <tr>
            <td>{filename}</td>
            <td>{camera}</td>
            <td>{dt}</td>
            <td>{has_gps}</td>
        </tr>
        """

    if not images_table_html:
        images_table_html = """
        <tr>
            <td colspan="4">לא נמצאו תמונות להצגה</td>
        </tr>
        """

    # ערכים בטוחים
    total_images = analysis.get("total_images", 0) or 0
    images_with_gps = analysis.get("images_with_gps", 0) or 0
    cameras_count = len(unique_cameras)

    map_html = map_html or "<p>לא ניתן להציג מפה</p>"
    timeline_html = timeline_html or "<p>לא ניתן להציג ציר זמן</p>"

    html = f"""
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>Image Intel Report</title>

        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: auto;
                padding: 20px;
                background: #f3f6f9;
                color: #222;
            }}

            .header {{
                background: linear-gradient(135deg, #1B4F72, #2E86AB);
                color: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
            }}

            .section {{
                background: white;
                padding: 25px;
                margin: 25px 0;
                border-radius: 10px;
                box-shadow: 0 3px 8px rgba(0, 0, 0, 0.08);
                position: relative;
                overflow: hidden;
            }}

            .stats {{
                display: flex;
                justify-content: center;
                gap: 20px;
                flex-wrap: wrap;
            }}

            .stat-card {{
                background: #E8F4FD;
                padding: 18px 28px;
                border-radius: 10px;
                text-align: center;
                min-width: 150px;
            }}

            .stat-number {{
                font-size: 2.2em;
                font-weight: bold;
                color: #1B4F72;
            }}

            .badge {{
                background: #2E86AB;
                color: white;
                padding: 6px 12px;
                border-radius: 20px;
                margin: 4px;
                display: inline-block;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }}

            th, td {{
                padding: 12px;
                border-bottom: 1px solid #ddd;
                text-align: right;
            }}

            th {{
                background: #E8F4FD;
                color: #1B4F72;
            }}

            tr:hover {{
                background: #f7f9fb;
            }}

            ul {{
                padding-right: 20px;
            }}

            .map-container,
            .timeline-container {{
                width: 100%;
                min-height: 420px;
            }}

            .footer {{
                text-align: center;
                color: #888;
                margin-top: 30px;
            }}
        </style>
    </head>

    <body>

        <div class="header">
            <h1>Image Intel Report</h1>
            <p>נוצר ב-{now}</p>
        </div>

        <div class="section">
            <h2>סיכום</h2>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{total_images}</div>
                    <div>תמונות</div>
                </div>

                <div class="stat-card">
                    <div class="stat-number">{images_with_gps}</div>
                    <div>עם GPS</div>
                </div>

                <div class="stat-card">
                    <div class="stat-number">{cameras_count}</div>
                    <div>מכשירים</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>פירוט קבצים</h2>
            <table>
                <thead>
                    <tr>
                        <th>שם קובץ</th>
                        <th>מצלמה</th>
                        <th>תאריך</th>
                        <th>GPS</th>
                    </tr>
                </thead>
                <tbody>
                    {images_table_html}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>תובנות מרכזיות</h2>
            <ul>
                {insights_html}
            </ul>
        </div>

        <div class="section">
            <h2>מפה</h2>
            <div class="map-container">
                {map_html}
            </div>
        </div>

        <div class="section">
            <h2>ציר זמן</h2>
            <div class="timeline-container">
                {timeline_html}
            </div>
        </div>

        <div class="section">
            <h2>מכשירים</h2>
            {cameras_html}
        </div>

        <div class="footer">
            Image Intel | האקתון 2025
        </div>

    </body>
    </html>
    """

    return html


# if __name__ == "__main__":
#     html_output = create_report(
#         fake_images_data,
#         fake_map_html,
#         fake_timeline_html,
#         fake_analysis
#     )
#
#     with open("test_report.html", "w", encoding="utf-8") as f:
#         f.write(html_output)
#
#     print("test_report.html נוצר בהצלחה")
