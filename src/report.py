import html as html_module
from datetime import datetime


def create_report(images_data, map_html, timeline_html, analysis):
    analysis = analysis or {}
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    # הגנה מפני None בכל הרשימות
    insights = analysis.get("insights") or []
    unique_cameras = analysis.get("unique_cameras") or []

    # יצירת רשימת תובנות
    insights_html = ""
    for insight in insights:
        insights_html += f"<li>{html_module.escape(str(insight))}</li>"

    # רשימת מצלמות
    cameras_html = ""
    for cam in list(unique_cameras):
        cameras_html += f"<span class='badge'>{html_module.escape(str(cam))}</span> "

    # יצירת טבלת תמונות
    images_table_html = ""
    for image in (images_data or []):
        filename = html_module.escape(str(image.get("filename", "לא ידוע")))
        camera = html_module.escape(str(image.get("camera", "לא ידוע")))
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

    # חישובים בטוחים
    total_images = analysis.get("total_images", 0) or 0
    images_with_gps = analysis.get("images_with_gps", 0) or 0
    cameras_count = len(unique_cameras)

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
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
                color: #222;
            }}

            .header {{
                background: #1B4F72;
                color: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
            }}

            .section {{
                background: white;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}

            .stats {{
                display: flex;
                gap: 20px;
                justify-content: center;
                flex-wrap: wrap;
            }}

            .stat-card {{
                background: #E8F4FD;
                padding: 15px 25px;
                border-radius: 8px;
                text-align: center;
                min-width: 140px;
            }}

            .stat-number {{
                font-size: 2em;
                font-weight: bold;
                color: #1B4F72;
            }}

            .badge {{
                background: #2E86AB;
                color: white;
                padding: 5px 10px;
                border-radius: 15px;
                margin: 3px;
                display: inline-block;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
                overflow: hidden;
            }}

            th, td {{
                padding: 10px;
                border-bottom: 1px solid #ddd;
                text-align: right;
            }}

            th {{
                background: #E8F4FD;
                color: #1B4F72;
            }}

            tr:hover {{
                background: #f9f9f9;
            }}

            ul {{
                padding-right: 20px;
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
            {map_html}
        </div>

        <div class="section">
            <h2>ציר זמן</h2>
            {timeline_html}
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
    
# אל תשכחו להוסיף את הנתונים האמיתיים
# if __name__ == "__main__":

#     html = create_report(
#         fake_images_data,
#         fake_map_html,
#         fake_timeline_html,
#         fake_analysis
#     )

#     with open("test_report.html", "w", encoding="utf-8") as f:
#         f.write(html)

#     print("test_report.html נוצר בהצלחה")
