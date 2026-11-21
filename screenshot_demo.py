
from pathlib import Path
from datetime import datetime

import pygame
from PIL import ImageGrab


def capture_screenshot():
    print("Screenshot demonstration")
    print("Only capture your own screen with your permission.")

    answer = input("Capture a screenshot now? (yes/no): ").strip().lower()

    if answer != "yes":
        print("Screenshot cancelled.")
        return

    folder = Path(__file__).resolve().parent / "demo_screenshots"
    folder.mkdir(exist_ok=True)

    filename = "screenshot_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
    destination = folder / filename

    screenshot = ImageGrab.grab()
    screenshot.save(destination)

    print("Screenshot saved successfully!")
    print("Location:", destination)


if __name__ == "__main__":
    capture_screenshot()
