import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk, ImageOps
import pillow_heif

pillow_heif.register_heif_opener()

EXTENSIONS = {
    ".heic", ".heif", ".jpg", ".jpeg", ".png",
    ".bmp", ".gif", ".tif", ".tiff", ".webp"
}

class OpenHEIC:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenHEIC")
        self.root.geometry("1100x750")
        self.root.minsize(500, 350)

        self.files = []
        self.index = 0
        self.photo = None

        toolbar = tk.Frame(root, padx=8, pady=8)
        toolbar.pack(fill="x")

        tk.Button(toolbar, text="Open Image", command=self.choose_file).pack(side="left")
        tk.Button(toolbar, text="◀ Previous", command=self.previous).pack(side="left", padx=8)
        tk.Button(toolbar, text="Next ▶", command=self.next).pack(side="left")

        self.status = tk.Label(toolbar, text="Open an image to begin")
        self.status.pack(side="left", padx=12)

        self.canvas = tk.Label(root, bg="#202020", anchor="center")
        self.canvas.pack(fill="both", expand=True)

        self.root.bind_all("<Right>", self.next)
        self.root.bind_all("<Left>", self.previous)
        self.root.bind_all("<Prior>", self.previous)
        self.root.bind_all("<Next>", self.next)

        self.root.bind("<Configure>", self.on_resize)

        if len(sys.argv) > 1:
            self.open_path(sys.argv[1])

    def choose_file(self):
        path = filedialog.askopenfilename(
            title="Open image",
            filetypes=[("Images", "*.heic *.heif *.jpg *.jpeg *.png *.bmp *.gif *.tif *.tiff *.webp"),
                       ("All files", "*.*")]
        )
        if path:
            self.open_path(path)

    def open_path(self, path):
        try:
            selected = Path(path).resolve()
            if not selected.is_file():
                raise FileNotFoundError(f"File not found:\n{selected}")

            folder_files = [
                p for p in selected.parent.iterdir()
                if p.is_file() and p.suffix.lower() in EXTENSIONS
            ]
            folder_files.sort(key=lambda p: p.name.casefold())

            self.files = folder_files
            self.index = next(
                i for i, p in enumerate(self.files)
                if p.resolve() == selected
            )
            self.show_current()
        except Exception as exc:
            messagebox.showerror("OpenHEIC", f"Could not open image:\n{exc}")

    def show_current(self):
        if not self.files:
            return

        path = self.files[self.index]
        try:
            with Image.open(path) as image:
                image = ImageOps.exif_transpose(image).convert("RGB")
                image.load()
                self.original = image.copy()

            self.root.title(f"OpenHEIC — {path.name}")
            self.status.config(
                text=f"{self.index + 1} / {len(self.files)}  |  {path.name}"
            )
            self.render_image()
        except Exception as exc:
            messagebox.showerror(
                "Image error",
                f"Could not display:\n{path}\n\n{exc}"
            )

    def render_image(self):
        if not hasattr(self, "original"):
            return

        width = max(self.canvas.winfo_width() - 20, 100)
        height = max(self.canvas.winfo_height() - 20, 100)

        image = self.original.copy()
        image.thumbnail((width, height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.config(image=self.photo, text="")

    def next(self, event=None):
        if self.files:
            self.index = (self.index + 1) % len(self.files)
            self.show_current()
        return "break"

    def previous(self, event=None):
        if self.files:
            self.index = (self.index - 1) % len(self.files)
            self.show_current()
        return "break"

    def on_resize(self, event):
        if event.widget == self.root:
            self.root.after_idle(self.render_image)

if __name__ == "__main__":
    root = tk.Tk()
    app = OpenHEIC(root)
    root.mainloop()
