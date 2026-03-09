import folium
from branca.element import Element

# רשימת צבעים
FOLIUM_COLORS = [
    "red", "blue", "green", "purple", "orange", "darkred",
    "lightred", "beige", "darkblue", "darkgreen", "cadetblue",
    "darkpurple", "white", "pink", "lightblue", "lightgreen",
    "gray", "black", "lightgray"
]


def get_images_with_gps(arr):
    """מחזיר רק תמונות שיש להן נתוני GPS.

    :param arr: רשימת מילונים של תמונות
    :type arr: list
    :return: רשימת תמונות עם GPS
    :rtype: list
    """
    return [img for img in arr if img.get("has_gps")]


def sort_by_time(arr):
    """ממיין את רשימת התמונות לפי זמן הצילום.
    תמונות ללא שדה datetime ימוינו לתחילת הרשימה.

    :param arr: רשימת מילונים של תמונות
    :type arr: list
    :return: None
    :rtype: None
    """
    arr.sort(key=lambda x: x.get("datetime", ""))


def get_avg(arr) -> tuple[float, float]:
    """מחשב ממוצע קווי רוחב ואורך של רשימת תמונות.

    :param arr: רשימת תמונות עם נתוני GPS
    :type arr: list
    :return: ממוצע קו רוחב וממוצע קו אורך, או (0.0, 0.0) אם הרשימה ריקה
    :rtype: tuple[float, float]
    """
    arr_len = len(arr)
    if arr_len == 0:
        return 0.0, 0.0
    avg_lat = sum(img["latitude"] for img in arr) / arr_len
    avg_lng = sum(img["longitude"] for img in arr) / arr_len
    return avg_lat, avg_lng


def create_map(images_data):
    """יוצר מפה אינטראקטיבית עם כל המיקומים.

    :param images_data: רשימת מילונים מ-extract_all
    :type images_data: list
    :return: מחרוזת HTML של המפה, או None אם אין תמונות עם GPS
    :rtype: str | None
    """
    if not images_data:
        return None

    images_with_gps = get_images_with_gps(images_data)
    if not images_with_gps:
        return None

    sort_by_time(images_with_gps)
    avg_lat, avg_lon = get_avg(images_with_gps)

    # יצירת מפה שממורכזת על ממוצע המיקומים
    location_map = folium.Map(location=[avg_lat, avg_lon], zoom_start=8)

    devices_colors = {}
    path_points = []
    color_index = 0

    for i, img in enumerate(images_with_gps, 1):
        model = img.get("camera_model", "unknown")
        if model not in devices_colors:
            devices_colors[model] = FOLIUM_COLORS[color_index % len(FOLIUM_COLORS)]
            color_index += 1

        marker_color = devices_colors[model]
        lat = img["latitude"]
        lon = img["longitude"]

        popup_html = f"""
            <div style="font-family: Arial; min-width: 200px;">
                <h4 style="margin-bottom: 10px; margin-top: 0px;">
                    <i class="fa fa-camera"></i> {img.get('filename', 'Unknown')}
                </h4>
                <b>Photo #:</b> {i}<br>
                <b>Time:</b> {img.get('datetime', 'N/A')}<br>
                <b>Device:</b> {model}<br>
                <b>Coordinates:</b><br>
                {lat:.6f}, {lon:.6f}
            </div>
        """
        popup_obj = folium.Popup(popup_html, max_width=300)

        path_points.append([lat, lon])

        folium.Marker(
            [lat, lon],
            popup=popup_obj,
            icon=folium.Icon(color=marker_color, icon='camera', prefix='fa')
        ).add_to(location_map)

    if len(path_points) > 1:
        folium.PolyLine(
            path_points,
            color="darkblue",
            weight=3,
            opacity=0.7,
            dash_array='5, 5',
            tooltip='Photo Route'
        ).add_to(location_map)

    legend_items = ""
    for device, color in devices_colors.items():
        legend_items += f"""
            <div style="margin-bottom: 6px;">
                <span style="
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    background-color: {color};
                    border-radius: 50%;
                    margin-left: 8px;
                    border: 1px solid black;
                "></span>
                <span dir="ltr">{device}</span>
            </div>
        """

    legend_html = f"""
    <div style="
        position: fixed;
        bottom: 40px;
        right: 40px;
        z-index: 9999;
        background-color: white;
        border: 2px solid gray;
        border-radius: 8px;
        padding: 12px;
        font-size: 14px;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.2);
        min-width: 180px;
    ">
        <div style="font-weight: bold; margin-bottom: 10px;">מקרא מכשירים</div>
        {legend_items}
    </div>
    """

    location_map.get_root().html.add_child(Element(legend_html))

    return location_map.get_root().render()


if __name__ == "__main__":
    fake_data = [
        {
            "filename": "test1.jpg",
            "latitude": 32.0853,
            "longitude": 34.7818,
            "has_gps": True,
            "camera_make": "Samsung",
            "camera_model": "Galaxy S23",
            "datetime": "2025-01-12 08:30:00",
        },
        {
            "filename": "test2.jpg",
            "latitude": 31.7683,
            "longitude": 35.2137,
            "has_gps": True,
            "camera_make": "Apple",
            "camera_model": "iPhone 15 Pro",
            "datetime": "2025-01-13 09:00:00",
        },
    ]

    html = create_map(fake_data)

    if html is not None:
        with open("test_map.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Map saved to test_map.html")
    else:
        print("No GPS images found.")