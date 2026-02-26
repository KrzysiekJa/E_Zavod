"""
Settings window for Appearance (Light/Dark mode)
"""
import tkinter as tk
from tkinter import ttk

class SettingsApp(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Settings")
        self.geometry("400x300")
        self.configure(bg="#f0f0f0")
        self.create_widgets()

    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Appearance tab
        appearance_tab = tk.Frame(notebook, bg="#f0f0f0")
        notebook.add(appearance_tab, text="Appearance")

        tk.Label(appearance_tab, text="Theme:", bg="#f0f0f0", font=("Helvetica", 12)).pack(pady=10)
        self.theme_var = tk.StringVar(value="Light")
        tk.Radiobutton(appearance_tab, text="Light", variable=self.theme_var, value="Light", bg="#f0f0f0", command=self.apply_theme).pack(anchor="w", padx=20)
        tk.Radiobutton(appearance_tab, text="Dark", variable=self.theme_var, value="Dark", bg="#f0f0f0", command=self.apply_theme).pack(anchor="w", padx=20)

        # Close button
        close_btn = tk.Button(self, text="Close", command=self.destroy, width=10, bg="#f44336", fg="white", font=("Helvetica", 12))
        close_btn.pack(pady=10)

    def apply_theme():
        global current_theme
        current_theme = theme_var.get()
        t = themes[current_theme]
        root.configure(bg=t["bg"])
    
        for b in buttons:
            if b["text"] == "EXIT":
                b.configure(bg=t["exit_bg"], fg=t["btn_fg"])
            else:
                b.configure(bg=t["btn_bg"], fg=t["btn_fg"])
    
        if settings_window.winfo_exists():
            settings_window.configure(bg=t["bg"])
            theme_label.configure(bg=t["bg"], fg=t["fg"])
            apply_btn.configure(bg=t["btn_bg"], fg=t["btn_fg"])
