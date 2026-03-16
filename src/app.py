import os
import shutil
import time
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
STATIC_DIR = os.path.join(BASE_DIR, "static")
# ---------------------------------------------------------

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

# ---> עדכון שלב 3: ייבוא המודל החדש במקום CLIP
from vision_florence import FlorenceVisionAnalyzer
from face_analyzer import FaceIntelligenceAnalyzer

app = Flask(
    __name__,
    static_folder=STATIC_DIR,
    static_url_path="/static"
)

# טעינת המודלים לזיכרון בעליית השרת
vision_ai_yolo = WorldVisionAnalyzer()
vision_ai_florence = FlorenceVisionAnalyzer()  # ---> המודל החדש
face_ai = FaceIntelligenceAnalyzer()

# מאגר זיכרון למיקומים כדי לא לעכב את השרת על אותה עיר פעמיים
geolocator = Nominatim(user_agent="image_intel_app")
geo_cache = {}


def get_city_name(lat, lon):
    """פונקציה המנתחת את מיקום שצולם התמונה, ומחזירה את מיקום במפה (שם בעברית)"""
    if not lat or not lon:
        return "לא ידוע"

    coord_key = f"{round(lat, 3)},{round(lon, 3)}"
    if coord_key in geo_cache:
        return geo_cache[coord_key]

    try:
        time.sleep(1)
        location = geolocator.reverse(f"{lat}, {lon}", exactly_one=True, language='he', timeout=3)
        if location:
            address = location.raw.get('address', {})
            city = address.get('city',
                               address.get('town', address.get('village', address.get('county', 'אזור לא מוגדר'))))
            geo_cache[coord_key] = city
            return city
    except Exception:
        pass

    return "מיקום לא אותר"


@app.route('/')
def index():
    yolo_targets = vision_ai_yolo.get_current_targets() if hasattr(vision_ai_yolo, 'get_current_targets') else []
    # לפלורנס אין רשימת מטרות קבועה ולכן נשלח רשימה ריקה כדי לא לשבור את ה-HTML הקיים
    return render_template('index.html', error_message=None, yolo_targets=yolo_targets, clip_targets=[])


@app.route('/detections/<path:filename>')
def serve_detections(filename):
    """נשאר לטובת תאימות לאחור (סריקות ישנות). סריקות חדשות מוגשות אוטומטית מתיקיית ה-runs"""
    abs_path = os.path.abspath(os.path.join(app.static_folder, 'detections', filename))
    if os.path.exists(abs_path):
        return send_file(abs_path)
    return "Image not found", 404


