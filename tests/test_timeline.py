# השורות הראשונות משנות את הניתוב כדי שאני יוכל לייבא את הפונקציות מתיקייה שכנה לא כולם צריכים את השורות האלה תלוי בסביבת עבודה
import sys
import os

# מוסיפים את תיקיית הפרויקט ל־sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")  # assuming file is inside a subfolder

from src import extractor
from src import timeline

da = extractor.extract_all("/Users/gidi/homework/image_intel/images/ready")

h = timeline.create_timeline(da)
with open('test.html', 'w', encoding='utf-8')as f:
    f.write(h)