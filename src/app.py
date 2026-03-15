import os
import shutil
from flask import Flask, render_template, request, send_file
from deep_translator import GoogleTranslator
import json
from geopy.geocoders import Nominatim

from analyzer import analyzer
from extractor import extract_all
from map_view import create_map
from report import create_report
from timeline import create_timeline
from vision import WorldVisionAnalyzer

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
vision_ai = WorldVisionAnalyzer()

# מאגר זיכרון למיקומים כדי לא לעכב את השרת על אותה עיר פעמיים
geolocator = Nominatim(user_agent="image_intel_app")
geo_cache = {}


def get_city_name(lat, lon):
    if not lat or not lon:
        return "לא ידוע"

    # עיגול קל כדי לקבץ מקומות קרובים ולחסוך פניות לרשת
    coord_key = f"{round(lat, 3)},{round(lon, 3)}"
    if coord_key in geo_cache:
        return geo_cache[coord_key]

    try:
        location = geolocator.reverse(f"{lat}, {lon}", exactly_one=True, language='he', timeout=3)
        if location:
            address = location.raw.get('address', {})
            # מנסה לשלוף עיר, אם אין אז יישוב, אם אין אז מחוז
            city = address.get('city',
                               address.get('town', address.get('village', address.get('county', 'אזור לא מוגדר'))))
            geo_cache[coord_key] = city
            return city
    except Exception:
        pass

    return "מיקום לא אותר"


@app.route('/')
def index():
    # שולח ל-HTML את המטרות הקיימות במודל כדי שיוצגו בלוח הבקרה
    current_targets = vision_ai.get_current_targets()
    return render_template('index.html', error_message=None, current_targets=current_targets)


@app.route('/image/<path:filepath>')
def serve_image(filepath):
    abs_path = os.path.abspath(os.path.join(os.getcwd(), filepath))
    if os.path.exists(abs_path):
        return send_file(abs_path)
    return "Image not found", 404


@app.route('/detections/<path:filename>')
def serve_detections(filename):
    abs_path = os.path.abspath(os.path.join(os.getcwd(), 'static', 'detections', filename))
    if os.path.exists(abs_path):
        return send_file(abs_path)
    return "Image not found", 404


@app.route('/analyze', methods=['POST'])
def analyze_images():
    files = request.files.getlist("photos")
    if not files or files[0].filename == '':
        return render_template('index.html', error_message="שגיאה: לא נבחרו קבצים.")

    # --- עדכון מנוע ה-AI ותרגום חכם מעברית לאנגלית ---
    dynamic_targets_json = request.form.get("dynamic_targets", "")
    if dynamic_targets_json:
        try:
            new_targets = json.loads(dynamic_targets_json)
            # תרגום אוטומטי אם המשתמש הזין עברית בעמודת ה"אנגלית"
            for t in new_targets:
                eng_val = t.get("english", "")
                if any("\u0590" <= c <= "\u05EA" for c in eng_val):
                    try:
                        t["english"] = GoogleTranslator(source='he', target='en').translate(eng_val).lower()
                    except Exception as e:
                        print(f"Translation error: {e}")

            vision_ai.update_targets(new_targets)
        except json.JSONDecodeError:
            print("שגיאה בפענוח נתוני המטרות מהמשתמש.")
    # -----------------------------------------------

    temp_folder = "uploads"
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    os.makedirs(temp_folder)

    for file in files:
        if not file.filename: continue
        clean_filename = file.filename.replace('\\', '/').lstrip('/')
        save_path = os.path.join(temp_folder, clean_filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        file.save(save_path)

    images_data = extract_all(temp_folder)

    print(f"מתחיל ניתוח ועיבוד מודיעיני עבור {len(images_data)} פריטים...")

    for img in images_data:
        filepath = img.get("filepath")
        if filepath:
            # 1. ניתוח ויזואלי
            ai_results = vision_ai.analyze_image(os.path.abspath(filepath))
            img["ai_detections"] = ai_results.get("detections", ["לא זוהו מטרות"])
            img["severity_score"] = ai_results.get("severity_score", 0)
            img["category"] = ai_results.get("category", "לא ידוע")
            img["annotated_url"] = ai_results.get("annotated_url")

            # 2. המרת קואורדינטות לעיר/אזור (Reverse Geocoding)
            img["city_name"] = get_city_name(img.get("latitude"), img.get("longitude"))

            # 3. חילוץ תאריך נקי (רק YYYY-MM-DD) לטובת סינון הדו"ח
            raw_dt = img.get("datetime")
            if raw_dt and raw_dt != "None":
                img["clean_date"] = str(raw_dt).split(" ")[0]
            else:
                img["clean_date"] = "לא ידוע"

    # מיון לפי חומרה לקראת הדו"ח
    images_data.sort(key=lambda x: x.get("severity_score", 0), reverse=True)

    map_html = create_map(images_data)
    timeline_html = create_timeline(images_data)
    analysis = analyzer(images_data)
    report_html = create_report(images_data, map_html, timeline_html, analysis)

    return report_html


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)