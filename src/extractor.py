from PIL import Image
from pathlib import Path
from PIL.ExifTags import TAGS


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
        except:
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
        except:
            return None
    else:
        return None


def datatime(data: dict):
    """
    מחלץ את התאריך והזמן שצולם התמונה
    Args:
        data: מילון של פרטים על התמונה

    Returns: מחרוזת תאריך data["DateTimeOriginal"], או None
    """
    try:
        return data["DateTimeOriginal"]
    except:
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
    except:
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
    except:
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

    # תיקון: טיפול בתמונה בלי EXIF - בלי זה, exif.items() נופל עם AttributeError
    try:
        img = Image.open(image_path)
        exif = img._getexif()
    except Exception:
        exif = None

    if exif is None:
        return {
            "filename": path.name,
            "datetime": None,
            "latitude": None,
            "longitude": None,
            "camera_make": None,
            "camera_model": None,
            "has_gps": False
        }

    data = {}
    for tag_id, value in exif.items():
        tag = TAGS.get(tag_id, tag_id)
        data[tag] = value
    # תיקון: הוסר print(data) שהיה כאן - הדפיס את כל ה-EXIF הגולמי על כל תמונה

    exif_dict = {
        "filename": path.name,
        "datetime": datatime(data),
        "latitude": latitude(data),
        "longitude": longitude(data),
        "camera_make": camera_make(data),
        "camera_model": camera_model(data),
        "has_gps": has_gps(data)
    }
    return exif_dict


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
    except Exception as e:
        print(e)
        return []