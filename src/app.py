import os
import shutil
import time
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
from vision_clip import ClipVisionAnalyzer
from face_analyzer import FaceIntelligenceAnalyzer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- הפתרון הדינמי ---
# המערכת בודקת בעצמה היכן ממוקמת תיקיית static במחשב הספציפי הזה
static_in_same_folder = os.path.join(BASE_DIR, "static")
static_one_level_up = os.path.abspath(os.path.join(BASE_DIR, "..", "static"))

if os.path.exists(static_in_same_folder):
    STATIC_DIR = static_in_same_folder
    print("V Static folder loaded from same directory.")
else:
    STATIC_DIR = static_one_level_up
    print("V Static folder loaded from one level up (..).")

app = Flask(
    __name__,
    static_folder=STATIC_DIR,
    static_url_path="/static"
)

# טעינת המודלים לזיכרון בעליית השרת
vision_ai_yolo = WorldVisionAnalyzer()
vision_ai_clip = ClipVisionAnalyzer()
face_ai = FaceIntelligenceAnalyzer()

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
        time.sleep(1)  # הגנה מפני חסימה (Too Many Requests) של שרתי המפות
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
    # שולח ל-HTML את המטרות של שני המודלים כדי שיוצגו בלוח הבקרה בהתאמה
    yolo_targets = vision_ai_yolo.get_current_targets() if hasattr(vision_ai_yolo, 'get_current_targets') else []
    clip_targets = vision_ai_clip.get_current_targets() if hasattr(vision_ai_clip, 'get_current_targets') else []
    return render_template('index.html', error_message=None, yolo_targets=yolo_targets, clip_targets=clip_targets)


@app.route('/image/<path:filepath>')
def serve_image(filepath):
    abs_path = os.path.abspath(os.path.join(os.getcwd(), filepath))
    if os.path.exists(abs_path):
        return send_file(abs_path)
    return "Image not found", 404


@app.route('/detections/<path:filename>')
def serve_detections(filename):
    # סנכרון נתיב החיפוש עם תיקיית ה-static האמיתית של השרת
    abs_path = os.path.abspath(os.path.join(app.static_folder, 'detections', filename))
    if os.path.exists(abs_path):
        return send_file(abs_path)
    return "Image not found", 404


