
from pathlib import Path
from PIL import Image
import win32gui
import win32ui
import ctypes

WINDOW_TITLE = "Super Mario Bros"

def main():
    hwnd = win32gui.FindWindow(None, WINDOW_TITLE)

    if not hwnd:
        print("Mario window not found. Start the game first.")
        return

    if win32gui.IsIconic(hwnd):
        print("Mario is minimized. Restore the window first.")
        return

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    if width <= 0 or height <= 0:
        print("Invalid Mario window dimensions.")
        return

    window_dc = win32gui.GetWindowDC(hwnd)
    source_dc = win32ui.CreateDCFromHandle(window_dc)
    memory_dc = source_dc.CreateCompatibleDC()

    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(source_dc, width, height)
    memory_dc.SelectObject(bitmap)

    try:
        result = ctypes.windll.user32.PrintWindow(
            hwnd,
            memory_dc.GetSafeHdc(),
            2
        )

        if result != 1:
            print("Windows could not capture Mario.")
            return

        info = bitmap.GetInfo()
        pixels = bitmap.GetBitmapBits(True)

        image = Image.frombuffer(
            "RGB",
            (info["bmWidth"], info["bmHeight"]),
            pixels,
            "raw",
            "BGRX",
            0,
            1
        ).copy()

        output = (
            Path(__file__).resolve().parent
            / "mario_capture_test.png"
        )

        image.save(output)

        print("Capture saved successfully!")
        print("Location:", output)
        print("Check that the image contains only Mario.")

    finally:
        win32gui.DeleteObject(bitmap.GetHandle())
        memory_dc.DeleteDC()
        source_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, window_dc)

if __name__ == "__main__":
    main()
