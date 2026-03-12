import os
import shutil
from analyzer import analyzer
from extractor import extract_all
from flask import Flask, render_template, request
from map_view import create_map
from report import create_report
from timeline import create_timeline


app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'icons'))

@app.route('/')
def index():
    """דף הבית - טופס לבחירת תיקייה"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_images():
    folder_path = request.form.get('folder_path')
    files = request.files.getlist("photos")

    if folder_path and os.path.isdir(folder_path):
        print(f"✅ תיקייה נמצאה: {folder_path}")
        pass

    elif files and files[0].filename != '':
        print(f"✅ קבצים התקבלו: {len(files)}")

        temp_folder = "uploads"
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)
        os.makedirs(temp_folder)

        for file in files:
            if not file.filename:  # ← דלג על ריקים
                continue
            clean_filename = file.filename.replace('\\', '/').lstrip('/')
            save_path = os.path.join(temp_folder, clean_filename)
            dir_name = os.path.dirname(save_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            file.save(save_path)
        folder_path = temp_folder
    else:
        return "לא נבחרו תמונות", 400

    # שלב 1: שליפת נתונים
    images_data = extract_all(folder_path)

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