
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import os

UPLOAD_URL = "http://127.0.0.1:5000/upload"

def main():
    folder = Path(__file__).resolve().parent / "demo_screenshots"
    screenshots = list(folder.glob("*.png")) if folder.exists() else []

    if not screenshots:
        print("No screenshots found in demo_screenshots.")
        return

    screenshot = max(screenshots, key=lambda file: file.stat().st_mtime)
    print("Screenshot selected:", screenshot.name)

    answer = input("Upload this screenshot to your demo server? (yes/no): ")
    if answer.strip().lower() != "yes":
        print("Upload cancelled.")
        return

    upload_key = os.environ.get("MARIO_UPLOAD_KEY")
    if not upload_key:
        print("MARIO_UPLOAD_KEY is not set in this terminal.")
        return

    boundary = "MarioDemoUploadBoundary"
    image_data = screenshot.read_bytes()

    body = (
        (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="screenshot"; '
            f'filename="{screenshot.name}"\r\n'
            "Content-Type: image/png\r\n\r\n"
        ).encode("utf-8")
        + image_data
        + f"\r\n--{boundary}--\r\n".encode("utf-8")
    )

    request = Request(
        UPLOAD_URL,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "X-Upload-Key": upload_key,
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=15) as response:
            print("Upload successful!")
            print(response.read().decode("utf-8"))
    except HTTPError as error:
        print("Server rejected upload. HTTP status:", error.code)
    except URLError as error:
        print("Could not connect to server:", error.reason)

if __name__ == "__main__":
    main()
