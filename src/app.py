import os
import shutil
from flask import Flask, render_template, request, send_file

# הייבואים שלנו
from analyzer import analyzer
from extractor import extract_all
from map_view import create_map
from report import create_report
from timeline import create_timeline

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'icons'))


@app.route('/')
def index():
    """דף הבית - טופס לבחירת קבצים ותיקיות"""
    # חשוב להעביר error_message=None כברירת מחדל
    return render_template('index.html', error_message=None)

@app.route('/image/<path:filepath>')
def serve_image(filepath):
    """
    מגיש תמונות מתיקיית uploads לציר הזמן.
    <path:filepath> מאפשר slashes בתוך הנתיב
    """
    abs_path = os.path.join(os.getcwd(), filepath)
    if os.path.exists(abs_path):
        return send_file(abs_path)
    return "Image not found", 404


@app.route('/analyze', methods=['POST'])
def analyze_images():
    # כל הקבצים (בין אם נבחרו כתמונות בודדות ובין אם מתוך תיקייה שלמה) יגיעו לכאן
    files = request.files.getlist("photos")

    # בדיקת Validation בצד השרת
    if not files or files[0].filename == '':
        return render_template('index.html', error_message="שגיאה: המערכת לא קיבלה קבצים לניתוח. אנא נסה שנית.")

    print(f"✅ קבצים התקבלו: {len(files)}")

    # הכנת תיקיית uploads
    temp_folder = "uploads"
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    os.makedirs(temp_folder)

    # שמירת כל הקבצים
    for file in files:
        if not file.filename:
            continue

        # חשוב: שומר על מבנה התיקיות הפנימי אם המשתמש העלה תיקייה שלמה
        clean_filename = file.filename.replace('\\', '/').lstrip('/')
        save_path = os.path.join(temp_folder, clean_filename)

        dir_name = os.path.dirname(save_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        file.save(save_path)

    # כעת יש לנו תיקייה מוכנה עם כל החומר. אפשר להמשיך ללוגיקה שלנו

    # שלב 1: שליפת נתונים מתיקיית ה-uploads
    images_data = extract_all(temp_folder)

    # שלב 2: יצירת מפה
    map_html = create_map(images_data)

    # שלב 3: ציר זמן
    timeline_html = create_timeline(images_data)

    # שלב 4: ניתוח
    analysis = analyzer(images_data)

    # שלב 5: הרכבת דו"ח
    report_html = create_report(images_data, map_html, timeline_html, analysis)

    return report_html


if __name__ == '__main__':
    app.run(debug=True)