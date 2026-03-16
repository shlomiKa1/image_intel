import os
import cv2
import numpy as np
from deepface import DeepFace
import time
import tempfile  # ייבוא קריטי לטיפול בקבצים זמניים ומניעת קריסות


class FaceIntelligenceAnalyzer:
    def __init__(self, base_output_dir="static/faces"):
        """
        אתחול מערכת זיהוי הפנים של Image Intel.
        """
        print("אתחול מנוע זיהוי וניתוח פנים (DeepFace)...")
        self.output_dir = base_output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        # החלפנו ל-ArcFace שהוא המודל המדויק ביותר כיום ב-DeepFace
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
                    "age": "ידוע (מטרת חוקר)",
                    "race": "ידוע (מטרת חוקר)",
                    "appearances": [],
                    "crop_path": filename  # שומרים את שם התמונה של החוקר
                }

                print(f"מטרת איסוף חדשה הוזנה בהצלחה: {target_name}")
                return True

        except Exception as e:
            print(f"שגיאה בקליטת פני יעד '{target_name}': {e}")
            return False

    def process_image(self, image_path, source_filename):
        """
        מקבלת תמונה מהשטח, מאתרת פנים, משווה למאגר הקיים,
        ואם זו פנים חדשות - מנתחת גיל/מוצא ושומרת את החיתוך.
        """
        try:
            # 1. איתור וחילוץ כל הפרצופים בתמונה
            faces = DeepFace.extract_faces(img_path=image_path, detector_backend=self.detector_backend, align=True,
                                           enforce_detection=False)

            for idx, face_obj in enumerate(faces):
                if face_obj["confidence"] < 0.85:
                    continue

                face_img = face_obj["face"]
                face_img_bgr = cv2.cvtColor((face_img * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)

                # 2. קידוד הפנים לווקטור (שימוש בקובץ זמני כדי למנוע קריסת NumPy ב-DeepFace)
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                    cv2.imwrite(tmp.name, face_img_bgr)
                    rep = \
                    DeepFace.represent(img_path=tmp.name, model_name=self.recognition_model, enforce_detection=False)[0]
                    current_embedding = rep["embedding"]
                os.remove(tmp.name)  # מחיקת הקובץ הזמני למניעת עומס

                # 3. בדיקה מול מאגר הזהויות הקיים
                matched_id = self._find_match_in_db(current_embedding)

                if matched_id:
                    if source_filename not in self.identities_db[matched_id]["appearances"]:
                        self.identities_db[matched_id]["appearances"].append(source_filename)
                else:
                    # 4. פרצוף חדש לגמרי
                    new_id = f"unknown_{self.unknown_counter}"
                    self.unknown_counter += 1

                    # מניעת קריסה בשמירת קבצים במערכות הפעלה - שם קובץ באנגלית וייחודי תמיד
                    safe_timestamp = int(time.time() * 1000)
                    crop_filename = f"face_{new_id}_{safe_timestamp}.jpg"
                    crop_filepath = os.path.join(self.output_dir, crop_filename)
                    cv2.imwrite(crop_filepath, face_img_bgr)

                    print(f"מנתח דמוגרפיה עבור אדם חדש: {new_id}...")
                    # שימוש בנתיב הקובץ השמור כדי למנוע קריסה בניתוח הדמוגרפי
                    demographics = \
                    DeepFace.analyze(img_path=crop_filepath, actions=['age', 'race'], enforce_detection=False)[0]

                    dominant_race = demographics["dominant_race"]
                    estimated_age = demographics["age"]

                    self.identities_db[new_id] = {
                        "name": f"אלמוני {self.unknown_counter - 1}",
                        "embedding": current_embedding,
                        "is_target": False,
                        "age": estimated_age,
                        "race": dominant_race,
                        "appearances": [source_filename],
                        "crop_path": crop_filename
                    }

        except ValueError:
            pass
        except Exception as e:
            print(f"שגיאה בסריקת פנים בתמונה {source_filename}: {e}")

        # עדכנו את סף הרגישות ל-0.68 (המומלץ ל-ArcFace) במקום 0.40
    def _find_match_in_db(self, target_embedding, threshold=0.68):
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
            # מונע הצגה של מטרות חוקר שלא הופיעו באף תמונה מהשטח
            if data["is_target"] and len(data["appearances"]) == 0:
                continue

            report_list.append({
                "name": data["name"],
                "age": data["age"],
                "race": data["race"],
                "appearances": data["appearances"],
                "crop_path": data["crop_path"],
                "is_target": data["is_target"]
            })
        return report_list


if __name__ == "__main__":
    analyzer = FaceIntelligenceAnalyzer()
    print("מחלקה FaceIntelligenceAnalyzer מוכנה!")