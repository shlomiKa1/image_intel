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

    # --- תובנות ---
    insights_html = ""
    for insight in insights:
        insights_html += f"<li class='insight-item'>{html_module.escape(str(insight))}</li>"
    if not insights_html:
        insights_html = "<li class='insight-item'>לא נמצאו תובנות להצגה</li>"

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
        camera = f"{make} {model}".strip() or "לא ידוע"
        camera = html_module.escape(camera)
        dt = html_module.escape(str(image.get("datetime", "לא ידוע")))
        has_gps = "כן" if image.get("has_gps") else "לא"

        images_table_html += f"""
        <tr>
            <td>{filename}</td>
            <td><span class="camera-tag">{camera}</span></td>
            <td dir="ltr" style="text-align: right;">{dt}</td>
            <td>{has_gps}</td>
        </tr>
        """

    if not images_table_html:
        images_table_html = "<tr><td colspan='4'>לא נמצאו תמונות להצגה</td></tr>"

    map_html = map_html or "<div class='placeholder-box'>לא ניתן להציג מפה</div>"
    timeline_html = timeline_html or "<div class='placeholder-box'>לא ניתן להציג ציר זמן</div>"

    html = f"""<!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Image Intel Report</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;700;900&display=swap');

            :root {{
                --sidebar-bg: #0b1121;
                --sidebar-btn: #151c2c;
                --sidebar-btn-hover: #1e293b;
                --brand-blue: #3b82f6;
                --brand-yellow: #facc15;
                --text-light: #ffffff;
                --text-dark: #0f172a;
                --text-muted: #64748b;
                --bg-light: #f8fafc;
                --font-primary: 'Heebo', sans-serif;
            }}

            html {{ scroll-behavior: smooth; }}

            body {{
                font-family: var(--font-primary);
                color: var(--text-dark);
                margin: 0;
                padding: 0;
                display: flex;
                background-color: var(--bg-light);
                overflow-x: hidden;
            }}

            .hero-bg-wrapper {{
                position: absolute;
                top: 0; left: 0;
                width: 100%; height: 100vh;
                z-index: -2; overflow: hidden;
            }}

            .earth-background {{
                width: 100%;
                height: 100%;
                background-image: url('https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?q=80&w=1920&auto=format&fit=crop');
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}

            .earth-background::after {{
                content: '';
                position: absolute;
                top: 0; left: 0; width: 100%; height: 100%;
                background-image: 
                    radial-gradient(circle at 20% 50%, rgba(59,130,246,0.15) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(99,102,241,0.1) 0%, transparent 40%),
                    radial-gradient(circle at 60% 80%, rgba(16,185,129,0.08) 0%, transparent 35%);
            }}

            .overlay {{
                position: absolute;
                top: 0; left: 0;
                width: 100%; height: 100%;
                background: linear-gradient(to bottom, rgba(2,6,23,0.4), rgba(2,6,23,0.95));
                z-index: -1;
            }}

            /* ===== SIDEBAR ===== */
            .sidebar {{
                width: 260px;
                background-color: var(--sidebar-bg);
                height: 100vh;
                position: fixed;
                right: 0; top: 0;
                padding: 40px 20px;
                box-sizing: border-box;
                display: flex;
                flex-direction: column;
                gap: 15px;
                z-index: 100;
                border-left: 1px solid rgba(255,255,255,0.05);
                box-shadow: -5px 0 20px rgba(0,0,0,0.5);
            }}

            .sidebar-logo {{
                font-size: 2.5em;
                font-weight: 900;
                color: var(--brand-blue);
                margin-bottom: 30px;
                text-align: center;
                line-height: 1.1;
                text-shadow: 0 0 10px rgba(59,130,246,0.3);
            }}

            .sidebar-logo span {{
                display: block;
                font-size: 0.4em;
                font-weight: 500;
                color: var(--text-muted);
                margin-top: 5px;
                letter-spacing: 1px;
            }}

            .sidebar a {{
                color: #e2e8f0;
                text-decoration: none;
                font-size: 1.1em;
                font-weight: 500;
                padding: 15px 20px;
                border-radius: 12px;
                background-color: var(--sidebar-btn);
                transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
                text-align: right;
                border: 1px solid transparent;
            }}

            .sidebar a:hover {{
                background-color: var(--sidebar-btn-hover);
                color: white;
                transform: translateX(-5px);
                border-color: rgba(59,130,246,0.3);
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            }}

            /* ===== MAIN CONTENT ===== */
            .main-content {{
                margin-right: 260px;
                flex-grow: 1;
                width: calc(100% - 260px);
                position: relative;
            }}

            /* ===== HERO ===== */
            .hero {{
                height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                padding: 40px;
                box-sizing: border-box;
                position: relative;
            }}

            .hero h1 {{
                font-size: 4.5em;
                font-weight: 900;
                line-height: 1.1;
                margin: 0 0 15px 0;
                color: var(--text-light);
                text-shadow: 0 4px 20px rgba(0,0,0,0.8);
                opacity: 0;
                transform: translateY(30px);
                animation: fadeInUp 1s ease-out forwards;
                animation-delay: 0.2s;
            }}

            .hero p {{
                font-size: 1.4em;
                margin: 0 0 50px 0;
                color: #cbd5e1;
                opacity: 0;
                transform: translateY(30px);
                animation: fadeInUp 1s ease-out forwards;
                animation-delay: 0.5s;
                text-shadow: 0 2px 10px rgba(0,0,0,0.8);
            }}

            .hero-stats {{
                display: flex;
                gap: 30px;
                opacity: 0;
                transform: translateY(30px);
                animation: fadeInUp 1s ease-out forwards;
                animation-delay: 0.8s;
                perspective: 1000px;
            }}

            .stat-card {{
                background: rgba(15,23,42,0.45);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border: 1px solid rgba(255,255,255,0.1);
                padding: 35px 45px;
                border-radius: 20px;
                text-align: center;
                min-width: 200px;
                transition: transform 0.1s;
                transform-style: preserve-3d;
            }}

            .stat-card .number {{
                font-size: 4em;
                font-weight: 900;
                color: var(--brand-yellow);
                margin-bottom: 5px;
                line-height: 1;
                text-shadow: 0 0 20px rgba(250,204,21,0.3);
                transform: translateZ(30px);
            }}

            .stat-card .label {{
                font-size: 1.1em;
                font-weight: 500;
                color: #e2e8f0;
                transform: translateZ(15px);
            }}

            @keyframes fadeInUp {{
                to {{ opacity: 1; transform: translateY(0); }}
            }}

            /* ===== CONTENT SECTIONS ===== */
            .content-wrapper {{
                background-color: var(--bg-light);
                position: relative;
                z-index: 10;
                border-top: 1px solid #e2e8f0;
                box-shadow: 0 -15px 40px rgba(0,0,0,0.1);
            }}

            .container {{
                padding: 60px 80px;
                max-width: 1200px;
                margin: 0 auto;
            }}

            .section {{
                background: #ffffff;
                border: 1px solid #e2e8f0;
                padding: 40px;
                margin-bottom: 50px;
                border-radius: 24px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.03);
                opacity: 0;
                transform: translateY(40px);
                transition: opacity 0.8s ease-out, transform 0.8s ease-out, box-shadow 0.3s ease;
            }}

            .section.visible {{
                opacity: 1;
                transform: translateY(0);
            }}

            .section:hover {{
                box-shadow: 0 15px 40px rgba(0,0,0,0.06);
            }}

            .section h2 {{
                font-size: 2em;
                font-weight: 900;
                margin-top: 0;
                margin-bottom: 30px;
                color: var(--text-dark);
                display: inline-block;
                border-bottom: 3px solid var(--brand-blue);
                padding-bottom: 10px;
            }}

            /* ===== TABLE ===== */
            table {{
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
            }}

            th, td {{
                padding: 18px 20px;
                text-align: right;
                border-bottom: 1px solid #f1f5f9;
            }}

            th {{
                color: var(--brand-blue);
                font-weight: 700;
                font-size: 1.1em;
                background-color: #f8fafc;
            }}

            th:first-child {{ border-top-right-radius: 12px; border-bottom-right-radius: 12px; }}
            th:last-child  {{ border-top-left-radius:  12px; border-bottom-left-radius:  12px; }}

            td {{ color: #334155; font-weight: 500; }}

            tbody tr {{ transition: all 0.2s ease; }}
            tbody tr:hover {{
                background-color: #f8fafc;
                transform: scale(1.01);
                box-shadow: 0 4px 10px rgba(0,0,0,0.02);
            }}

            .camera-tag {{
                background: #e2e8f0;
                color: #1e293b;
                padding: 6px 12px;
                border-radius: 8px;
                font-size: 0.9em;
                font-weight: 700;
            }}

            /* ===== INSIGHTS ===== */
            .insight-item {{
                font-size: 1.2em;
                margin-bottom: 15px;
                color: #334155;
                transition: transform 0.2s ease, color 0.2s ease;
                list-style-type: none;
                position: relative;
                padding-right: 25px;
            }}

            .insight-item::before {{
                content: '•';
                color: var(--brand-blue);
                font-size: 1.5em;
                position: absolute;
                right: 0; top: -5px;
            }}

            .insight-item:hover {{
                transform: translateX(-5px);
                color: var(--brand-blue);
            }}

            /* ===== PLACEHOLDER ===== */
            .placeholder-box {{
                width: 100%;
                min-height: 400px;
                background: #f1f5f9;
                border-radius: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--text-muted);
                font-weight: 500;
                font-size: 1.2em;
                border: 2px dashed #cbd5e1;
            }}
            /* ===== COLLAPSIBLE ===== */
            .collapsible-content {{
                max-height: 480px;
                overflow: hidden;
                transition: max-height 0.5s ease;
                position: relative;
            }}

            .collapsible-content {{
                max-height: 480px;
                overflow: hidden;
                transition: max-height 0.5s ease;
                position: relative;
            }}

            .collapsible-content.expanded {{
                max-height: 9999px;
            }}

            .collapsible-content:not(.expanded)::after {{
                content: '';
                position: absolute;
                bottom: 0; left: 0; right: 0;
                height: 80px;
                background: linear-gradient(to bottom, transparent, white);
                pointer-events: none;
            }}

            .toggle-btn {{
                display: block;
                margin: 18px auto 0;
                padding: 10px 32px;
                background: var(--brand-blue);
                color: white;
                border: none;
                border-radius: 30px;
                font-size: 1em;
                font-weight: 700;
                font-family: var(--font-primary);
                cursor: pointer;
                transition: background 0.2s, transform 0.2s;
            }}

            .toggle-btn:hover {{
                background: #2563eb;
                transform: scale(1.04);
            }}

            /* ===== DEVICES ===== */
            .devices-grid {{
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
                margin-top: 10px;
            }}

            .device-badge {{
                background: linear-gradient(135deg, #1e293b, #334155);
                color: #e2e8f0;
                padding: 10px 20px;
                border-radius: 30px;
                font-size: 1em;
                font-weight: 700;
                border: 1px solid rgba(59,130,246,0.3);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                transition: transform 0.2s, box-shadow 0.2s;
                cursor: default;
            }}

            .device-badge:hover {{
                transform: translateY(-3px);
                box-shadow: 0 6px 16px rgba(59,130,246,0.25);
                border-color: var(--brand-blue);
            }}
        </style>
    </head>
    <body>

        <!-- רקע כדור הארץ -->
        <div class="hero-bg-wrapper">
            <div class="earth-background"></div>
            <div class="overlay"></div>
        </div>

        <!-- תפריט ימני -->
        <div class="sidebar">
            <div class="sidebar-logo">Image Intel<span>מערכת מודיעין ויזואלי</span></div>
            <a href="#hero">מסך פתיחה</a>
            <a href="#details">פירוט נתונים</a>
            <a href="#insights">תובנות מבצעיות</a>
            <a href="#map">מפה גיאוגרפית</a>
            <a href="#timeline">ציר זמן</a>
            <a href="#devices">מכשירים</a>
        </div>

        <!-- תוכן ראשי -->
        <div class="main-content">

            <!-- מסך פתיחה עם כרטיסיות ספירה -->
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

            <!-- סקציות תוכן -->
            <div class="content-wrapper">
                <div class="container">

                    <div class="section scroll-animate" id="details">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                            <h2 style="margin:0">פירוט נתונים</h2>
                            <select id="camera-filter" onchange="filterTable(this.value)" style="
                                padding: 8px 12px; border-radius: 8px;
                                border: 1px solid #e2e8f0; font-size: 0.95em;">
                                <option value="all">כל המכשירים</option>
                                {''.join(f'<option value="{c}">{c}</option>' for c in unique_cameras)}
                            </select>
                        </div>
                        
                        <div class="collapsible-content" id="details-content">
                        <table>
                            <thead>
                                <tr>
                                    <th>שם קובץ</th>
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
                        <button class="toggle-btn" onclick="toggleSection('details-content', this)">ראה עוד ▼</button>

                    </div>

                    <div class="section scroll-animate" id="insights">
                        <h2>תובנות מבצעיות</h2>
                        <div class="collapsible-content" id="insights-content">
                            {insights_html}
                        </div>
                         <button class="toggle-btn" onclick="toggleSection('insights-content', this)">ראה עוד ▼</button>
                    </div>

                    <div class="section scroll-animate" id="map">
                        <h2>מפה גיאוגרפית</h2>
                        <div class="collapsible-content" id="map-content">
                            {map_html}
                        </div>
                        <button class="toggle-btn" onclick="toggleSection('map-content', this)">ראה עוד ▼</button>
                    </div>

                    <div class="section scroll-animate" id="timeline">
                        <h2>ציר זמן</h2>
                        <div class="collapsible-content" id="timeline-content">
                            {timeline_html}
                        </div>
                        <button class="toggle-btn" onclick="toggleSection('timeline-content', this)">ראה עוד ▼</button>
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

        <script>
            // 1. ספירת מספרים
            document.addEventListener("DOMContentLoaded", () => {{
                const counters = document.querySelectorAll('.count-up');
                const speed = 200;
                counters.forEach(counter => {{
                    const updateCount = () => {{
                        const target = +counter.getAttribute('data-target');
                        const count = +counter.innerText;
                        const inc = target / speed;
                        if (count < target) {{
                            counter.innerText = Math.ceil(count + inc);
                            setTimeout(updateCount, 15);
                        }} else {{
                            counter.innerText = target;
                        }}
                    }};
                    setTimeout(updateCount, 1800);
                }});
            }});

            // 2. אפקט 3D Tilt לכרטיסיות
            const cards = document.querySelectorAll('.stat-card');
            cards.forEach(card => {{
                card.addEventListener('mousemove', e => {{
                    const rect = card.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    const xRotation = ((y - rect.height / 2) / rect.height) * -20;
                    const yRotation = ((x - rect.width / 2) / rect.width) * 20;
                    card.style.transform = `perspective(1000px) rotateX(${{xRotation}}deg) rotateY(${{yRotation}}deg) scale3d(1.05, 1.05, 1.05)`;
                }});
                card.addEventListener('mouseleave', () => {{
                    card.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`;
                }});
            }});

            // 3. אנימציות גלילה
            const observer = new IntersectionObserver((entries, observer) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        entry.target.classList.add('visible');
                        observer.unobserve(entry.target);
                    }}
                }});
            }}, {{ root: null, rootMargin: '0px', threshold: 0.15 }});

            // 4. פתיחה/סגירה של סקציות
            function toggleSection(id, btn) {{
                const el = document.getElementById(id);
                el.classList.toggle('expanded');
                btn.textContent = el.classList.contains('expanded') ? 'סגור ▲' : 'ראה עוד ▼';
            }}

            document.querySelectorAll('.scroll-animate').forEach(section => {{
                observer.observe(section);
            }});

            // 5. הפעלת scroll zoom במפה רק אחרי "ראה עוד"
            function toggleMapScroll(btn) {{
                const iframe = document.querySelector('#map-content iframe');
                const mapDiv = document.querySelector('#map-content .folium-map');
                const isExpanded = document.getElementById('map-content').classList.contains('expanded');

                // folium מייצר div עם leaflet בתוכו
                if (mapDiv && mapDiv._leaflet_map) {{
                    if (isExpanded) {{
                        mapDiv._leaflet_map.scrollWheelZoom.enable();
                    }} else {{
                        mapDiv._leaflet_map.scrollWheelZoom.disable();
                    }}
                }}
            }}
            function filterTable(camera) {{
                const rows = document.querySelectorAll('tbody tr');
                rows.forEach(row => {{
                    // עמודה 2 היא "מקור איסוף" (המצלמה)
                    const camCell = row.cells[1].textContent.trim();
                    row.style.display = (camera === 'all' || camCell.includes(camera)) ? '' : 'none';
                }});
            }}
        </script>
    </body>
    </html>
    """

    return html