@app.route('/analyze', methods=['POST'])
def analyze_images():
    start_time = time.time()

    raw_files = request.files.getlist("photos")
    files = [f for f in raw_files if f.filename != '']

    if not files:
        return render_template('index.html', error_message="שגיאה: לא נבחרו קבצים.")

    # ---> עדכון שלב 3: ניהול תיקיות ריצה (Sessions) מבוסס זמן
    run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    run_dir = os.path.join(app.static_folder, 'runs', run_id)
    det_dir = os.path.join(run_dir, 'detections')
    faces_dir = os.path.join(run_dir, 'faces')
    os.makedirs(det_dir, exist_ok=True)
    os.makedirs(faces_dir, exist_ok=True)

    # איפוס מוחלט של זיכרון הפנים והגדרת תיקיית יעד חדשה
    face_ai.identities_db.clear()
    face_ai.unknown_counter = 1
    face_ai.output_dir = faces_dir

    # --- איתור בחירת המודל מהמשתמש ---
    ai_model_choice = request.form.get("ai_model", "yolo")
    # נשלוף גם את בקשת רמת הפירוט של פלורנס (נקנפג ב-HTML בשלב הבא)
    florence_detail = request.form.get("florence_detail", "<DETAILED_CAPTION>")

    if ai_model_choice in ["florence", "clip"]:  # תמיכה זמנית בשם clip עד לעדכון ה-HTML
        active_vision_ai = vision_ai_florence
        active_vision_ai.output_dir = Path(det_dir)  # הפניית תוצרי פלורנס לתיקיית הריצה הנוכחית
        print(f"החוקר בחר במנוע: Florence-2 (VLM). רמת פירוט: {florence_detail}")
    else:
        active_vision_ai = vision_ai_yolo
        active_vision_ai.output_dir = Path(det_dir)
        print("החוקר בחר במנוע: YOLO (סריקה טקטית)")

    # --- הגדרת מטרות מתבצעת רק במודל הטקטי (YOLO) ---
    if active_vision_ai == vision_ai_yolo:
        dynamic_targets_json = request.form.get("dynamic_targets", "")
        if dynamic_targets_json:
            try:
                new_targets = json.loads(dynamic_targets_json)
                for t in new_targets:
                    eng_val = t.get("english", "")
                    if any("\u0590" <= c <= "\u05EA" for c in eng_val):
                        try:
                            t["english"] = GoogleTranslator(source='he', target='en').translate(eng_val).lower()
                        except Exception as e:
                            print(f"Translation error: {e}")
                active_vision_ai.update_targets(new_targets)
            except json.JSONDecodeError:
                print("שגיאה בפענוח נתוני המטרות מהמשתמש.")

    temp_folder = "uploads"
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    os.makedirs(temp_folder)

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

    for file in files:
        if not file.filename: continue
        clean_filename = file.filename.replace('\\', '/').lstrip('/')
        save_path = os.path.join(temp_folder, clean_filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        file.save(save_path)

    images_data = extract_all(temp_folder)
    print(f"מתחיל ניתוח ועיבוד מודיעיני עבור {len(images_data)} פריטים...")

    # הוספת מילים באנגלית כדי ללכוד את התיאורים של Florence
    human_keywords = ["אדם", "חייל", "חשוד", "קצין", "איש", "person", "soldier", "man", "woman", "people", "terrorist",
                      "boy", "girl", "officer", "guard"]

    for img in images_data:
        filepath = img.get("filepath")
        if filepath:
            filename = os.path.basename(filepath)

            # --- הרצת הניתוח במודל הנבחר ---
            if active_vision_ai == vision_ai_florence:
                ai_results = active_vision_ai.analyze_image(os.path.abspath(filepath), detail_level=florence_detail)
            else:
                ai_results = active_vision_ai.analyze_image(os.path.abspath(filepath))

            img["ai_detections"] = ai_results.get("detections", ["לא זוהו מטרות"])
            img["severity_score"] = ai_results.get("severity_score", 0)
            img["category"] = ai_results.get("category", "לא ידוע")

            annotated_url = ai_results.get("annotated_url")
            if not annotated_url:
                dest_path = os.path.join(det_dir, filename)
                shutil.copy(os.path.abspath(filepath), dest_path)
                annotated_url = filename
            else:
                annotated_url = str(annotated_url).replace('\\', '/').split('/')[-1]

            # ניתוב חכם לטובת ה-HTML הקיים (עד שנעדכן את report.py)
            img["annotated_url"] = f"../runs/{run_id}/detections/{annotated_url}"

            if face_rec_enabled:
                # 1. נבדוק את הדגל החכם ואת רשימת הקואורדינטות (BBoxes) ממנועי הראייה
                has_human = ai_results.get("has_human", False)
                human_bboxes = ai_results.get("human_bboxes", [])

                # 2. גיבוי: אם מודל אחר פועל (ולא החזיר דגל), נחפש מילות מפתח בטקסט
                if not has_human:
                    detections_text = " ".join(img["ai_detections"]).lower()
                    has_human = any(kw in detections_text for kw in human_keywords)

                # 3. נפעיל את זיהוי הפנים רק אם זוהה אדם, ונעביר את המיקומים הישירות לחיתוך!
                if has_human:
                    print(f"בודק היתכנות לפנים בתמונה {filename}...")
                    face_ai.process_image(os.path.abspath(filepath), filename, human_bboxes=human_bboxes)

            img["city_name"] = get_city_name(img.get("latitude"), img.get("longitude"))

            raw_dt = img.get("datetime")
            if raw_dt and raw_dt != "None":
                img["clean_date"] = str(raw_dt).split(" ")[0]
            else:
                img["clean_date"] = "לא ידוע"

    images_data.sort(key=lambda x: x.get("severity_score", 0), reverse=True)

    end_time = time.time()
    processing_time = round(end_time - start_time, 2)
    print(f"הסריקה הושלמה תוך {processing_time} שניות.")

    map_html = create_map(images_data)
    timeline_html = create_timeline(list(images_data))
    analysis = analyzer(images_data)
    if not analysis:
        analysis = {}

    analysis['processing_time'] = processing_time

    faces_data = face_ai.get_report_data() if face_rec_enabled else []
    for face in faces_data:
        if "crop_path" in face:
            crop_filename = str(face["crop_path"]).replace('\\', '/').split('/')[-1]
            face["crop_path"] = f"../runs/{run_id}/faces/{crop_filename}"

    analysis['faces_data'] = faces_data

    report_html = create_report(images_data, map_html, timeline_html, analysis)

    return report_html


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)