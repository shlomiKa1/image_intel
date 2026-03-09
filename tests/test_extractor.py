from src import extractor
from pathlib import Path


if __name__ == "__main__":
    # print(extractor.extract_metadata(Path(r"C:\Users\shlom\Kodcode\תכנות\פרויקטים\image_intel\images\sample_data\20230205_183551.jpg")))
    # print(extractor.extract_metadata(Path(r"C:\Users\shlom\Kodcode\תכנות\פרויקטים\image_intel\images\ready\IMG_010.jpg")))
    # print(extractor.extract_metadata(r"C:\Users\shlom\Kodcode\תכנות\פרויקטים\image_intel\images\sample_data\תמונה של WhatsApp‏ 2024-06-08 בשעה 22.25.21_39231de9.jpg"))
    # print(extractor.extract_metadata(r"C:\Users\shlom\Kodcode\תכנות\פרויקטים\image_intel\images\sample_data\תהלוכה.jpg"))
    ext = extractor.extract_all(r"C:\Users\shlom\Kodcode\תכנות\פרויקטים\image_intel\images\sample_data")
    for line, info in enumerate(ext):
        print(f"{line}: {info}")
    print()
    pass
