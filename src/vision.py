import os
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from ultralytics import YOLO
from pillow_heif import register_heif_opener


# רישום תמיכה בתמונות פורמט HEIC (אייפון)
register_heif_opener()


class WorldVisionAnalyzer:
    def __init__(self):
        print("אתחול מנוע מודיעין ויזואלי (YOLO-World)...")
        self.model = YOLO('yolov8s-world.pt')

        self.targets = {
            'tank': ('טנק', 10), 'armored personnel carrier': ('נגמ"ש', 10),
            'military truck': ('משאית צבאית', 7), 'military jeep': ("ג'יפ צבאי / האמר", 7),
            'pickup truck with a weapon': ('טנדר חמוש', 9), 'soldier with rifle': ('חייל חמוש', 9),
            'group of soldiers': ('כוח צבאי', 10), 'armed person': ('חשוד חמוש', 10),
            'person in tactical gear': ('אדם בציוד טקטי', 6), 'drone': ('רחפן', 8),
            'military helicopter': ('מסוק צבאי', 9), 'fighter jet': ('מטוס קרב', 10),
            'assault rifle': ('רובה / נשק ארוך', 9), 'handgun': ('אקדח', 8),
            'missile launcher': ('משגר טילים', 10), 'military checkpoint': ('מחסום צבאי', 6),
            'military tent': ('מאהל צבאי', 5), 'civilian car': ('רכב אזרחי', 1),
            'person': ('אדם (לא חמוש)', 1), 'backpack': ('תיק', 2)
        }

        self.classes_eng = list(self.targets.keys())
        self.model.set_classes(self.classes_eng)

        self.base_dir = Path(os.getcwd())
        self.output_dir = self.base_dir / "static" / "detections"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"המערכת מוכנה. תמונות יישמרו ב: {self.output_dir}")

    def add_custom_targets(self, custom_keywords_str):
        """מקבל מחרוזת של מילים באנגלית מופרדות בפסיק ומגדיר אותן למודל"""
        if not custom_keywords_str:
            return

        # פיצול המחרוזת לרשימה וניקוי רווחים
        custom_words = [word.strip() for word in custom_keywords_str.split(",") if word.strip()]

        for word in custom_words:
            if word not in self.targets:
                # מוסיף את המילה (ברירת מחדל: חומרה 8 כדי שיבלוט)
                self.targets[word] = (f"🔍 חיפוש אישי: {word}", 8)

        # עדכון המודל ברשימה החדשה
        self.classes_eng = list(self.targets.keys())
        self.model.set_classes(self.classes_eng)

    def get_current_targets(self):
        """מחזיר את המילון הנוכחי לטובת תצוגה במסך ההגדרות"""
        # ממיר את המבנה לפורמט שקל ל-HTML לקרוא
        return [{"english": k, "hebrew": v[0], "severity": v[1]} for k, v in self.targets.items()]

    def update_targets(self, new_targets_list):
        """
        מקבל רשימה מעודכנת מהמשתמש ודורס את הגדרות המודל.
        מצפה למבנה: [{'english': 'tank', 'hebrew': 'טנק', 'severity': 10}, ...]
        """
        if not new_targets_list:
            return

        new_targets_dict = {}
        for item in new_targets_list:
            eng = item.get("english", "").strip().lower()
            heb = item.get("hebrew", "").strip()
            sev = int(item.get("severity", 0))
            if eng and heb:
                new_targets_dict[eng] = (heb, sev)

        # עדכון המודל במילון החדש
        self.targets = new_targets_dict
        self.classes_eng = list(self.targets.keys())
        self.model.set_classes(self.classes_eng)
        print(f"המודל עודכן בהצלחה עם {len(self.classes_eng)} מטרות.")

    def analyze_image(self, image_path):
        if not os.path.exists(image_path):
            return {"detections": ["קובץ לא נמצא"], "severity_score": 0, "category": "שגיאה", "annotated_url": None}

        try:
            img = Image.open(image_path).convert("RGB")
            img_array = np.array(img)
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            img_h, img_w, _ = img_bgr.shape

            results = self.model.predict(img_bgr, conf=0.20, verbose=False)[0]

            # מילון לאיסוף הממצאים לצורך קיבוץ (Grouping)
            detections_dict = {}
            max_severity = 0
            main_category = "לא זוהו מטרות"

            for box in results.boxes:
                conf = float(box.conf[0]) * 100
                class_id = int(box.cls[0])
                eng_name = self.classes_eng[class_id]
                heb_name, severity = self.targets[eng_name]

                # שמירת כל רמות הוודאות עבור כל אובייקט כדי שנוכל לקבץ
                if heb_name not in detections_dict:
                    detections_dict[heb_name] = []
                detections_dict[heb_name].append(conf)

                if severity > max_severity:
                    max_severity = severity
                    main_category = heb_name

                # ציור המלבנים והטקסט באנגלית למניעת ג'יבריש
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(img_bgr, (x1, y1), (x2, y2), (0, 0, 255), 3)

                label_for_img = f"{eng_name} ({conf:.1f}%)"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = max(img_w, img_h) / 1200.0
                thickness = max(1, int(font_scale * 2))
                text_size = cv2.getTextSize(label_for_img, font, font_scale, thickness)[0]

                cv2.rectangle(img_bgr, (x1, y1 - text_size[1] - 10), (x1 + text_size[0], y1), (0, 0, 255), -1)
                cv2.putText(img_bgr, label_for_img, (x1, y1 - 5), font, font_scale, (255, 255, 255), thickness,
                            cv2.LINE_AA)

            stem = Path(image_path).stem
            annotated_filename = f"det_{stem}.jpg"
            output_path = self.output_dir / annotated_filename
            cv2.imwrite(str(output_path), img_bgr)

            # עיבוד התוצאות לדו"ח: קיבוץ ומיון
            # עיבוד התוצאות לדו"ח: קיבוץ ומיון
            res_items = []
            if not detections_dict:
                # תיקון הבאג: מחזיר רשימה של מחרוזות נקיות
                res_items = ["לא אותרו מטרות משמעותיות"]
                final_severity = 0
            else:
                for heb_name, confs in detections_dict.items():
                    max_conf = max(confs)
                    count = len(confs)
                    # טקסט מקצועי ומסודר
                    if count > 1:
                        item_text = f"{heb_name}: נמצאו {count} (רמת סבירות: {max_conf:.1f}%)"
                    else:
                        item_text = f"{heb_name} (רמת סבירות: {max_conf:.1f}%)"
                    res_items.append({"text": item_text, "conf": max_conf})

                # מיון הרשימה מהאחוז הגבוה לנמוך
                res_items.sort(key=lambda x: x["conf"], reverse=True)

                # חילוץ הטקסט בלבד לאחר המיון
                res_items = [item["text"] for item in res_items]
                final_severity = max_severity

            return {
                "detections": res_items,
                "severity_score": final_severity,
                "category": main_category,
                "annotated_url": annotated_filename
            }

        except Exception as e:
            print(f"Error in vision analysis: {e}")
            return {"detections": ["שגיאה בניתוח"], "severity_score": 0, "category": "שגיאה", "annotated_url": None}