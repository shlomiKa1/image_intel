from datetime import datetime


def create_report(images_data, map_html, timeline_html, analysis):
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    # יצירת רשימת תובנות
    insights_html = ""
    for insight in analysis.get("insights", []):
        insights_html += f"<li>{insight}</li>"

    # רשימת מצלמות
    cameras_html = ""
    for cam in list(analysis.get("unique_cameras", [])):
        cameras_html += f"<span class='badge'>{cam}</span> "

    # יצירת טבלת תמונות
    images_table_html = ""
    for image in images_data:
        filename = image.get("filename", "לא ידוע")
        camera = image.get("camera", "לא ידוע")
        dt = image.get("datetime", "לא ידוע")
        has_gps = "כן" if image.get("has_gps") else "לא"

        images_table_html += f"""
        <tr>
            <td>{filename}</td>
            <td>{camera}</td>
            <td>{dt}</td>
            <td>{has_gps}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>Image Intel Report</title>

        <style>
            body {{
                font-family: Arial;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
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
            }}

            .stat-card {{
                background: #E8F4FD;
                padding: 15px 25px;
                border-radius: 8px;
                text-align: center;
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
                    <div class="stat-number">{analysis.get('total_images', 0)}</div>
                    <div>תמונות</div>
                </div>

                <div class="stat-card">
                    <div class="stat-number">{analysis.get('images_with_gps', 0)}</div>
                    <div>עם GPS</div>
                </div>

                <div class="stat-card">
                    <div class="stat-number">{len(analysis.get('unique_cameras', []))}</div>
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


        <div style="text-align:center; color:#888; margin-top:30px;">
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
