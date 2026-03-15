import os
import shutil
from flask import Flask, render_template, request, send_file
from deep_translator import GoogleTranslator



from analyzer import analyzer
from extractor import extract_all
from map_view import create_map
from report import create_report
from timeline import create_timeline
from vision import WorldVisionAnalyzer

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
vision_ai = WorldVisionAnalyzer()


@app.route('/')
def index():
    return render_template('index.html', error_message=None)


@app.route('/image/<path:filepath>')
def serve_image(filepath):
    abs_path = os.path.abspath(os.path.join(os.getcwd(), filepath))
    if os.path.exists(abs_path):
        return send_file(abs_path)
    return "Image not found", 404


@app.route('/analyze', methods=['POST'])
def analyze_images():
    files = request.files.getlist("photos")
    if not files or files[0].filename == '':
        return render_template('index.html', error_message="שגיאה: המערכת לא קיבלה קבצים לניתוח.")


    # ------------------------------------------

    temp_folder = "uploads"
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    os.makedirs(temp_folder)

    for file in files:
        if not file.filename: continue
        clean_filename = file.filename.replace('\\', '/').lstrip('/')
        save_path = os.path.join(temp_folder, clean_filename)
        dir_name = os.path.dirname(save_path)
        if dir_name: os.makedirs(dir_name, exist_ok=True)
        file.save(save_path)

    print(f"קבצים התקבלו מהמשתמש: {len(files)}")

    # --- טיפול במילות מטרה אישיות (עברית ואנגלית, שורות נפרדות) ---
    custom_keywords_raw = request.form.get("custom_keywords", "")
    if custom_keywords_raw:
        # פיצול לפי ירידת שורה, וניקוי רווחים
        keywords = [k.strip() for k in custom_keywords_raw.split('\n') if k.strip()]
        translated_keywords = []
        for kw in keywords:
            # אם יש אותיות בעברית - נתרגם לאנגלית
            if any("\u0590" <= c <= "\u05EA" for c in kw):
                try:
                    translated = GoogleTranslator(source='he', target='en').translate(kw)
                    translated_keywords.append(translated)
                except:
                    translated_keywords.append(kw)
            else:
                translated_keywords.append(kw)

        # שליחה למודל מופרד בפסיקים (כי המודל מצפה לפסיקים)
        vision_ai.add_custom_targets(",".join(translated_keywords))
    # -------------------------------------------------------------

    images_data = extract_all(temp_folder)

    print(f"🔍 מתחיל ניתוח מודיעיני ויזואלי עבור {len(images_data)} פריטים...")
    for img in images_data:
        filepath = img.get("filepath")
        if filepath:
            ai_results = vision_ai.analyze_image(os.path.abspath(filepath))
            img["ai_detections"] = ai_results.get("detections", "לא זוהו מטרות")
            img["severity_score"] = ai_results.get("severity_score", 0)
            img["category"] = ai_results.get("category", "לא ידוע")
            img["annotated_url"] = ai_results.get("annotated_url")

    images_data.sort(key=lambda x: x.get("severity_score", 0), reverse=True)

    map_html = create_map(images_data)
    timeline_html = create_timeline(images_data)
    analysis = analyzer(images_data)
    report_html = create_report(images_data, map_html, timeline_html, analysis)

    return report_html


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)