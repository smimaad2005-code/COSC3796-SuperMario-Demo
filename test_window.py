
import tkinter as tk
from datetime import datetime

WINDOW_TITLE = "Mario Screenshot Demo - Test Window"

root = tk.Tk()
root.title(WINDOW_TITLE)
root.geometry("650x400")
root.configure(bg="#172033")

title = tk.Label(
    root,
    text="SCREENSHOT DEMONSTRATION",
    font=("Arial", 22, "bold"),
    fg="white",
    bg="#172033"
)
title.pack(pady=45)

message = tk.Label(
    root,
    text="Mario has closed.\nThis is an authorized test window.",
    font=("Arial", 16),
    fg="#9fe870",
    bg="#172033"
)
message.pack(pady=20)

clock = tk.Label(
    root,
    font=("Arial", 18),
    fg="white",
    bg="#172033"
)
clock.pack(pady=20)

def update_clock():
    clock.config(
        text=datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    )
    root.after(1000, update_clock)

update_clock()
root.mainloop()
