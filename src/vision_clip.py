import torch
import clip
from PIL import Image
from pillow_heif import register_heif_opener
import os

# רישום תמיכה בתמונות פורמט HEIC (אייפון)
register_heif_opener()


class ClipVisionAnalyzer:
    def __init__(self):
        """
        אתחול מנוע הבינה המלאכותית (CLIP) להבנת הקשר וסיווג סצנות.
        """
        print("אתחול מנוע הקשר חזותי (CLIP)...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # טעינת מודל ViT-B/32
        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)

        # מילון המטרות המורחב - סצנות, תשתיות ואירועים
        self.targets_dict = {
            # --- כלים וכוחות צבא ---
            'an 8-wheeled military armored personnel carrier (APC)': 'נגמ"ש אופני',
            'a military heavy battle tank': 'טנק',
            'a military armored vehicle on tracks': 'נגמ"ש זחלי',
            'a military logistics truck': 'משאית צבאית',
            'a tactical military jeep or humvee': "ג'יפ צבאי / האמר",
            'a pickup truck with a weapon mounted': 'טנדר חמוש (טויוטה)',
            'a soldier in military uniform with a rifle': 'חייל חמוש',
            'a group of soldiers': 'כוח צבאי / התקהלות חיילים',
            'an armed person in civilian clothes': 'חשוד חמוש (אזרחי)',
            'a person wearing a tactical vest and helmet': 'אדם בציוד טקטי',

            # --- אוויר וים ---
            'a military drone or quadcopter in the sky': 'רחפן',
            'a large military UAV or drone': 'כטב"ם',
            'a military attack helicopter': 'מסוק קרב',
            'a fighter jet airplane': 'מטוס קרב',
            'a large commercial seaport with cargo containers': 'נמל ימי / מכולות',
            'a military warship or submarine': 'ספינת מלחמה / צוללת',
            'an airport runway with planes': 'שדה תעופה / מסלול המראה',

            # --- אמל"ח ומתקנים ---
            'an assault rifle or machine gun': 'נשק ארוך / רובה',
            'a handgun or pistol': 'אקדח',
            'a missile or rocket launcher': 'משגר טילים / רקטות',
            'military communication equipment or radar': 'ציוד קשר / מכ"ם',
            'a military checkpoint or roadblock': 'מחסום צבאי',
            'a military tent or encampment': 'מאהל / בסיס ארעי',
            'a watchtower or observation post': 'עמדת תצפית / פילבוקס',
            'a border fence with barbed wire': 'גדר מערכת / תיל',

            # --- תשתיות אסטרטגיות ---
            'a nuclear or coal power plant': 'תחנת כוח',
            'a large suspension or concrete bridge': 'גשר אסטרטגי',
            'an oil refinery or industrial chemical plant': 'בית זיקוק / מתקן תעשייתי',
            'a satellite dish or large communication tower': 'אנטנת תקשורת / לוויין',
            'a water dam or large reservoir': 'סכר / מאגר מים',

            # --- אירועים ותרחישים (Context) ---
            'a violent riot or angry protest with fire': 'הפרת סדר / הפגנה אלימה',
            'a large explosion or smoke plume in a city': 'פיצוץ / עשן חריג',
            'a military convoy moving on a dirt road': 'שיירה צבאית במרחב',
            'a building destroyed by an airstrike or artillery': 'מבנה מופצץ / הריסות',
            'a dense urban warfare environment': 'לש"ב (לוחמה בשטח בנוי)',

            # --- אזרחי / מוגן ---
            'a public hospital or medical facility': 'בית חולים / מתקן רפואי',
            'a school or university building': 'בית ספר / מוסד חינוכי',
            'a dense urban residential neighborhood': 'אזור מגורים צפוף',
            'a regular civilian car or SUV': 'רכב אזרחי',
            'a typical civilian building': 'מבנה אזרחי',
            'an empty landscape with no military targets': 'שטח פתוח (ללא מטרות)',
            'a photo of a person with no weapons': 'אדם (לא חמוש)'
        }

        # מילון חומרה מודיעינית (0-10)
        self.severity_map = {
            'טנק': 10, 'משגר טילים / רקטות': 10, 'פיצוץ / עשן חריג': 10, 'מטוס קרב': 10, 'מסוק קרב': 10,
            'שיירה צבאית במרחב': 9, 'כוח צבאי / התקהלות חיילים': 9, 'חשוד חמוש (אזרחי)': 9, 'הפרת סדר / הפגנה אלימה': 9,
            'נגמ"ש אופני': 8, 'נגמ"ש זחלי': 8, 'טנדר חמוש (טויוטה)': 8, 'חייל חמוש': 8, 'כטב"ם': 8,
            'לש"ב (לוחמה בשטח בנוי)': 8,
            'רחפן': 7, 'נשק ארוך / רובה': 7, 'משאית צבאית': 7, "ג'יפ צבאי / האמר": 7, 'מבנה מופצץ / הריסות': 7,
            'תחנת כוח': 6, 'נמל ימי / מכולות': 6, 'שדה תעופה / מסלול המראה': 6, 'ספינת מלחמה / צוללת': 6,
            'אדם בציוד טקטי': 5, 'מחסום צבאי': 5, 'עמדת תצפית / פילבוקס': 5, 'בית זיקוק / מתקן תעשייתי': 5,
            'מאהל / בסיס ארעי': 4, 'ציוד קשר / מכ"ם': 4, 'גדר מערכת / תיל': 4, 'גשר אסטרטגי': 4,
            'אנטנת תקשורת / לוויין': 4,
            'אקדח': 4, 'סכר / מאגר מים': 4,
            'בית חולים / מתקן רפואי': 2, 'בית ספר / מוסד חינוכי': 2,
            'אזור מגורים צפוף': 1, 'רכב אזרחי': 1, 'מבנה אזרחי': 1, 'אדם (לא חמוש)': 1, 'שטח פתוח (ללא מטרות)': 0
        }

        # קידוד ראשוני של הטקסטים
        self._encode_text_features()
        print("מנוע ה-CLIP מוכן לפעולה.")

    def _encode_text_features(self):
        """פונקציית עזר לקידוד המילון לווקטורים מתמטיים. רצה באתחול ובכל עדכון."""
        self.phrases = list(self.targets_dict.keys())
        with torch.no_grad():
            text_tokens = clip.tokenize(self.phrases).to(self.device)
            self.text_features = self.model.encode_text(text_tokens)
            self.text_features /= self.text_features.norm(dim=-1, keepdim=True)

    def get_current_targets(self):
        """מחזיר את המילון הנוכחי לטובת תצוגה במסך ההגדרות (כמו ב-YOLO)"""
        return [{"english": k, "hebrew": v, "severity": self.severity_map.get(v, 0)} for k, v in
                self.targets_dict.items()]

    def update_targets(self, new_targets_list):
        """
        מקבל רשימה מעודכנת מהמשתמש ודורס את הגדרות המודל.
        מצפה למבנה: [{'english': '...', 'hebrew': '...', 'severity': 10}, ...]
        """
        if not new_targets_list:
            return

        new_targets_dict = {}
        new_severity_map = {}

        for item in new_targets_list:
            eng = item.get("english", "").strip().lower()
            heb = item.get("hebrew", "").strip()
            sev = int(item.get("severity", 0))
            if eng and heb:
                new_targets_dict[eng] = heb
                new_severity_map[heb] = sev

        # עדכון המילונים וקידוד מחדש של המודל כדי שיכיר את המילים החדשות
        self.targets_dict = new_targets_dict
        self.severity_map = new_severity_map
        self._encode_text_features()
        print(f"מודל CLIP עודכן בהצלחה עם {len(self.targets_dict)} מטרות סצנה/הקשר.")

    def analyze_image(self, image_path):
        """
        מנתח תמונה ומחזיר מילון עם זיהוי, ציון חומרה וקטגוריה.
        """
        if not os.path.exists(image_path):
            return {"detections": ["קובץ לא נמצא"], "severity_score": 0, "category": "שגיאה", "annotated_url": None}

        try:
            image = Image.open(image_path).convert("RGB")
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                image_features /= image_features.norm(dim=-1, keepdim=True)

                similarity = (100.0 * image_features @ self.text_features.T).softmax(dim=-1)

                # לוקחים את 2 התוצאות הגבוהות ביותר
                values, indices = similarity[0].topk(2)

                res_items = []
                max_severity = 0
                main_category = "לא זוהו מטרות"

                for val, idx in zip(values, indices):
                    conf = val.item() * 100
                    best_phrase = self.phrases[idx]
                    hebrew_result = self.targets_dict[best_phrase]

                    if conf >= 12.0:  # רף ביטחון מינימלי
                        res_items.append(f"{hebrew_result} (הקשר: {conf:.1f}%)")

                        base_severity = self.severity_map.get(hebrew_result, 0)
                        final_severity = base_severity

                        if final_severity > max_severity:
                            max_severity = final_severity
                            main_category = hebrew_result

                # סינון רעשים ושטח פתוח
                if not res_items or "שטח פתוח" in res_items[0]:
                    res_items = ["לא אותרה סצנה ביטחונית משמעותית"]
                    max_severity = 0
                    main_category = "שטח פתוח"

                return {
                    "detections": res_items,
                    "severity_score": max_severity,
                    "category": main_category,
                    "annotated_url": None  # CLIP לא מצייר מלבנים
                }

        except Exception as e:
            print(f"Error in CLIP analysis: {e}")
            return {"detections": ["שגיאה בניתוח הקשר"], "severity_score": 0, "category": "שגיאה",
                    "annotated_url": None}


if __name__ == "__main__":
    analyzer = ClipVisionAnalyzer()
    print("מודל ה-CLIP תקין ומוכן לשילוב.")