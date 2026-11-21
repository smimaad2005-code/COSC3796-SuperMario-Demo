
import os
import sys

# Set the working directory to the bundled game resources.
if getattr(sys, "frozen", False):
    os.chdir(sys._MEIPASS)
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

from source.main import main

if __name__ == "__main__":
    main()
