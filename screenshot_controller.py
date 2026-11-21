
from pathlib import Path
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from PIL import Image
import win32gui
import win32ui
import ctypes
import os
import time
import uuid

UPLOAD_URL = "http://127.0.0.1:5000/upload"
MARIO_TITLE = "Super Mario Bros"
TEST_TITLE = "Mario Screenshot Demo - Test Window"
INTERVAL_SECONDS = 30


def capture_window(window_title):
    hwnd = win32gui.FindWindow(None, window_title)

    if not hwnd:
        return None

    if win32gui.IsIconic(hwnd):
        return None

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    if width <= 0 or height <= 0:
        return None

    window_dc = win32gui.GetWindowDC(hwnd)
    source_dc = win32ui.CreateDCFromHandle(window_dc)
    memory_dc = source_dc.CreateCompatibleDC()

    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(source_dc, width, height)
    memory_dc.SelectObject(bitmap)

    try:
        result = ctypes.windll.user32.PrintWindow(
            hwnd, memory_dc.GetSafeHdc(), 2
        )

        if result != 1:
            return None

        info = bitmap.GetInfo()
        pixels = bitmap.GetBitmapBits(True)

        return Image.frombuffer(
            "RGB",
            (info["bmWidth"], info["bmHeight"]),
            pixels,
            "raw",
            "BGRX",
            0,
            1
        ).copy()

    finally:
        win32gui.DeleteObject(bitmap.GetHandle())
        memory_dc.DeleteDC()
        source_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, window_dc)


def upload_image(image, upload_key, prefix):
    folder = Path(__file__).resolve().parent / "demo_screenshots"
    folder.mkdir(exist_ok=True)

    filename = (
        prefix + "_" +
        datetime.now().strftime("%Y%m%d_%H%M%S_%f") +
        ".png"
    )

    screenshot_path = folder / filename
    image.save(screenshot_path)

    boundary = "MarioDemo" + uuid.uuid4().hex
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

    with urlopen(request, timeout=15) as response:
        response.read()

    print("Screenshot uploaded:", filename, flush=True)


def main():
    print("=== AUTHORIZED MARIO SCREENSHOT DEMO ===")
    print("Captures Mario while the game is open.")
    print("After Mario closes, captures the test window.")
    print("Automatic upload every 30 seconds.")
    print("Press Ctrl+C to stop.")

    upload_key = os.environ.get("MARIO_UPLOAD_KEY")

    if not upload_key:
        print("ERROR: MARIO_UPLOAD_KEY is not configured.")
        return

    answer = input("Start authorized screenshot demo? Type YES: ")

    if answer.strip() != "YES":
        print("Cancelled.")
        return

    print("SCREENSHOT DEMO ACTIVE — Ctrl+C to stop.")

    try:
        while True:
            try:
                mario = capture_window(MARIO_TITLE)

                if mario is not None:
                    upload_image(mario, upload_key, "mario")
                else:
                    test_image = capture_window(TEST_TITLE)

                    if test_image is not None:
                        upload_image(test_image, upload_key, "after_close")
                    else:
                        print(
                            "No available demo window. "
                            "Skipping screenshot.",
                            flush=True
                        )

            except (HTTPError, URLError, OSError) as error:
                print("Capture/upload error:", error, flush=True)

            time.sleep(INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nSCREENSHOT DEMO STOPPED.")


if __name__ == "__main__":
    main()