@app.route('/analyze', methods=['POST'])
def analyze_images():
    start_time = time.time()  # תחילת מדידת זמן הסריקה

    # שליפת כל הקבצים וסינון אלו שאין להם שם (שדות קלט ריקים)
    raw_files = request.files.getlist("photos")
    files = [f for f in raw_files if f.filename != '']

    # עכשיו בודקים באמת אם אין קבצים בכלל
    if not files:
        return render_template('index.html', error_message="שגיאה: לא נבחרו קבצים.")

    # --- איתור בחירת המודל מהמשתמש ---
    ai_model_choice = request.form.get("ai_model", "yolo")
    if ai_model_choice == "clip":
        active_vision_ai = vision_ai_clip
        print("החוקר בחר במנוע: CLIP (סריקה הקשרית)")
    else:
        active_vision_ai = vision_ai_yolo
        print("החוקר בחר במנוע: YOLO (סריקה טקטית)")

    # --- עדכון מנוע ה-AI הנבחר ותרגום חכם מעברית לאנגלית ---
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

            # מעדכנים את המודל הפעיל
            active_vision_ai.update_targets(new_targets)
        except json.JSONDecodeError:
            print("שגיאה בפענוח נתוני המטרות מהמשתמש.")
    # -----------------------------------------------

    temp_folder = "uploads"
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    os.makedirs(temp_folder)

    # --- טיפול בקליטת מטרות פנים מהחוקר ---
    face_rec_enabled = request.form.get("face_recognition") == "true"

    if face_rec_enabled:
        target_face_files = request.files.getlist("target_faces")
        target_face_names = request.form.getlist("target_face_names")

        if target_face_files and target_face_names:
            targets_dir = os.path.join(temp_folder, "targets")
            os.makedirs(targets_dir, exist_ok=True)

            for t_file, t_name in zip(target_face_files, target_face_names):
                if t_file and t_file.filename != '':
                    t_path = os.path.join(targets_dir, t_file.filename)
                    t_file.save(t_path)
                    face_ai.add_investigator_target(t_path, t_name)
    # ---------------------------------------------------------------

    for file in files:
        if not file.filename: continue
        clean_filename = file.filename.replace('\\', '/').lstrip('/')
        save_path = os.path.join(temp_folder, clean_filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        file.save(save_path)

    images_data = extract_all(temp_folder)

    print(f"מתחיל ניתוח ועיבוד מודיעיני עבור {len(images_data)} פריטים...")

    # מילות מפתח שיפעילו את מנוע זיהוי הפנים
    human_keywords = ["אדם", "חייל", "חשוד", "קצין", "איש", "person", "soldier"]

    for img in images_data:
        filepath = img.get("filepath")
        if filepath:
            # הגדרת filename כאן פותרת את באג ה-UnboundLocalError
            filename = os.path.basename(filepath)

            # 1. ניתוח ויזואלי במודל שנבחר
            ai_results = active_vision_ai.analyze_image(os.path.abspath(filepath))
            img["ai_detections"] = ai_results.get("detections", ["לא זוהו מטרות"])
            img["severity_score"] = ai_results.get("severity_score", 0)
            img["category"] = ai_results.get("category", "לא ידוע")

            # --- פתרון תצוגת התמונה ל-CLIP ---
            annotated_url = ai_results.get("annotated_url")
            if not annotated_url:
                # התיקון: שימוש בתיקיית ה-static האמיתית של פלאסק ולא במיקום אקראי
                dest_path = os.path.join(app.static_folder, 'detections', filename)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy(os.path.abspath(filepath), dest_path)
                annotated_url = filename
            else:
                # התיקון: חיתוך הנתיב והשארת שם הקובץ בלבד
                annotated_url = str(annotated_url).replace('\\', '/').split('/')[-1]

            img["annotated_url"] = annotated_url

            # 2. זיהוי פנים - מופעל רק אם זוהה אדם והחוקר בחר באפשרות!
            if face_rec_enabled:
                detections_text = " ".join(img["ai_detections"])
                if any(kw in detections_text for kw in human_keywords):
                    print(f"זוהתה דמות אנושית בתמונה {filename}, מעביר לניתוח פנים...")
                    face_ai.process_image(os.path.abspath(filepath), filename)

            # 3. המרת קואורדינטות לעיר/אזור
            img["city_name"] = get_city_name(img.get("latitude"), img.get("longitude"))

            # 4. חילוץ תאריך נקי
            raw_dt = img.get("datetime")
            if raw_dt and raw_dt != "None":
                img["clean_date"] = str(raw_dt).split(" ")[0]
            else:
                img["clean_date"] = "לא ידוע"

    # מיון לפי חומרה לקראת הדו"ח
    images_data.sort(key=lambda x: x.get("severity_score", 0), reverse=True)

    # סיום המדידה
    end_time = time.time()
    processing_time = round(end_time - start_time, 2)
    print(f"הסריקה הושלמה תוך {processing_time} שניות.")

    # איסוף הנתונים לדו"ח
    map_html = create_map(images_data)
    # שימוש ב-list() כדי להגן על ציר הזמן מפני המיון של החומרה
    timeline_html = create_timeline(list(images_data))
    analysis = analyzer(images_data)
    if not analysis:
        analysis = {}

    analysis['processing_time'] = processing_time

    faces_data = face_ai.get_report_data() if face_rec_enabled else []
    # מנקים גם את הנתיבים של זיהוי הפנים (פותר בעיות למאק/ווינדוס)
    for face in faces_data:
        if "crop_path" in face:
            face["crop_path"] = str(face["crop_path"]).replace('\\', '/').split('/')[-1]

    analysis['faces_data'] = faces_data

    report_html = create_report(images_data, map_html, timeline_html, analysis)

    return report_html


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)