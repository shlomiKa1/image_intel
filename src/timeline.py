def create_timeline(images_data):
    dated_images = [img for img in images_data if img.get("datetime")]
    dated_images.sort(key=lambda x: x["datetime"])

    html = """
    <style>

    body{
        font-family: Arial;
        background:#f7f7f7;
    }

    .timeline{
        position:relative;
        max-width:900px;
        margin:auto;
    }

    .timeline::after{
        content:'';
        position:absolute;
        width:4px;
        background:#444;
        top:0;
        bottom:0;
        left:50%;
        margin-left:-2px;
    }

    .event{
        padding:20px 40px;
        position:relative;
        width:50%;
        box-sizing:border-box;
    }

    .left{
        left:0;
        text-align:right;
        padding-right:60px;
    }

    .right{
        left:50%;
        text-align:left;
        padding-left:60px;
    }

    .card{
        background:white;
        padding:15px;
        border-radius:10px;
        box-shadow:0 4px 10px rgba(0,0,0,0.15);
        display:inline-block;
        max-width:300px;
    }

    .dot{
        position:absolute;
        top:25px;
        width:14px;
        height:14px;
        background:#0077ff;
        border-radius:50%;
        border:3px solid white;
        box-shadow:0 0 0 2px #0077ff;
    }

    .left .dot{
        right:-7px;
    }

    .right .dot{
        left:-7px;
    }

    .date{
        font-weight:bold;
        color:#0077ff;
        margin-bottom:5px;
    }

    .camera{
        color:gray;
        font-size:12px;
    }

    </style>

    <div class="timeline">
    """

    for i, img in enumerate(dated_images):

        side = "left" if i % 2 == 0 else "right"

        html += f"""
        <div class="event {side}">
            <div class="dot"></div>

            <div class="card">
                <div class="date">{img.get("datetime")}</div>
                <div>{img.get("filename")}</div>
                <div class="camera">{img.get("camera_make")} {img.get("camera_model")}</div>
            </div>
        </div>
        """

    html += "</div>"

    return html