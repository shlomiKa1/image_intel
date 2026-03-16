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

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".heic", ".avif"}


def safe_str(value):
    """Convert EXIF value to clean string or return None."""
    if value is None:
        return None
    if isinstance(value, bytes):
        value = value.decode(errors="ignore")
    return str(value).split("\x00")[0].strip()


def to_float(value):
    """Convert EXIF numeric values (including rationals) to float."""
    try:
        return float(value)
    except Exception:
        try:
            return float(value[0]) / float(value[1])
        except Exception:
            return None


def dms_to_decimal(dms_tuple, ref):
    """Convert GPS degrees/minutes/seconds to decimal format."""
    if not dms_tuple or len(dms_tuple) != 3:
        return None

    degrees = to_float(dms_tuple[0])
    minutes = to_float(dms_tuple[1])
    seconds = to_float(dms_tuple[2])

    if degrees is None or minutes is None or seconds is None:
        return None

    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)

    if isinstance(ref, bytes):
        ref = ref.decode(errors="ignore")

    if ref in ["S", "W"]:
        decimal = -decimal

    return decimal


def extract_datetime(data):
    """Extract and normalize EXIF datetime."""
    date_str = data.get("DateTimeOriginal") or data.get("DateTime")
    date_str = safe_str(date_str)

    if not date_str:
        return None

    for fmt in FORMATS:
        try:
            parsed = datetime.strptime(date_str, fmt)
            return parsed.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

    return date_str


def latitude(data):
    gps = data.get("GPSInfo")
    if gps and 2 in gps and 1 in gps:
        return dms_to_decimal(gps[2], gps[1])
    return None


def longitude(data):
    gps = data.get("GPSInfo")
    if gps and 4 in gps and 3 in gps:
        return dms_to_decimal(gps[4], gps[3])
    return None


def camera_make(data):
    return safe_str(data.get("Make"))


def camera_model(data):
    return safe_str(data.get("Model"))


def has_gps(data):
    return latitude(data) is not None and longitude(data) is not None


def extract_metadata(path: Path):
    data = None

    try:
        with Image.open(path) as img:
            if hasattr(img, "getexif"):
                exif = img.getexif()
                if exif:
                    data = {TAGS.get(k, k): v for k, v in exif.items()}

                    if 34853 in exif:
                        gps_ifd = exif.get_ifd(34853)
                        data["GPSInfo"] = {k: v for k, v in gps_ifd.items()}
    except Exception:
        data = None

    if data is None:
        return {
            "filename": path.name,
            "datetime": None,
            "latitude": None,
            "longitude": None,
            "camera_make": None,
            "camera_model": None,
            "has_gps": False,
        }

    return {
        "filename": path.name,
        "datetime": extract_datetime(data),
        "latitude": latitude(data),
        "longitude": longitude(data),
        "camera_make": camera_make(data),
        "camera_model": camera_model(data),
        "has_gps": has_gps(data),
    }


def extract_all(folder_path):
    path = Path(folder_path)
    imgs = []

    try:
        for file_path in path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                metadata = extract_metadata(file_path)
                metadata["filepath"] = str(file_path.absolute())
                imgs.append(metadata)
    except Exception as e:
        print(f"Error reading folder: {e}")

    return imgs