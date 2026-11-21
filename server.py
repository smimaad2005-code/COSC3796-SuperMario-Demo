
from flask import Flask, request, send_file, render_template_string, abort, Response
from pathlib import Path
from datetime import datetime
from io import BytesIO
from PIL import Image
import os
import secrets

app = Flask(__name__)

UPLOAD_FOLDER = Path(__file__).resolve().parent / "server_uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

UPLOAD_KEY = os.environ.get("MARIO_UPLOAD_KEY")
VIEW_PASSWORD = os.environ.get("MARIO_VIEW_PASSWORD")

if not UPLOAD_KEY or not VIEW_PASSWORD:
    raise SystemExit(
        "Set MARIO_UPLOAD_KEY and MARIO_VIEW_PASSWORD before starting."
    )

latest_file = None

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Super Mario Screenshot Demo</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background: #161b22;
            color: white;
            padding: 30px;
        }
        img {
            max-width: 90%;
            border: 2px solid #58a6ff;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <h1>Super Mario Screenshot Demonstration</h1>
    <p>Authorized demonstration screenshots only.</p>
    <p>This page refreshes every 30 seconds.</p>
    {% if has_image %}
        <img src="/latest" alt="Latest screenshot">
    {% else %}
        <p>No screenshots uploaded yet.</p>
    {% endif %}
</body>
</html>
"""

@app.before_request
def authenticate():
    if request.path == "/upload":
        supplied = request.headers.get("X-Upload-Key", "")
        if not secrets.compare_digest(supplied, UPLOAD_KEY):
            abort(401)
    else:
        auth = request.authorization
        if (
            not auth
            or not secrets.compare_digest(auth.username or "", "viewer")
            or not secrets.compare_digest(auth.password or "", VIEW_PASSWORD)
        ):
            return Response(
                "Authentication required",
                401,
                {"WWW-Authenticate": 'Basic realm="Mario Demo"'}
            )

@app.route("/")
def index():
    return render_template_string(
        HTML,
        has_image=latest_file is not None
    )

@app.route("/upload", methods=["POST"])
def upload():
    global latest_file

    if "screenshot" not in request.files:
        return {"error": "No screenshot provided"}, 400

    try:
        data = request.files["screenshot"].read(10 * 1024 * 1024 + 1)

        if len(data) > 10 * 1024 * 1024:
            return {"error": "Image too large"}, 413

        image = Image.open(BytesIO(data))
        image.verify()

        image = Image.open(BytesIO(data))
        image.load()

        filename = "screenshot_" + datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        ) + ".png"

        destination = UPLOAD_FOLDER / filename
        image.save(destination, format="PNG")
        latest_file = destination

        print("Screenshot received:", filename)
        return {"message": "Screenshot uploaded successfully"}

    except Exception:
        return {"error": "Invalid image"}, 400

@app.route("/latest")
def latest():
    if latest_file is None or not latest_file.exists():
        abort(404)

    response = send_file(latest_file, mimetype="image/png")
    response.headers["Cache-Control"] = "no-store"
    return response

if __name__ == "__main__":
    print("Starting secured Super Mario demonstration server...")
    app.run(host="127.0.0.1", port=5000, debug=False)
