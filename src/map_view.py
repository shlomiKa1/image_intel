import folium
from branca.element import Element
from folium.plugins import AntPath

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
    :return: ממוצע קו רוחב וממוצע קו אורך
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
    :return: HTML להטמעה של המפה, או None אם אין תמונות עם GPS
    :rtype: str | None
    """
    if not images_data:
        return None

    images_with_gps = get_images_with_gps(images_data)
    if not images_with_gps:
        return None

    sort_by_time(images_with_gps)
    avg_lat, avg_lon = get_avg(images_with_gps)

    location_map = folium.Map(
        location=[avg_lat, avg_lon],
        zoom_start=8,
        width="100%",
        height=500,
        scrollWheelZoom=False
    )
    location_map.get_root().html.add_child(
        folium.Element('<script>window.intel_map_id = null;</script>')
    )

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
                <h4 style="margin-bottom: 10px; margin-top: 0;">
                    {img.get('filename', 'Unknown')}
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
            icon=folium.Icon(color=marker_color, icon="camera", prefix="fa")
        ).add_to(location_map)

    if len(path_points) > 1:
        AntPath(
            path_points,
            color="darkblue",
            weight=4,
            opacity=0.8,
            delay=800,
            dash_array=[10, 20],
            pulse_color="white",
            tooltip="מסלול כרונולוגי"
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
        position: absolute;
        bottom: 20px;
        left: 20px;
        z-index: 1000;
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

    return location_map._repr_html_()