import html as html_module
from datetime import datetime


def create_report(images_data, map_html, timeline_html, analysis):
    analysis = analysis or {}
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    insights = analysis.get("insights") or []
    unique_cameras = analysis.get("unique_cameras") or []
    total_images = analysis.get("total_images", 0) or 0
    images_with_gps = analysis.get("images_with_gps", 0) or 0
    cameras_count = len(unique_cameras)

    # הפקת רשימת ערים וימים ייחודיים לטובת הסינונים הנופלים
    unique_cities = set()
    unique_dates = set()
    for img in (images_data or []):
        city = img.get("city_name", "לא ידוע")
        if city and city != "מיקום לא אותר" and city != "לא ידוע":
            unique_cities.add(city)

        date = img.get("clean_date", "לא ידוע")
        if date and date != "לא ידוע":
            unique_dates.add(date)

    unique_cities = sorted(list(unique_cities))
    unique_dates = sorted(list(unique_dates), reverse=True)

    # --- תובנות ---
    insights_html = ""
    for insight in insights:
        # ניקוי אימוג'ים אם נשארו במקרה במחרוזת
        clean_insight = str(insight).replace("⚠️", "").replace("⚡", "").replace("🕵️‍♂️", "").replace("🌙", "").replace(
            "👀", "").strip()
        insights_html += f"<li class='insight-item'>{html_module.escape(clean_insight)}</li>"
    if not insights_html:
        insights_html = "<li class='insight-item'>לא נמצאו תובנות חריגות להצגה</li>"

    # --- מכשירים ---
    cameras_badges_html = ""
    for cam in list(unique_cameras):
        cameras_badges_html += f"<span class='device-badge'>{html_module.escape(str(cam))}</span>"
    if not cameras_badges_html:
        cameras_badges_html = "<p style='color:#64748b'>לא נמצאו מכשירים</p>"

    # --- טבלת תמונות ---
    images_table_html = ""
    for image in (images_data or []):
        filename = html_module.escape(str(image.get("filename", "לא ידוע")))

        make = image.get("camera_make", "")
        model = image.get("camera_model", "")
        camera = f"{make} {model}".strip()
        if not camera or camera == "None None" or camera == "None":
            camera = "לא ידוע"
        camera = html_module.escape(camera)

        dt = str(image.get("datetime", ""))
        if not dt or dt == "None":
            dt_text = "<span style='color:#94a3b8; font-style:italic;'>לא אותר תאריך</span>"
        else:
            dt_text = html_module.escape(dt)

        clean_date = html_module.escape(str(image.get("clean_date", "לא ידוע")))
        city = html_module.escape(str(image.get("city_name", "לא ידוע")))

        lat = image.get("latitude")
        lon = image.get("longitude")

        # --- תיקון הקישור לגוגל מפות והתצוגה שביקשת ---
        if image.get("has_gps") and lat and lon:
            maps_url = f"https://www.google.com/maps?q={lat},{lon}"
            has_gps = f"<span style='color:#1d1d1f; font-weight:600;'>עיר / אזור: {city}</span><br><a href='{maps_url}' target='_blank' style='color:#0A84FF; font-weight:600; text-decoration:none;'>📍 למיקום המדוייק</a>"
            gps_plain_text = "אותר"
        else:
            has_gps = "<span style='color:#94a3b8;'>חסר מיקום</span>"
            gps_plain_text = "חסר"

        ai_detections = image.get("ai_detections", ["לא בוצע ניתוח"])
        if isinstance(ai_detections, str):
            ai_detections = [ai_detections]

        detections_html = "<div class='detections-list'>"
        for det in ai_detections:
            # ללא אימוג'ים
            detections_html += f"<div class='det-item'>{html_module.escape(str(det))}</div>"
        detections_html += "</div>"

        # עמודת הנתונים החבויים לטובת חיפוש חופשי יעיל
        hidden_search_data = f"{filename} {camera} {dt_text} {city} {' '.join(ai_detections)}"

        annotated_url = image.get("annotated_url")
        if annotated_url:
            img_src = f"/static/detections/{html_module.escape(str(annotated_url))}"
            image_col_html = f"""
            <div class="img-thumb-box" onclick="openModal('{img_src}')">
                <img src="{img_src}" alt="פענוח">
                <div class="zoom-icon">הגדל</div>
            </div>
            <div class="file-name-label">{filename}</div>
            """
        else:
            image_col_html = f"""
            <div class="img-thumb-box" style="display:flex; align-items:center; justify-content:center;">
                <span style="color:#94a3b8; font-weight:600;">אין תמונה</span>
            </div>
            <div class="file-name-label">{filename}</div>
            """

        images_table_html += f"""
        <tr>
            <td class="col-visual">{image_col_html}</td>
            <td class="col-detections">{detections_html}</td>
            <td><span class="camera-tag">{camera}</span></td>
            <td dir="ltr" style="text-align: right;">{dt_text}</td>
            <td>{has_gps}<span style="display:none;" class="search-data-hidden">{hidden_search_data} {gps_plain_text}</span><span style="display:none;" class="date-hidden">{clean_date}</span><span style="display:none;" class="city-hidden">{city}</span></td>
        </tr>
        """

    if not images_table_html:
        images_table_html = "<tr><td colspan='5' style='text-align:center;'>לא נמצאו תמונות להצגה</td></tr>"

    map_html = map_html or "<div class='placeholder-box'>אין נתוני מיקום להצגת מפה</div>"
    timeline_html = timeline_html or "<div class='placeholder-box'>אין נתוני זמן להצגת ציר הזמן</div>"

    html = f"""<!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Image Intel Report</title>
        <style>
            /* ייבוא הפונט הישן עבור הכותרות */
            @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;700;900&display=swap');

            :root {{
                --sidebar-bg: #0b1121;
                --sidebar-btn: #151c2c;
                --sidebar-btn-hover: #1e293b;
                --brand-blue: #0A84FF;
                --brand-yellow: #facc15;
                --text-light: #ffffff;
                --text-dark: #1d1d1f;
                --text-muted: #86868b;
                --bg-light: #f5f5f7;
            }}

            html {{ scroll-behavior: smooth; }}

            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                color: var(--text-dark);
                margin: 0; padding: 0; display: flex;
                background-color: var(--bg-light);
                overflow-x: hidden;
                letter-spacing: 0.01em;
            }}

            /* החלת הפונט הקודם (Heebo) רק על הכותרות הראשיות */
            h1, h2, .sidebar-logo {{ font-family: 'Heebo', sans-serif !important; }}

            .hero-bg-wrapper {{ position: absolute; top: 0; left: 0; width: 100%; height: 100vh; z-index: -2; overflow: hidden; }}
            .earth-background {{ width: 100%; height: 100%; background-image: url('https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?q=80&w=1920&auto=format&fit=crop'); background-size: cover; background-position: center; background-attachment: fixed; }}
            .earth-background::after {{ content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-image: radial-gradient(circle at 20% 50%, rgba(10,132,255,0.15) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(99,102,241,0.1) 0%, transparent 40%), radial-gradient(circle at 60% 80%, rgba(16,185,129,0.08) 0%, transparent 35%); }}
            .overlay {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to bottom, rgba(5,5,5,0.4), rgba(5,5,5,0.95)); z-index: -1; }}

            .sidebar {{ width: 260px; background-color: var(--sidebar-bg); height: 100vh; position: fixed; right: 0; top: 0; padding: 40px 20px; box-sizing: border-box; display: flex; flex-direction: column; gap: 15px; z-index: 100; border-left: 1px solid rgba(255,255,255,0.05); box-shadow: -5px 0 20px rgba(0,0,0,0.5); }}
            .sidebar-logo {{ font-size: 2.2em; font-weight: 800; color: var(--brand-blue); margin-bottom: 30px; text-align: center; line-height: 1.1; }}
            .sidebar-logo span {{ display: block; font-size: 0.4em; font-weight: 500; color: #94a3b8; margin-top: 5px; font-family: -apple-system, BlinkMacSystemFont, sans-serif !important; }}
            .sidebar a {{ color: #e2e8f0; text-decoration: none; font-size: 1.05em; font-weight: 500; padding: 15px 20px; border-radius: 12px; background-color: var(--sidebar-btn); transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); text-align: right; border: 1px solid transparent; }}
            .sidebar a:hover {{ background-color: var(--sidebar-btn-hover); color: white; transform: translateX(-5px); }}

            .main-content {{ margin-right: 260px; flex-grow: 1; width: calc(100% - 260px); position: relative; }}
            .hero {{ height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 40px; box-sizing: border-box; position: relative; }}
            .hero h1 {{ font-size: 4em; font-weight: 800; line-height: 1.1; margin: 0 0 15px 0; color: var(--text-light); opacity: 0; transform: translateY(30px); animation: fadeInUp 1s ease-out forwards; animation-delay: 0.2s; }}
            .hero p {{ font-size: 1.3em; margin: 0 0 50px 0; color: #cbd5e1; opacity: 0; transform: translateY(30px); animation: fadeInUp 1s ease-out forwards; animation-delay: 0.5s; }}

            .hero-stats {{ display: flex; gap: 30px; opacity: 0; transform: translateY(30px); animation: fadeInUp 1s ease-out forwards; animation-delay: 0.8s; }}
            .stat-card {{ background: rgba(15,23,42,0.45); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.1); padding: 30px 40px; border-radius: 20px; text-align: center; min-width: 180px; }}
            .stat-card .number {{ font-size: 3.5em; font-weight: 800; color: var(--brand-yellow); margin-bottom: 5px; line-height: 1; }}
            .stat-card .label {{ font-size: 1.05em; font-weight: 500; color: #e2e8f0; }}

            @keyframes fadeInUp {{ to {{ opacity: 1; transform: translateY(0); }} }}

            .content-wrapper {{ background-color: var(--bg-light); position: relative; z-index: 10; border-top: 1px solid #d2d2d7; box-shadow: 0 -15px 40px rgba(0,0,0,0.05); }}
            .container {{ padding: 60px 80px; max-width: 1400px; margin: 0 auto; }}
            .section {{ background: #ffffff; border: 1px solid #d2d2d7; padding: 40px; margin-bottom: 50px; border-radius: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); opacity: 0; transform: translateY(40px); transition: opacity 0.8s ease-out, transform 0.8s ease-out; }}
            .section.visible {{ opacity: 1; transform: translateY(0); }}
            .section h2 {{ font-size: 1.8em; font-weight: 800; margin-top: 0; margin-bottom: 30px; color: var(--text-dark); display: inline-block; border-bottom: 3px solid var(--brand-blue); padding-bottom: 10px; }}

            table {{ width: 100%; border-collapse: separate; border-spacing: 0; }}
            th, td {{ padding: 18px 20px; text-align: right; border-bottom: 1px solid #f1f5f9; vertical-align: top; }}
            th {{ color: var(--brand-blue); font-weight: 700; font-size: 1.05em; background-color: #f8fafc; border-bottom: 2px solid #e2e8f0; }}
            th:first-child {{ border-top-right-radius: 12px; border-bottom-right-radius: 12px; }}
            th:last-child  {{ border-top-left-radius:  12px; border-bottom-left-radius:  12px; }}
            td {{ color: #1d1d1f; font-weight: 500; font-size: 15px; }}
            tbody tr:hover {{ background-color: #f8fafc; }}

            .col-visual {{ width: 220px; }}
            .col-detections {{ width: 280px; }}

            .img-thumb-box {{ width: 100%; height: 120px; background: #f1f5f9; border: 1px solid #d2d2d7; border-radius: 12px; overflow: hidden; position: relative; cursor: pointer; transition: transform 0.2s; }}
            .img-thumb-box:hover {{ border-color: var(--brand-blue); transform: scale(1.02); }}
            .img-thumb-box img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}

            .zoom-icon {{ position: absolute; bottom: 8px; left: 8px; background: rgba(0,0,0,0.6); color: white; padding: 4px 10px; border-radius: 6px; font-size: 12px; opacity: 0; transition: opacity 0.3s; font-weight:600; pointer-events: none; }}
            .img-thumb-box:hover .zoom-icon {{ opacity: 1; }}

            .file-name-label {{ text-align: center; font-size: 13px; font-weight: 600; color: var(--text-muted); margin-top: 8px; word-break: break-all; direction: ltr; }}

            .detections-list {{ max-height: 140px; overflow-y: auto; padding-right: 5px; }}
            .detections-list::-webkit-scrollbar {{ width: 6px; }}
            .detections-list::-webkit-scrollbar-track {{ background: transparent; }}
            .detections-list::-webkit-scrollbar-thumb {{ background: #d2d2d7; border-radius: 4px; }}

            .det-item {{ border-right: 3px solid var(--brand-blue); padding: 6px 12px; margin-bottom: 8px; font-size: 14px; font-weight: 600; color: #1d1d1f; background: #f8fafc; border-radius: 6px; }}
            .camera-tag {{ display: inline-block; background: #f5f5f7; color: #1d1d1f; padding: 6px 12px; border-radius: 8px; font-size: 14px; font-weight: 600; border: 1px solid #d2d2d7; max-width: 100%; word-wrap: break-word; }}

            .insight-item {{ font-size: 17px; margin-bottom: 15px; color: #1d1d1f; font-weight: 500; list-style-type: none; position: relative; padding-right: 25px; }}
            .insight-item::before {{ content: '•'; color: var(--brand-blue); font-size: 1.5em; position: absolute; right: 0; top: -5px; }}

            .placeholder-box {{ width: 100%; min-height: 150px; background: #f8fafc; border-radius: 16px; display: flex; align-items: center; justify-content: center; color: var(--text-muted); font-weight: 600; font-size: 16px; border: 1px dashed #d2d2d7; }}

            .collapsible-content {{ max-height: 480px; overflow: hidden; transition: max-height 0.3s ease; position: relative; }}
            .collapsible-content.expanded {{ max-height: 80vh; overflow-y: auto; padding-bottom:10px; }}
            .collapsible-content:not(.expanded)::after {{ content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 80px; background: linear-gradient(to bottom, transparent, var(--bg-light)); pointer-events: none; }}

            .toggle-btn {{ display: block; margin: 20px auto 0; padding: 10px 30px; background: #f5f5f7; color: var(--brand-blue); border: 1px solid #d2d2d7; border-radius: 20px; font-size: 15px; font-weight: 600; font-family: inherit; cursor: pointer; transition: all 0.2s; }}
            .toggle-btn:hover {{ background: #e8e8ed; }}

            .devices-grid {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 10px; }}
            .device-badge {{ background: #1d1d1f; color: #f5f5f7; padding: 10px 20px; border-radius: 20px; font-size: 15px; font-weight: 600; cursor: default; border: 1px solid #38383a; }}

            /* שורת סינונים עליונה */
            .filters-bar {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 25px; background: #f8fafc; padding: 15px; border-radius: 16px; border: 1px solid #e2e8f0; }}
            .filter-input {{ padding: 8px 14px; border-radius: 10px; border: 1px solid #d2d2d7; font-size: 14px; font-weight: 500; font-family: inherit; color: var(--text-dark); background: white; outline: none; }}
            .filter-input:focus {{ border-color: var(--brand-blue); }}

            /* Modal ללא טשטוש כבד כדי למנוע איטיות בגלילה */
            .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0, 0.9); }}
            .modal-content {{ margin: auto; display: block; max-width: 90%; max-height: 85vh; border-radius: 12px; position: relative; top: 50px; }}
            .close-modal {{ position: absolute; top: 25px; left: 40px; color: #fff; font-size: 40px; font-weight: 300; cursor: pointer; transition: 0.2s; }}
            .close-modal:hover {{ opacity: 0.7; }}
        </style>
    </head>
    <body>

        <div class="hero-bg-wrapper"><div class="earth-background"></div><div class="overlay"></div></div>

        <div class="sidebar">
            <div class="sidebar-logo">Image Intel<span>מערכת מודיעין ויזואלי</span></div>
            <a href="#hero">מסך פתיחה</a>
            <a href="#details">פירוט נתונים</a>
            <a href="#insights">תובנות מבצעיות</a>
            <a href="#map">מפה גיאוגרפית</a>
            <a href="#timeline">ציר זמן</a>
            <a href="#devices">מכשירים</a>
        </div>

        <div class="main-content">

            <div class="hero" id="hero">
                <h1>מערכת ניתוח מודיעין בזמן אמת</h1>
                <p>עיבוד, הצלבה וניתוח של חומרי ויזינט (VISINT) מזירות פעולה.<br>נוצר ב-{now}</p>

                <div class="hero-stats">
                    <div class="stat-card">
                        <div class="number count-up" data-target="{cameras_count}">0</div>
                        <div class="label">חתימות דיגיטליות</div>
                    </div>
                    <div class="stat-card">
                        <div class="number count-up" data-target="{images_with_gps}">0</div>
                        <div class="label">נ"צ (GPS) אומתו</div>
                    </div>
                    <div class="stat-card">
                        <div class="number count-up" data-target="{total_images}">0</div>
                        <div class="label">פריטים נותחו</div>
                    </div>
                </div>
            </div>

            <div class="content-wrapper">
                <div class="container">

                    <div class="section scroll-animate" id="details">
                        <div class="filters-bar">
                            <h2 style="margin:0; flex-grow:1; border:none; padding:0;">פירוט נתונים וסינון</h2>

                            <input type="text" id="text-filter" class="filter-input" placeholder="חיפוש חופשי בדו&quot;ח..." onkeyup="applyFilters()" style="min-width: 150px;">

                            <select id="date-filter" class="filter-input" onchange="applyFilters()" style="cursor:pointer;">
                                <option value="all">תאריך: הכל</option>
                                {''.join(f'<option value="{d}">{d}</option>' for d in unique_dates)}
                            </select>

                            <select id="city-filter" class="filter-input" onchange="applyFilters()" style="cursor:pointer;">
                                <option value="all">מיקום: הכל</option>
                                {''.join(f'<option value="{c}">{c}</option>' for c in unique_cities)}
                            </select>

                            <select id="camera-filter" class="filter-input" onchange="applyFilters()" style="cursor:pointer;">
                                <option value="all">מכשיר: הכל</option>
                                {''.join(f'<option value="{c}">{c}</option>' for c in unique_cameras)}
                            </select>
                        </div>

                        <div class="collapsible-content" id="details-content">
                        <table id="intel-table">
                            <thead>
                                <tr>
                                    <th>תמונה ושם קובץ</th>
                                    <th>ממצאים מודיעיניים</th>
                                    <th>מקור איסוף</th>
                                    <th>תאריך קליטה</th>
                                    <th>אימות מיקום</th>
                                </tr>
                            </thead>
                            <tbody>
                                {images_table_html}
                            </tbody>
                        </table>
                        </div>
                        <button class="toggle-btn" onclick="toggleSection('details-content', this)">הצג הכל</button>

                    </div>

                    <div class="section scroll-animate" id="insights">
                        <h2>תובנות מבצעיות</h2>
                        <div class="collapsible-content" id="insights-content">
                            {insights_html}
                        </div>
                         <button class="toggle-btn" onclick="toggleSection('insights-content', this)">הצג הכל</button>
                    </div>

                    <div class="section scroll-animate" id="map">
                        <h2>מפה גיאוגרפית</h2>
                        <div class="collapsible-content" id="map-content">
                            {map_html}
                        </div>
                        <button class="toggle-btn" onclick="toggleSection('map-content', this)">הצג הכל</button>
                    </div>

                    <div class="section scroll-animate" id="timeline">
                        <h2>ציר זמן</h2>
                        <div class="collapsible-content" id="timeline-content">
                            {timeline_html}
                        </div>
                        <button class="toggle-btn" onclick="toggleSection('timeline-content', this)">הצג הכל</button>
                    </div>

                    <div class="section scroll-animate" id="devices">
                        <h2>מכשירים</h2>
                        <div class="devices-grid">
                            {cameras_badges_html}
                        </div>
                    </div>

                </div>
            </div>
        </div>

        <div id="imageModal" class="modal">
            <span class="close-modal" onclick="closeModal()">×</span>
            <img class="modal-content" id="imgModalTarget">
        </div>

        <script>
            document.addEventListener("DOMContentLoaded", () => {{
                const counters = document.querySelectorAll('.count-up');
                const speed = 200;
                counters.forEach(counter => {{
                    const updateCount = () => {{
                        const target = +counter.getAttribute('data-target');
                        const count = +counter.innerText;
                        const inc = target / speed;
                        if (count < target) {{ counter.innerText = Math.ceil(count + inc); setTimeout(updateCount, 15); }}
                        else {{ counter.innerText = target; }}
                    }};
                    setTimeout(updateCount, 1800);
                }});
            }});

            const observer = new IntersectionObserver((entries, observer) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{ entry.target.classList.add('visible'); observer.unobserve(entry.target); }}
                }});
            }}, {{ root: null, rootMargin: '0px', threshold: 0.15 }});

            document.querySelectorAll('.scroll-animate').forEach(section => observer.observe(section));

            function toggleSection(id, btn) {{
                const el = document.getElementById(id);
                el.classList.toggle('expanded');
                btn.textContent = el.classList.contains('expanded') ? 'סגור הצגה' : 'הצג הכל';
            }}

            // סינון משולב חכם: מצלמה, GPS/עיר, תאריך וטקסט חופשי
            function applyFilters() {{
                const cameraFilter = document.getElementById('camera-filter').value;
                const cityFilter = document.getElementById('city-filter').value;
                const dateFilter = document.getElementById('date-filter').value;
                const textFilter = document.getElementById('text-filter').value.toLowerCase();

                const rows = document.querySelectorAll('#intel-table tbody tr');

                rows.forEach(row => {{
                    if(row.cells.length < 5) return;

                    const camCell = row.cells[2].textContent.trim();
                    const hiddenData = row.querySelector('.search-data-hidden') ? row.querySelector('.search-data-hidden').textContent.toLowerCase() : '';
                    const cityHidden = row.querySelector('.city-hidden') ? row.querySelector('.city-hidden').textContent : '';
                    const dateHidden = row.querySelector('.date-hidden') ? row.querySelector('.date-hidden').textContent : '';

                    const matchCamera = (cameraFilter === 'all' || camCell.includes(cameraFilter));
                    const matchCity = (cityFilter === 'all' || cityHidden === cityFilter);
                    const matchDate = (dateFilter === 'all' || dateHidden === dateFilter);
                    const matchText = (textFilter === '' || hiddenData.includes(textFilter));

                    row.style.display = (matchCamera && matchCity && matchDate && matchText) ? '' : 'none';
                }});
            }}

            function openModal(imgSrc) {{
                document.getElementById('imgModalTarget').src = imgSrc;
                document.getElementById('imageModal').style.display = "block";
            }}

            function closeModal() {{
                document.getElementById('imageModal').style.display = "none";
            }}

            window.onclick = function(event) {{
                const modal = document.getElementById('imageModal');
                if (event.target == modal) {{
                    closeModal();
                }}
            }}
        </script>
    </body>
    </html>
    """

    return html