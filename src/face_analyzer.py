import os
import tempfile
os.environ["TF_USE_LEGACY_KERAS"] = "1"

import cv2
import numpy as np
from deepface import DeepFace
import time


class FaceIntelligenceAnalyzer:
    def __init__(self, base_output_dir="static/faces"):
        """
        אתחול מערכת זיהוי הפנים של Image Intel.
        """
        print("אתחול מנוע זיהוי וניתוח פנים (DeepFace)...")
        self.output_dir = base_output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        self.recognition_model = "ArcFace"
        self.detector_backend = "retinaface"

        self.identities_db = {}
        self.unknown_counter = 1

    def add_investigator_target(self, image_path, target_name):
        """
        פונקציה המאפשרת לחוקר להזין תמונת יעד ושם.
        """
        if not os.path.exists(image_path):
            print(f"שגיאה: תמונת היעד {image_path} לא נמצאה.")
            return False

        try:
            # חילוץ החתימה המתמטית של הפנים
            representation = DeepFace.represent(img_path=image_path, model_name=self.recognition_model,
                                                detector_backend=self.detector_backend, enforce_detection=True)

            if representation:
                face_embedding = representation[0]["embedding"]
                target_id = f"target_{target_name.replace(' ', '_')}"

                # העתקת תמונת היעד לתיקיית התצוגה כדי שתוצג בדו"ח
                filename = os.path.basename(image_path)
                dest_path = os.path.join(self.output_dir, filename)
                if os.path.abspath(image_path) != os.path.abspath(dest_path):
                    import shutil
                    shutil.copy(image_path, dest_path)

                self.identities_db[target_id] = {
                    "name": target_name,
                    "embedding": face_embedding,
                    "is_target": True,
                    "appearances": [],
                    "crop_path": filename  # שומרים את שם התמונה של החוקר
                }

                print(f"מטרת איסוף חדשה הוזנה בהצלחה: {target_name}")
                return True

        except Exception as e:
            print(f"שגיאה בקליטת פני יעד '{target_name}': {e}")
            return False

    # ---> הוספנו את הפרמטר human_bboxes שמקבל רשימה של קואורדינטות
    def process_image(self, image_path, source_filename, human_bboxes=None):
        """
        מקבלת תמונה מהשטח (ואופציונלית מיקומים של בני אדם ממנוע הראייה),
        גוזרת את האנשים בלבד, מאתרת פנים, ומשווה למאגר הקיים.
        """
        try:
            print(f"  → מנסה לחלץ פנים מ: {source_filename}")

            # טוענים את התמונה המקורית לזיכרון כדי לגזור ממנה
            img_bgr = cv2.imread(image_path)
            if img_bgr is None:
                return
            h_temp, w_temp = img_bgr.shape[:2]
            human_bboxes = [(0, 0, w_temp, h_temp)]
            print("  [מצב בדיקה] מתעלם ממנוע הראייה - סורק את התמונה המלאה")
            crops_to_process = []

            # יישום הרעיון שלך: אם קיבלנו קואורדינטות של בני אדם, נגזור רק אותם
            if human_bboxes and len(human_bboxes) > 0:
                print(f"  → משתמש ב-{len(human_bboxes)} מיקומי גוף (BBoxes) שהתקבלו ממנוע הראייה!")
                for (x1, y1, x2, y2) in human_bboxes:
                    # הוספת שוליים לחיתוך כדי לא "לגלח" את הראש בטעות
                    h_img, w_img = img_bgr.shape[:2]
                    y1 = max(0, int(y1) - 30)
                    y2 = min(h_img, int(y2) + 30)
                    x1 = max(0, int(x1) - 30)
                    x2 = min(w_img, int(x2) + 30)

                    crops_to_process.append(img_bgr[y1:y2, x1:x2])
            else:
                # גיבוי: אם לא הגיעו קואורדינטות מסיבה כלשהי, נסרוק את כל התמונה
                crops_to_process.append(img_bgr)

            # כעת עוברים בלולאה רק על החיתוכים המדויקים של בני האדם
            for crop in crops_to_process:
                # שימו לב: DeepFace יודע לקבל פיקסלים חתוכים (crop) במקום נתיב קובץ
                faces = DeepFace.extract_faces(img_path=crop, detector_backend=self.detector_backend, align=True,
                                               enforce_detection=False)

                # אם לא נמצאו פנים בחיתוך, נדלג
                if not faces:
                    continue

                for idx, face_obj in enumerate(faces):
                    conf = face_obj["confidence"]
                    print(f"  → פנים {idx}: confidence={conf:.2f}")
                    if conf < 0.85 or conf == 0.0:
                        continue

                    face_img = face_obj["face"]

                    face_img_bgr = cv2.cvtColor((face_img * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)

                    # 2. קידוד הפנים (בשמירה כ-PNG למניעת איבוד מידע בדחיסה)
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        cv2.imwrite(tmp.name, face_img_bgr)
                        rep = DeepFace.represent(img_path=tmp.name, model_name=self.recognition_model,
                                                 enforce_detection=False)[0]
                        current_embedding = rep["embedding"]
                    os.remove(tmp.name)  # מחיקת הקובץ הזמני

                    # 3. בדיקה מול מאגר הזהויות הקיים
                    matched_id = self._find_match_in_db(current_embedding)

                    if matched_id:
                        if source_filename not in self.identities_db[matched_id]["appearances"]:
                            self.identities_db[matched_id]["appearances"].append(source_filename)
                    else:
                        # 4. פרצוף חדש לגמרי
                        new_id = f"unknown_{self.unknown_counter}"
                        self.unknown_counter += 1

                        safe_timestamp = int(time.time() * 1000)
                        crop_filename = f"face_{new_id}_{safe_timestamp}.jpg"
                        crop_filepath = os.path.join(self.output_dir, crop_filename)
                        cv2.imwrite(crop_filepath, face_img_bgr)

                        self.identities_db[new_id] = {
                            "name": f"אלמוני {self.unknown_counter - 1}",
                            "embedding": current_embedding,
                            "is_target": False,
                            "appearances": [source_filename],
                            "crop_path": crop_filename
                        }

        except ValueError as e:
            print(f"ValueError בזיהוי פנים ({source_filename}): {e}")
        except Exception as e:
            print(f"שגיאה בסריקת פנים בתמונה {source_filename}: {e}")

    def _find_match_in_db(self, target_embedding, threshold=0.72):
        best_match_id = None
        best_distance = float("inf")

        for identity_id, data in self.identities_db.items():
            db_embedding = data["embedding"]
            distance = self._cosine_distance(target_embedding, db_embedding)

            if distance < threshold and distance < best_distance:
                best_distance = distance
                best_match_id = identity_id

        return best_match_id

    def _cosine_distance(self, a, b):
        a = np.array(a)
        b = np.array(b)
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        return 1 - (dot_product / (norm_a * norm_b))

    def get_report_data(self):
        report_list = []
        for identity_id, data in self.identities_db.items():
            if data["is_target"] and len(data["appearances"]) == 0:
                continue

            report_list.append({
                "name": data["name"],
                "appearances": data["appearances"],
                "crop_path": data["crop_path"],
                "is_target": data["is_target"]
            })
        return report_list


if __name__ == "__main__":
    analyzer = FaceIntelligenceAnalyzer()
    print("מחלקה FaceIntelligenceAnalyzer מוכנה!")