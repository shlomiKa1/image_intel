# # השורות הראשונות משנות את הניתוב כדי שאני יוכל לייבא את הפונקציות מתיקייה שכנה לא כולם צריכים את השורות האלה תלוי בסביבת עבודה
# # import sys
# # import os
# #
# # # מוסיפים את תיקיית הפרויקט ל־sys.path
# # sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")  # assuming file is inside a subfolder
#
# from src import extractor
# from src import timeline
#
# da = extractor.extract_all("/Users/gidi/homework/image_intel/images/sample_date")
#
# h = timeline.create_timeline(da)
# with open('test.html', 'w', encoding='utf-8')as f:
#     f.write(h)

from pathlib import Path
from src import extractor
from src import timeline

if __name__ == "__main__":
    # ext = extractor.extract_all(Path(r"C:\Users\shlom\Kodcode\תכנות\פרויקטים\image_intel\images\uploads"))
    # ext = extractor.extract_all(Path(r"C:\Users\shlom\Kodcode\תכנות\פרויקטים\image_intel\images\sample_data"))

    images_path = Path(r"C:\Users\shlom\Kodcode\תכנות\פרויקטים\image_intel\images\sample_data")
    images_data = extractor.extract_all(images_path)

    print(f"סה\"כ תמונות בתיקייה: {len(images_data)}")
    # for img in images_data:
    #     print(img["filename"], "→ datetime:", img["datetime"])
    # יוצר את ה-timeline
    html = timeline.create_timeline(images_data)
    output = Path(r"C:\Users\shlom\Kodcode\תכנות\פרויקטים\image_intel\src\test_timeline.html")

    if html is not None:
        with open(output, "w", encoding="utf-8") as f:
            f.write(html)
        print("timeline saved to test_timeline")
    else:
        print("No GPS images found.")
