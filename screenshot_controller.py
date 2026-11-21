
from pathlib import Path
from datetime import datetime
from urllib.request import Request, urlopen
from PIL import ImageGrab
import os

UPLOAD_URL = "http://127.0.0.1:5000/upload"

def main():
    print("=== SUPER MARIO SCREENSHOT DEMO ===")
    print("This program captures your screen only with permission.")

    answer = input("Capture and upload a new screenshot? (yes/no): ")
    if answer.strip().lower() != "yes":
        print("Cancelled.")
        return

    upload_key = os.environ.get("MARIO_UPLOAD_KEY")
    if not upload_key:
        print("Error: MARIO_UPLOAD_KEY is not set.")
        return

    folder = Path(__file__).resolve().parent / "demo_screenshots"
    folder.mkdir(exist_ok=True)

    filename = "screenshot_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".png"
    screenshot_path = folder / filename

    ImageGrab.grab().save(screenshot_path)
    print("New screenshot captured:", filename)

    boundary = "MarioScreenshotDemoBoundary"
    image_data = screenshot_path.read_bytes()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="screenshot"; filename="{filename}"\r\n'
        "Content-Type: image/png\r\n\r\n"
    ).encode("utf-8") + image_data + (
        f"\r\n--{boundary}--\r\n"
    ).encode("utf-8")

    request = Request(
        UPLOAD_URL,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "X-Upload-Key": upload_key,
        },
        method="POST"
    )

    try:
        with urlopen(request, timeout=15) as response:
            print("New screenshot uploaded successfully!")
            print(response.read().decode("utf-8"))
    except Exception as error:
        print("Upload failed:", error)

if __name__ == "__main__":
    main()

