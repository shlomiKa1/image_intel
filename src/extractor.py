from datetime import datetime
from PIL import Image
from pathlib import Path
from PIL.ExifTags import TAGS
from pillow_heif import register_heif_opener

register_heif_opener()  # ← בראש הקובץ, לפני כל שימוש ב-PIL

FORMATS = [
        "%Y:%m:%d %H:%M:%S",  # EXIF סטנדרטי
        "%Y-%m-%d %H:%M:%S",  # מקפים
        "%Y/%m/%d %H:%M:%S",  # לוכסנים
    ]

SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.heic'}

"""
extractor.py - שליפת EXIF מתמונות
צוות 1, זוג A

ראו docs/api_contract.md לפורמט המדויק של הפלט.

"""
def dms_to_decimal(dms_tuple, ref):
    """
    פונקצית לחישוב שטח של המיקום של ה GPS
    Args:
        dms_tuple: טפל של (מעלות, דקות, שניות) משמאל לימין
        ref: איזה אזור במפה: (N, E, S, W)

    Returns: מספר עשרוני של מיקום המדויק של ה GPS למפה
    """
    degrees = dms_tuple[0]
    minutes = dms_tuple[1]
    seconds = dms_tuple[2]
    decimal = float(degrees) + (float(minutes) / 60) + (float(seconds) / 3600)
    # טיפול בדרום ומערב שצריך את הערך השלילי
    if ref in [b'S', b'W', 'S', 'W']:
        decimal = -decimal
    return decimal

def has_gps(data: dict):
    """
    בודק אם קיים GPS לקובץ
    Args:
        data: מילון של פרטים על התמונה

    Returns: True אם יש GPS, אחרת False
    """
    # מילון למפתחות של הקווים למיקום של המפה
    required_keys = {1, 2, 3, 4}
    return required_keys.issubset(data["GPSInfo"].keys()) if "GPSInfo" in data else False

def latitude(data: dict):
    """
    מחלץ את קו הרוחב של המיקום של התמונה
    Args:
        data: מילון של פרטים על התמונה

    Returns: מספר עשרוני של latitude, או None
    """
    if has_gps(data):
        try:
            lat =  dms_to_decimal(data["GPSInfo"][2], data["GPSInfo"][1])
            return lat
        except (KeyError, TypeError, ValueError, IndexError):
            return None
    else:
        return None

def longitude(data: dict):
    """
    מחלץ את קו האורך של המיקום של התמונה
    Args:
        data: מילון של פרטים על התמונה

    Returns: מספר עשרוני של longitude, או None
    """
    if has_gps(data):
        try:
            lon = dms_to_decimal(data["GPSInfo"][4], data["GPSInfo"][3])
            return lon
        except (KeyError, TypeError, ValueError, IndexError):
            return None
    else:
        return None

def extract_datetime(data: dict):
    """
    מחלץ את התאריך והזמן שצולם התמונה
    Args:
        data: מילון של פרטים על התמונה

    Returns: מחרוזת תאריך data["DateTimeOriginal"], או None אם יש תאריך לא תקין או אין תאריך
    """
    raw = data.get("DateTimeOriginal") or data.get("DateTime")
    if not raw:
        return None

    for fmt in FORMATS:
        try:
            dt = datetime.strptime(raw.strip(), fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")  # תמיד מחזיר פורמט אחיד
        except ValueError:
            continue
    return None

def camera_make(data: dict):
    """
    מחלץ את היצרן של המכשיר שבו צולם התמונה
    Args:
        data: מילון של פרטים על התמונה

    Returns: מחרוזת יצרן data["Make"], או None
    """
    try:
        return data["Make"].split("\x00")[0]
    except (KeyError, AttributeError):
        return None

def camera_model(data: dict):
    """
    מחלץ את סוג המכשיר שבו צולם התמונה
    Args:
        data: מילון של פרטים על התמונה

    Returns: מחרוזת סוג המכשיר data["Model"], או None
    """
    try:
        return data["Model"].split("\x00")[0]
    except (KeyError, AttributeError):
        return None

def extract_metadata(image_path):
    """
    שולף EXIF מתמונה בודדת.

    Args:
        image_path: נתיב לקובץ תמונה

    Returns:
        dict עם: filename, datetime, latitude, longitude,
              camera_make, camera_model, has_gps
    """
    path = Path(image_path)
    data = None  # ← הגדר כאן מראש

    try:
        with Image.open(image_path) as img:
            if path.suffix.lower() == '.heic':
                exif_raw = img.getexif()
                data = {TAGS.get(k, k): v for k, v in exif_raw.items()}
                gps_data = exif_raw.get_ifd(0x8825)
                if gps_data:
                    data["GPSInfo"] = {k: v for k, v in gps_data.items()}
            else:
                exif = img._getexif()
                if exif is not None:
                    data = {TAGS.get(k, k): v for k, v in exif.items()}
    except (OSError, IOError, AttributeError):
        data = None

    if data is None:
        return {
            "filename": path.name,
            "datetime": None,
            "latitude": None,
            "longitude": None,
            "camera_make": None,
            "camera_model": None,
            "has_gps": False
        }

    return {
        "filename": path.name,
        "datetime": extract_datetime(data),
        "latitude": latitude(data),
        "longitude": longitude(data),
        "camera_make": camera_make(data),
        "camera_model": camera_model(data),
        "has_gps": has_gps(data)
    }

def extract_all(folder_path):
    """
    שולף EXIF מכל התמונות בתיקייה.

    Args:
        folder_path: נתיב לתיקייה

    Returns:
        list של dicts (כמו extract_metadata), או רשימה ריקה
    """
    path = Path(folder_path)
    imgs = []
    try:
        # עוברים על כל הקבצים שיש בתיקייה
        for file in path.rglob('*'):
            # בדיקות האם זה קובץ שמסתיים באחד מ- {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.heic'}
            if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS:
                imgs.append(extract_metadata(file))
        return imgs
    except OSError:
        return []