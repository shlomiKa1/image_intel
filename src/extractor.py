from PIL import Image
from PIL.ExifTags import TAGS
from pathlib import Path
import os

"""
extractor.py - שליפת EXIF מתמונות
צוות 1, זוג A

ראו docs/api_contract.md לפורמט המדויק של הפלט.

"""


def has_gps(data: dict):
    """
    בודק אם קיים GPS לקובץ
    Args:
        data: מילון של פרטים על התמונה

    Returns: True/False
    """
    return "GPSInfo" in data


def latitude(data: dict):
    """
    מחלץ את קו הרוחב של המיקום של התמונה
    Args:
        data: מילון של פרטים על התמונה

    Returns: מספר עשרוני של latitude
    """
    if has_gps(data):
        try:
            lat =  data["GPSInfo"][2]
            result = float(lat[0] + lat[1]/60 + lat[2]/3600)
            return result
        except:
            return None
    else:
        return None


def longitude(data: dict):
    """
    מחלץ את קו האורך של המיקום של התמונה
    Args:
        data: מילון של פרטים על התמונה

    Returns: מספר עשרוני של longitude
    """
    if has_gps(data):
        try:
            lat = data["GPSInfo"][4]
            result = float(lat[0] + (lat[1] / 60) + (lat[2] / 3600))
            return result
        except:
            return None
    else:
        return None


def datatime(data: dict):
    """
    מחלץ את התאריך והזמן שצולם התמונה
    Args:
        data: מילון של פרטים על התמונה

    Returns: תאריך data["DateTimeOriginal"]
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

    Returns: יצרן data["Make"]
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

    Returns: סוג המכשיר data["Model"]
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
        list של dicts (כמו extract_metadata)
    """
    path = Path(folder_path)
    imgs = []
    try:
        # עוברים על כל הקבצים שיש בתיקייה
        for file in path.rglob('*'):
            try:
                # מנסה לפתוח כתמונה ואם לא מצליח ממשיך הלאה
                if Image.open(file):
                    imgs.append(extract_metadata(file))
            except:
                continue
        return imgs
    except Exception as e:
        print(e)
        return None
