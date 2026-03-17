import os
import cv2
import torch
import numpy as np
from PIL import Image
from pathlib import Path
from transformers import AutoProcessor, AutoModelForCausalLM
from pillow_heif import register_heif_opener
from deep_translator import GoogleTranslator  # <--- התוספת למתרגם

import transformers.dynamic_module_utils as dynamic_utils

_original_get_imports = dynamic_utils.get_imports


def _fixed_get_imports(filename: str | os.PathLike) -> list[str]:
    imports = _original_get_imports(filename)
    if "flash_attn" in imports:
        imports.remove("flash_attn")
    return imports


dynamic_utils.get_imports = _fixed_get_imports
# רישום תמיכה בתמונות פורמט HEIC (אייפון) כדי שלא יקרסו בסריקה
register_heif_opener()


class FlorenceVisionAnalyzer:
    def __init__(self):
        """
        אתחול מנוע הראייה-שפה (VLM) מבוסס Florence-2.
        המודל מורד בפעם הראשונה ונשמר מקומית (On-Premise).
        """
        print("אתחול מנוע ראייה מתקדם (Florence-2-base)... זה עשוי לקחת רגע.")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # שימוש בגרסת הבסיס (base) שהיא מאוזנת בין מהירות לביצועים
        model_id = "microsoft/Florence-2-base"

        try:
            # מנסה לטעון מהמחסן המקומי בלי לבדוק אינטרנט
            self.processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True, local_files_only=True)
            self.model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True,
                                                              local_files_only=True).to(self.device)
            print("Florence-2 loaded from local cache (Offline Mode).")
        except Exception:
            # אם אין קבצים מקומיים, חוזרים למצב המקורי שלך ומורידים מהרשת
            print("Downloading Florence-2 for the first time...")
            self.processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True).to(self.device)


        self.model.eval()  # נעילת המודל למצב הסקה (לא אימון)

        # הגדרת תיקיית הפלט לתמונות שעליהן נצייר את הממצאים
        self.base_dir = Path(os.getcwd())
        self.output_dir = self.base_dir / "static" / "detections"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # אתחול המתרגם <--- תוספת
        self.translator = GoogleTranslator(source='en', target='iw')

        # מילון מילות מפתח לקביעת חומרה מודיעינית באופן דינמי (מתוך הטקסט החופשי)
        self.threat_keywords = {
            10: ['tank', 'fighter jet', 'missile', 'explosion', 'dead body', 'terrorist', 'rocket'],
            9: ['soldier', 'military', 'rifle', 'machine gun', 'armed', 'blood', 'convoy', 'war'],
            8: ['drone', 'uav', 'apc', 'armored vehicle', 'sniper'],
            7: ['police', 'checkpoint', 'guard', 'barbed wire', 'riot', 'fire'],
            6: ['knife', 'handgun', 'pistol', 'weapon', 'helicopter'],
            3: ['fence', 'tower', 'base', 'camp']
        }

        print(f"המערכת מוכנה. תמונות מפוענחות יישמרו ב: {self.output_dir}")

    def _calculate_severity(self, text_output, detected_labels):
        """
        פונקציה פנימית העוברת על התיאור והתוויות שחולצו,
        ומחזירה ציון חומרה וקטגוריה מובילה בהתבסס על מילות מפתח.
        """
        combined_text = (text_output + " " + " ".join(detected_labels)).lower()

        max_severity = 0
        main_category = "אזרחי / שגרתי"

        for severity, keywords in self.threat_keywords.items():
            for kw in keywords:
                if kw in combined_text:
                    if severity > max_severity:
                        max_severity = severity
                        main_category = kw.capitalize()  # הופך את המילה לקטגוריה

        return max_severity, main_category

    def analyze_image(self, image_path, detail_level="<DETAILED_CAPTION>"):
        """
        הפונקציה המרכזית: מקבלת נתיב תמונה ורמת פירוט (Caption או Detailed).
        1. מפיקה תיאור סצנה מילולי.
        2. מבצעת איתור אובייקטים (OD) ומציירת עליהם מלבנים.
        מחזירה את הפורמט הנדרש עבור לוח הבקרה (app.py).
        """
        if not os.path.exists(image_path):
            return {"detections": ["קובץ לא נמצא"], "severity_score": 0, "category": "שגיאה", "annotated_url": None,
                    "has_human": False, "human_bboxes": []}

        try:
            image = Image.open(image_path).convert("RGB")

            # ---------------------------------------------------------
            # משימה 1: הפקת תיאור סצנה מילולי (Text Generation)
            # ---------------------------------------------------------
            inputs_text = self.processor(text=detail_level, images=image, return_tensors="pt").to(self.device)
            with torch.no_grad():
                generated_ids_text = self.model.generate(
                    input_ids=inputs_text["input_ids"],
                    pixel_values=inputs_text["pixel_values"],
                    max_new_tokens=1024,
                    num_beams=3,
                    do_sample=False
                )
            gen_text = self.processor.batch_decode(generated_ids_text, skip_special_tokens=False)[0]
            parsed_text = self.processor.post_process_generation(gen_text, task=detail_level,
                                                                 image_size=(image.width, image.height))
            scene_description = parsed_text[detail_level]

            # ---------------------------------------------------------
            # משימה 2: איתור אובייקטים וציור מלבנים (<OD> - Object Detection)
            # ---------------------------------------------------------
            od_task = "<OD>"
            inputs_od = self.processor(text=od_task, images=image, return_tensors="pt").to(self.device)
            with torch.no_grad():
                generated_ids_od = self.model.generate(
                    input_ids=inputs_od["input_ids"],
                    pixel_values=inputs_od["pixel_values"],
                    max_new_tokens=1024,
                    num_beams=3,
                    do_sample=False
                )
            gen_od = self.processor.batch_decode(generated_ids_od, skip_special_tokens=False)[0]
            parsed_od = self.processor.post_process_generation(gen_od, task=od_task,
                                                               image_size=(image.width, image.height))

            od_results = parsed_od.get(od_task, {})
            bboxes = od_results.get("bboxes", [])
            labels = od_results.get("labels", [])

            # המרת התמונה ל-OpenCV (BGR) לצורך ציור
            img_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # ---> שינוי 1: רשימות מילות מפתח ומערך ריק לשמירת הקואורדינטות
            human_kws = ['person', 'man', 'woman', 'boy', 'girl', 'people', 'human', 'face', 'soldier', 'crowd']
            human_bboxes = []

            # ציור המלבנים והתוויות
            if bboxes and labels:
                for bbox, label in zip(bboxes, labels):
                    x1, y1, x2, y2 = map(int, bbox)

                    # ---> שינוי 2: אם האובייקט הוא אדם, נשמור את הקואורדינטות שלו
                    if any(kw in label.lower() for kw in human_kws):
                        human_bboxes.append((x1, y1, x2, y2))

                    # ציור מלבן אדום סביב האובייקט
                    cv2.rectangle(img_bgr, (x1, y1), (x2, y2), (0, 0, 255), 2)

                    # הוספת רקע לטקסט כדי שיהיה קריא
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.7
                    thickness = 2
                    text_size = cv2.getTextSize(label, font, font_scale, thickness)[0]
                    cv2.rectangle(img_bgr, (x1, y1 - text_size[1] - 5), (x1 + text_size[0], y1), (0, 0, 255), -1)
                    cv2.putText(img_bgr, label, (x1, y1 - 2), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

            # שמירת התמונה עם הממצאים
            stem = Path(image_path).stem
            annotated_filename = f"florence_{stem}.jpg"
            output_path = self.output_dir / annotated_filename
            cv2.imwrite(str(output_path), img_bgr)

            # ---------------------------------------------------------
            # עיבוד התוצאות הסופיות לדו"ח המודיעיני (עודכן לכלול תרגום ודגל פנים)
            # ---------------------------------------------------------
            # חישוב חומרה בהתבסס על הטקסט האנגלי והתוויות
            severity, category = self._calculate_severity(scene_description, labels)

            # בדיקה האם המודל תיאר בני אדם באנגלית
            combined_eng_text = (scene_description + " " + " ".join(labels)).lower()
            has_human = any(kw in combined_eng_text for kw in human_kws)

            # תרגום התיאורים והתוויות לעברית (עם Fallback למקור באנגלית במקרה של שגיאה)
            try:
                heb_desc = self.translator.translate(scene_description)

                heb_labels = []
                unique_labels = list(set(labels))
                if unique_labels:
                    translated_labels_str = self.translator.translate(" | ".join(unique_labels))
                    heb_labels = [l.strip() for l in translated_labels_str.split("|")]
            except:
                heb_desc = scene_description
                heb_labels = list(set(labels))

            # ארגון הרשימה להצגה בדוח עם הנתונים המתורגמים
            report_detections = [f" תיאור: {heb_desc}"]

            if heb_labels:
                report_detections.append(f" אובייקטים שאותרו: {', '.join(heb_labels)}")
            else:
                report_detections.append("🔍 לא אותרו אובייקטים מוגדרים (רק תיאור סצנה)")

            return {
                "detections": report_detections,
                "severity_score": severity,
                "category": category,
                "annotated_url": annotated_filename,
                "has_human": has_human,
                "human_bboxes": human_bboxes  # ---> שינוי 3: החזרת המיקומים לשרת
            }

        except Exception as e:
            print(f"Error in Florence-2 analysis: {e}")
            return {"detections": ["שגיאה בפענוח VLM"], "severity_score": 0, "category": "שגיאה", "annotated_url": None,
                    "has_human": False, "human_bboxes": []}


if __name__ == "__main__":
    analyzer = FlorenceVisionAnalyzer()
    print("מודל Florence-2 מוכן לשילוב באפליקציה.")