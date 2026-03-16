from datetime import datetime
from PIL import Image
from pathlib import Path
from PIL.ExifTags import TAGS
from pillow_heif import register_heif_opener

register_heif_opener()

FORMATS = [
    "%Y:%m:%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y/%m/%d %H:%M:%S",
]

SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.heic', '.avif'}

def dms_to_decimal(dms_tuple, ref):
    degrees = dms_tuple[0]
    minutes = dms_tuple[1]
    seconds = dms_tuple[2]
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def extract_datetime(data):
    date_str = data.get('DateTimeOriginal') or data.get('DateTime')
    if not date_str: return None
    for fmt in FORMATS:
        try:
            parsed = datetime.strptime(date_str, fmt)
            return parsed.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    return date_str

def latitude(data):
    if 'GPSInfo' in data and 2 in data['GPSInfo'] and 1 in data['GPSInfo']:
        return dms_to_decimal(data['GPSInfo'][2], data['GPSInfo'][1])
    return None

def longitude(data):
    if 'GPSInfo' in data and 4 in data['GPSInfo'] and 3 in data['GPSInfo']:
        return dms_to_decimal(data['GPSInfo'][4], data['GPSInfo'][3])
    return None

def camera_make(data):
    return data.get('Make').split("\x00")[0]

def camera_model(data):
    return data.get('Model').split("\x00")[0]

def has_gps(data):
    return latitude(data) is not None and longitude(data) is not None

def extract_metadata(path: Path):
    try:
        with Image.open(path) as img:
            data = None
            if hasattr(img, 'getexif'):
                exif = img.getexif()
                if exif is not None:
                    data = {TAGS.get(k, k): v for k, v in exif.items()}
                    if 34853 in exif:
                        gps_ifd = exif.get_ifd(34853)
                        data['GPSInfo'] = {k: v for k, v in gps_ifd.items()}
    except Exception:
        data = None

    if data is None:
        return {
            "filename": path.name, "datetime": None, "latitude": None,
            "longitude": None, "camera_make": None, "camera_model": None, "has_gps": False
        }

    return {
        "filename": path.name, "datetime": extract_datetime(data),
        "latitude": latitude(data), "longitude": longitude(data),
        "camera_make": camera_make(data), "camera_model": camera_model(data), "has_gps": has_gps(data)
    }

def extract_all(folder_path):
    path = Path(folder_path)
    imgs = []
    try:
        # rglob חיפוש עמוק בכל תתי-התיקיות
        for file_path in path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                metadata = extract_metadata(file_path)
                if metadata:
                    # חובה! שומר את הנתיב המלא כדי שה-AI ידע למצוא את הקובץ
                    metadata["filepath"] = str(file_path.absolute())
                    imgs.append(metadata)
    except Exception as e:
        print(f"Error reading folder: {e}")
    return imgs