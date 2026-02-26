import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os
import subprocess
import json
from datetime import datetime
import sys
import csv

# For PDF export (optional, install reportlab if needed)
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

class UltraDBReportPro:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 ULTRA DB REPORT PRO v4.0")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Variables
        self.settings_file = "db_report_settings.json"
        self.load_settings()
        
        # Apply argument if passed (database path)
        if len(sys.argv) > 1:
            db_path = sys.argv[1]
            if os.path.exists(db_path):
                self.saved_settings["last_db_path"] = db_path
        
        # Styling
        self.setup_styles()
        
        # Color themes (only Light and Blue, with darker buttons)
        self.themes = self.create_themes()
        
        self.current_theme = "light"  # default
        self.db_path = self.saved_settings.get("last_db_path", "")
        
        self.create_widgets()
        self.apply_theme()
        
    def create_themes(self):
        """Create themes (only Light and Blue) with darker buttons"""
        return {
            "light": {
                "bg": "#f5f5f5", "fg": "#000000", "accent": "#007acc",
                "button_bg": "#d0d0d0", "button_fg": "#000000",
                "entry_bg": "#ffffff", "entry_fg": "#000000",
                "frame_bg": "#ffffff", "label_bg": "#f5f5f5",
                "text_bg": "#ffffff", "text_fg": "#000000",
                "hover": "#b0b0b0",
                "warning_bg": "#ff69b4"  # FIX: pink for Re-choose button
            },
            "blue": {
                "bg": "#e6f3ff", "fg": "#003366", "accent": "#0052cc",
                "button_bg": "#99ccff", "button_fg": "#003366",
                "entry_bg": "#ffffff", "entry_fg": "#003366",
                "frame_bg": "#d9ebff", "label_bg": "#e6f3ff",
                "text_bg": "#ffffff", "text_fg": "#003366",
                "hover": "#80b3ff",
                "warning_bg": "#ff69b4"  # FIX: pink for Re-choose button
            }
        }
    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
    def load_settings(self):
        """Load saved settings"""
        self.saved_settings = {
            "rows": "5",
            "mode": "number",
            "separator": "NONE",
            "theme": "light",
            "last_db_path": "",
            "show_tables": True,
            "show_table_names": True,
            "show_statistics": True,
            "show_data_types": True,
            "separate_titles": True,
            "blank_line_after_table_name": True, 
            "window_geometry": ""
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.saved_settings.update(loaded)
            except:
                pass
    
    def save_settings(self):
        """Save current settings"""
        geometry = self.root.geometry()
        
        settings = {
            "rows": self.row_var.get(),
            "mode": self.mode_var.get(),
            "separator": self.sep_var.get(),
            "theme": self.theme_var.get(),
            "last_db_path": self.db_path,
            "show_tables": True,
            "show_table_names": self.show_table_names_var.get(),
            "show_statistics": self.show_statistics_var.get(),
            "show_data_types": self.show_data_types_var.get(),
            "separate_titles": self.separate_titles_var.get(),  # <-- added this line
            "blank_line_after_table_name": self.blank_line_after_table_name_var.get(),  # <-- added this line
            "window_geometry": geometry
        }
        
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
        except:
            pass
    
    def create_widgets(self):
        """Create all UI widgets"""
        # FIX: No top panel with DB label and select button – moved to left panel
        
        # Main area with PanedWindow for resizable left panel
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill="both", expand=True, padx=10, pady=10)  # FIX: reduced padding
        
        # LEFT PANEL - Settings (fixed width, narrower)
        left_frame = tk.Frame(self.paned, width=280)  # FIX: fixed width for narrow menu
        left_frame.pack_propagate(False)  # prevent shrinking
        self.paned.add(left_frame, weight=0)  # weight=0 means fixed size
        
        # ===== DATABASE BLOCK (new) =====
        db_block = tk.LabelFrame(left_frame, text="📁 DATABASE", 
                                font=("Arial", 11, "bold"))
        db_block.pack(fill="x", pady=(0, 10), padx=5)
        
        # Database path label
        self.db_label = tk.Label(db_block, text="No database selected", 
                               font=("Arial", 9), wraplength=250, justify="left")
        self.db_label.pack(pady=5, padx=10, anchor="w")  # FIX: anchor left
        
        # Check DB button (moved here)
        self.check_db_btn = tk.Button(db_block, text="🔍 CHECK DATABASE", 
                                     command=self.check_database,
                                     font=("Arial", 10, "bold"),
                                     height=1)
        self.check_db_btn.pack(pady=5, padx=10, fill="x")  # FIX: fill x for full width
        
        # ===== ROWS BLOCK =====
        block1 = tk.LabelFrame(left_frame, text="📊 ROWS", 
                              font=("Arial", 11, "bold"))
        block1.pack(fill="x", pady=(0, 10), padx=5)
        
        entry_frame = tk.Frame(block1)
        entry_frame.pack(pady=5, padx=10, anchor="w")  # FIX: anchor left
        
        tk.Label(entry_frame, text="Number:", 
                font=("Arial", 10)).pack(side="left", padx=(0, 5))
        
        self.row_var = tk.StringVar(value=self.saved_settings["rows"])
        self.row_entry = tk.Entry(entry_frame, textvariable=self.row_var, 
                                 width=8, font=("Arial", 11), justify="center")
        self.row_entry.pack(side="left")
        
        # Radio buttons
        self.mode_var = tk.StringVar(value=self.saved_settings["mode"]) 
        mode_frame = tk.Frame(block1)
        mode_frame.pack(pady=5, padx=10, anchor="w")  # FIX: anchor left
        
        tk.Radiobutton(mode_frame, text="Specify number", 
                      variable=self.mode_var, value="number",
                      font=("Arial", 10)).pack(anchor="w", pady=2)
        tk.Radiobutton(mode_frame, text="Max (all rows)", 
                      variable=self.mode_var, value="max",
                      font=("Arial", 10)).pack(anchor="w", pady=2)
        
        # ===== TABLE SEPARATORS BLOCK (renamed) =====
        block2 = tk.LabelFrame(left_frame, text="📐 TABLE SEPARATORS", 
                              font=("Arial", 11, "bold"))
        block2.pack(fill="x", pady=(0, 10), padx=5)
        
        self.SEPARATORS = [
            "NONE",
            "BLANK ROW",
            "----------------------------------",
            "__________________________________",
            "==================================",
            "***********************************",
            "###################################",
            "═══════════════════════════════════"
        ]
        
        self.sep_var = tk.StringVar(value=self.saved_settings["separator"])
        sep_combo = ttk.Combobox(block2, textvariable=self.sep_var, 
                                values=self.SEPARATORS, 
                                state="readonly",
                                font=("Arial", 10),
                                width=28)
        sep_combo.pack(pady=5, padx=10, anchor="w")  # FIX: anchor left
        
        # ===== REPORT CONTENT BLOCK =====
        block3 = tk.LabelFrame(left_frame, text="📝 REPORT CONTENT", 
                              font=("Arial", 11, "bold"))
        block3.pack(fill="x", pady=(0, 10), padx=5)
        
        content_frame = tk.Frame(block3)
        content_frame.pack(pady=5, padx=10, anchor="w")  # FIX: anchor left
        
        # Show tables (always checked, disabled)
        self.show_tables_var = tk.BooleanVar(value=True)
        tk.Checkbutton(content_frame, text="Show tables (always)", 
                      variable=self.show_tables_var,
                      state="disabled",
                      font=("Arial", 10)).pack(anchor="w", pady=2)
        
        # New option: Separate titles (adds extra line before each table title for better readability)
        self.separate_titles_var = tk.BooleanVar(value=self.saved_settings.get("separate_titles", True))
        tk.Checkbutton(content_frame, text="Separate titles (---- line)", 
                      variable=self.separate_titles_var,
                      font=("Arial", 10)).pack(anchor="w", pady=2)
        
        # Show table names report content (optional)
        self.show_table_names_var = tk.BooleanVar(value=self.saved_settings["show_table_names"])
        tk.Checkbutton(content_frame, text="Show table names", 
                      variable=self.show_table_names_var,
                      font=("Arial", 10)).pack(anchor="w", pady=2)
        
        # blank line after table name (adds an empty line after the table name for better readability)
        self.blank_line_after_table_name_var = tk.BooleanVar(value=self.saved_settings.get("blank_line_after_table_name", True))
        tk.Checkbutton(content_frame, text="Blank line after table name", 
                      variable=self.blank_line_after_table_name_var,
                      font=("Arial", 10)).pack(anchor="w", pady=2)
        
        # Show statistics (shortened)
        self.show_statistics_var = tk.BooleanVar(value=self.saved_settings["show_statistics"])
        tk.Checkbutton(content_frame, text="Show statistics",  # FIX: shortened
                      variable=self.show_statistics_var,
                      font=("Arial", 10)).pack(anchor="w", pady=2)
        
        # Show data types in header
        self.show_data_types_var = tk.BooleanVar(value=self.saved_settings["show_data_types"])
        tk.Checkbutton(content_frame, text="Show data types in column headers", 
                      variable=self.show_data_types_var,
                      font=("Arial", 10)).pack(anchor="w", pady=2)
        
        # ===== THEME BLOCK =====
        block4 = tk.LabelFrame(left_frame, text="🎨 THEME", 
                              font=("Arial", 11, "bold"))
        block4.pack(fill="x", pady=(0, 10), padx=5)
        
        themes_frame = tk.Frame(block4)
        themes_frame.pack(pady=5, padx=10, anchor="w")  # FIX: anchor left
        
        self.theme_var = tk.StringVar(value=self.saved_settings["theme"])
        colors = ["light", "blue"]
        color_names = {"light": "☀️ Light", "blue": "🔵 Blue"}
        
        for color in colors:
            btn = tk.Radiobutton(themes_frame, text=color_names[color],
                               variable=self.theme_var, value=color,
                               command=self.apply_theme,
                               font=("Arial", 10))
            btn.pack(anchor="w", pady=2)  # FIX: pack left-aligned
        
        # ===== ACTION BUTTONS =====
        block5 = tk.LabelFrame(left_frame, text="🎯 ACTIONS", 
                              font=("Arial", 11, "bold"))
        block5.pack(fill="x", pady=(0, 10), padx=5)
        
        button_frame = tk.Frame(block5)
        button_frame.pack(pady=10, padx=10, fill="x")
        
        button_font = ("Arial", 11, "bold")  # slightly smaller
        btn_width = 22
        
        # Update button
        self.update_btn = tk.Button(button_frame, text="🔄 UPDATE", 
                                   command=self.do_update,
                                   font=button_font,
                                   height=1, width=btn_width)
        self.update_btn.pack(pady=3)
        
        # Check DB button was moved to Database block, so remove from here
        
        # Save As button
        self.save_as_btn = tk.Button(button_frame, text="💾 SAVE AS TXT or CSV", 
                                    command=self.show_save_as_menu,
                                    font=button_font,
                                    height=1, width=btn_width)
        self.save_as_btn.pack(pady=3)
        
        # Print  to PDF button
        self.print_btn = tk.Button(button_frame, text="🖨️ PRINT TO PDF", 
                                  command=self.print_to_pdf,
                                  font=button_font,
                                  height=1, width=btn_width)
        self.print_btn.pack(pady=3)
        
        # Re-choose database button (pink)
        self.rechoose_btn = tk.Button(button_frame, text="📂 RE-CHOOSE DATABASE", 
                                     command=self.confirm_rechoose_db,
                                     font=button_font,
                                     height=1, width=btn_width,
                                     bg="#ff69b4", fg="black")  # FIX: pink background
        self.rechoose_btn.pack(pady=3)
        
        # Return button
        self.return_btn = tk.Button(button_frame, text="🔙 RETURN TO VIEWER", 
                                   command=self.return_to_viewer,
                                   font=button_font,
                                   height=1, width=btn_width)
        self.return_btn.pack(pady=3)
        
        # RIGHT PANEL - Preview
        right_frame = tk.Frame(self.paned)
        self.paned.add(right_frame, weight=3)
        
        text_frame = tk.LabelFrame(right_frame, text="📄 PREVIEW", 
                                  font=("Arial", 11, "bold"))
        text_frame.pack(fill="both", expand=True)
        

        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        self.text_area = tk.Text(text_frame, 
                                 font=("Courier New", 10),
                                 wrap="none",
                                 undo=True)
        self.text_area.grid(row=0, column=0, sticky="nsew")
        

        v_scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=self.text_area.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.text_area.config(yscrollcommand=v_scrollbar.set)
        

        h_scrollbar = tk.Scrollbar(text_frame, orient="horizontal", command=self.text_area.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.text_area.config(xscrollcommand=h_scrollbar.set)
        
        # Context menu
        self.create_context_menu()
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="✅ Ready...", 
                                  bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                  font=("Arial", 9))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Key bindings
        self.setup_bindings()
        
        # Auto-load database if exists
        if self.db_path and os.path.exists(self.db_path):
            self.update_status(f"Database loaded: {os.path.basename(self.db_path)}")
            self.db_label.config(text=f"📁 {os.path.basename(self.db_path)}", fg="green")
    
    def create_context_menu(self):
        """Create context menu for text area"""
        self.context_menu = tk.Menu(self.text_area, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_text)
        self.context_menu.add_command(label="Paste", command=self.paste_text)
        self.context_menu.add_command(label="Select All", command=self.select_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Clear", command=self.clear_text)
        
        self.text_area.bind("<Button-3>", self.show_context_menu)
    
    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)
    
    def copy_text(self):
        try:
            text = self.text_area.get("sel.first", "sel.last")
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
        except:
            pass
    
    def paste_text(self):
        try:
            text = self.root.clipboard_get()
            self.text_area.insert("insert", text)
        except:
            pass
    
    def select_all(self):
        self.text_area.tag_add("sel", "1.0", "end")
    
    def clear_text(self):
        self.text_area.delete("1.0", tk.END)
    
    def setup_bindings(self):
        """Hotkey bindings"""
        self.root.bind('<Return>', lambda e: self.do_update())
        self.root.bind('<Control-s>', lambda e: self.show_save_as_menu())
        self.root.bind('<Control-p>', lambda e: self.print_report())
        self.root.bind('<Control-q>', lambda e: self.return_to_viewer())
        self.root.bind('<Control-o>', lambda e: self.select_db_direct())
        self.root.bind('<F1>', lambda e: self.show_help())
    
    def show_help(self):
        help_text = """🚀 ULTRA DB REPORT PRO v4.0

Hotkeys:
• Ctrl+P / Enter - Update preview
• Ctrl+S - Save As menu
• Ctrl+O - Select database
• Ctrl+Q - Return to Viewer
• F1 - Help

Report Content:
• Tables are always shown
• Table names, statistics, data types are optional

Export formats:
• TXT - Plain text
• CSV - Comma separated values
• PDF - Portable Document Format (requires reportlab)"""
        messagebox.showinfo("Help", help_text)
    
    def confirm_rechoose_db(self):
        """Confirm before re-selecting database"""
        if messagebox.askyesno("Confirm", "Are you sure you want to select another database?"):
            self.select_db_direct()
    
    def select_db_direct(self):
        """Direct database selection without confirmation"""
        path = filedialog.askopenfilename(
            title="Select Database File",
            filetypes=[("SQLite DB", "*.db *.sqlite *.sqlite3"), ("All files", "*.*")]
        )
        if path:
            self.db_path = path
            self.db_label.config(text=f"📁 {os.path.basename(path)}", fg="green")
            self.update_status(f"Database selected: {os.path.basename(path)}")
            self.save_settings()
            # Auto-update preview
            self.do_update()
    
    def update_status(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_bar.config(text=f"[{timestamp}] {message}")
        self.root.update()
    
    def apply_theme(self):
        """Apply selected theme"""
        self.current_theme = self.theme_var.get()
        theme = self.themes[self.current_theme]
        self.save_settings()
        
        # Apply to root
        self.root.config(bg=theme["bg"])
        
        # Apply to all widgets recursively
        self.apply_theme_recursive(self.root, theme)
        
        # Special for text area
        self.text_area.config(bg=theme["text_bg"], fg=theme["text_fg"],
                            insertbackground=theme["fg"])
        self.status_bar.config(bg=theme["accent"], fg="white")
        
        # FIX: Re-choose button stays pink regardless of theme
        self.rechoose_btn.config(bg="#ff69b4", fg="black")
    
    def apply_theme_recursive(self, widget, theme):
        """Recursively apply theme to widgets"""
        try:
            widget_type = str(widget.winfo_class())
            
            if widget_type in ("Frame", "Labelframe", "LabelFrame", "TFrame"):
                widget.config(bg=theme["frame_bg"])
            elif widget_type == "Label":
                widget.config(bg=theme["label_bg"], fg=theme["fg"])
            elif widget_type == "Button":
                # Skip rechoose button to keep it pink
                if widget != self.rechoose_btn:
                    widget.config(bg=theme["button_bg"], fg=theme["button_fg"],
                                activebackground=theme["hover"])
            elif widget_type == "Entry":
                widget.config(bg=theme["entry_bg"], fg=theme["entry_fg"],
                            insertbackground=theme["fg"])
            elif widget_type in ("Radiobutton", "Checkbutton"):
                widget.config(bg=theme["label_bg"], fg=theme["fg"])
        except:
            pass
        
        for child in widget.winfo_children():
            self.apply_theme_recursive(child, theme)
    
    def check_database(self):
        """Check database integrity"""
        if not self.db_path:
            messagebox.showwarning("Warning", "Select a database first!")
            return
        
        try:
            self.update_status("Checking database...")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            tables = cursor.fetchall()
            
            if not tables:
                messagebox.showwarning("DB Check", "Database contains no tables!")
                conn.close()
                return
            
            result_lines = []
            result_lines.append(f"🔍 DATABASE CHECK: {os.path.basename(self.db_path)}")
            result_lines.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            result_lines.append("")
            result_lines.append(f"📊 Total tables: {len(tables)}")
            
            total_rows = 0
            for table_name, in tables:
                cursor.execute(f"SELECT COUNT(*) FROM \"{table_name}\"")
                row_count = cursor.fetchone()[0]
                total_rows += row_count
                
                cursor.execute(f"PRAGMA table_info(\"{table_name}\")")
                columns = cursor.fetchall()
                result_lines.append(f"   • {table_name}: {row_count} rows, {len(columns)} columns")
            
            result_lines.append("")
            result_lines.append(f"📈 Total rows in database: {total_rows}")
            
            # Integrity check
            cursor.execute("PRAGMA integrity_check;")
            integrity = cursor.fetchone()[0]
            result_lines.append(f"✅ Integrity: {integrity}")
            
            conn.close()
            
            # Show results in a new window
            self.show_check_results(result_lines)
            
        except Exception as e:
            messagebox.showerror("Error", f"Database check failed:\n{str(e)}")
    
    def show_check_results(self, lines):
        """Show database check results in a separate window"""
        result_window = tk.Toplevel(self.root)
        result_window.title("Database Check Results")
        result_window.geometry("600x500")
        
        text_area = scrolledtext.ScrolledText(result_window, wrap="word", 
                                            font=("Courier New", 10))
        text_area.pack(fill="both", expand=True, padx=10, pady=10)
        text_area.insert("1.0", "\n".join(lines))
        text_area.config(state="disabled")
        
        tk.Button(result_window, text="OK", command=result_window.destroy,
                 font=("Arial", 10, "bold")).pack(pady=10)
        
        self.apply_theme_recursive(result_window, self.themes[self.current_theme])
    
    def do_update(self):
        """Generate preview"""
        if not self.db_path:
            messagebox.showwarning("Warning", "Select a database first!")
            return
        
        try:
            self.update_status("Generating preview...")
            
            if self.mode_var.get() == "max":
                row_count = "max"
            else:
                try:
                    row_count = int(self.row_var.get())
                    if row_count <= 0:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Error", "Enter a valid number!")
                    return
            
            separator = self.sep_var.get()
            report = self.generate_report(row_count, separator)
            
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, report)
            
            self.update_status("Preview generated successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate preview:\n{str(e)}")
    
    def generate_report(self, row_count, separator):
        """Generate report based on user settings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        
        report_lines = []
        total_tables = len(tables)
        
        for i, (table_name,) in enumerate(tables, 1):
            # Table name (optional)
            if self.show_table_names_var.get():
                report_lines.append(f"TABLE {i}/{total_tables}: {table_name}")
                # Blank line after table name (optional)
                if self.blank_line_after_table_name_var.get():
                    report_lines.append("")
            
            # Get column info for data types
            cursor.execute(f"PRAGMA table_info(\"{table_name}\")")
            col_info = cursor.fetchall()
            col_names = [col[1] for col in col_info]
            col_types = [col[2] for col in col_info]
            
            # Get data
            if row_count == "max":
                cursor.execute(f"SELECT * FROM \"{table_name}\"")
            else:
                cursor.execute(f"SELECT * FROM \"{table_name}\" LIMIT {row_count}")
            rows = cursor.fetchall()
            
            # Build header with optional data types
            header_parts = []
            for idx, name in enumerate(col_names):
                if self.show_data_types_var.get():
                    header_parts.append(f"{name} ({col_types[idx]})")
                else:
                    header_parts.append(name)
            
            # Calculate column widths for alignment
            col_widths = []
            for idx, name in enumerate(header_parts):
                max_width = len(name)
                for row in rows:
                    val = str(row[idx]) if row[idx] is not None else "NULL"
                    max_width = max(max_width, len(val))
                col_widths.append(min(max_width, 50))
            
            # Create header line
            header_line = " | ".join(name.ljust(col_widths[idx]) for idx, name in enumerate(header_parts))
            report_lines.append(header_line)
            
            # Add separator line only if enabled
            if self.separate_titles_var.get():
                report_lines.append("-" * len(header_line))
            
            # Data rows
            for row in rows:
                row_parts = []
                for idx, val in enumerate(row):
                    val_str = str(val) if val is not None else "NULL"
                    row_parts.append(val_str.ljust(col_widths[idx]))
                report_lines.append(" | ".join(row_parts))
            
            # Statistics (optional)
            if self.show_statistics_var.get():
                report_lines.append("")
                report_lines.append(f"📊 Statistics for '{table_name}':")
                
                # Get actual total rows
                cursor.execute(f"SELECT COUNT(*) FROM \"{table_name}\"")
                total_rows = cursor.fetchone()[0]
                report_lines.append(f"   • Total rows: {total_rows} (showing {row_count if row_count != 'max' else 'all'})")
                report_lines.append(f"   • Columns: {len(col_names)}")
                
                # Min/max for numeric columns
                for idx, (name, col_type) in enumerate(zip(col_names, col_types)):
                    if col_type.upper() in ('INTEGER', 'REAL', 'NUMERIC'):
                        try:
                            cursor.execute(f"SELECT MIN(\"{name}\"), MAX(\"{name}\") FROM \"{table_name}\"")
                            min_val, max_val = cursor.fetchone()
                            if min_val is not None:
                                report_lines.append(f"   • {name}: min={min_val}, max={max_val}")
                        except:
                            pass
                
                # NULL count
                for idx, name in enumerate(col_names):
                    cursor.execute(f"SELECT COUNT(*) FROM \"{table_name}\" WHERE \"{name}\" IS NULL")
                    null_count = cursor.fetchone()[0]
                    if null_count > 0:
                        report_lines.append(f"   • {name}: {null_count} NULL values")
            
            # Separator (if not last table)
            if separator != "NONE" and i < total_tables:
                if separator == "blank row":
                    # Just add one blank line
                    report_lines.append("")
                else:
                    # Add separator line with blank lines around
                    report_lines.append("")
                    report_lines.append(separator)
                    report_lines.append("")
        
        conn.close()
        return "\n".join(report_lines)
    
    def show_save_as_menu(self):
        """Show popup menu for Save As options (TXT and CSV only)"""
        if not self.text_area.get("1.0", "end-1c").strip():
            messagebox.showwarning("Warning", "Generate a report first!")
            return
            
        popup = tk.Menu(self.root, tearoff=0)
        popup.add_command(label="TXT file", command=self.save_as_txt)
        popup.add_command(label="CSV file", command=self.save_as_csv)
        popup.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
    
    def pdf_not_available(self):
        messagebox.showinfo("Info", "PDF export requires reportlab library.\nInstall with: pip install reportlab")
    
    def save_as_txt(self):
        file_path = filedialog.asksaveasfilename(
            title="Save as TXT",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.text_area.get("1.0", tk.END))
                self.update_status(f"Saved as TXT: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", f"Report saved as TXT:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save:\n{str(e)}")
    
    def save_as_csv(self):
        file_path = filedialog.asksaveasfilename(
            title="Save as CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        if file_path:
            try:
                content = self.text_area.get("1.0", tk.END).strip()
                with open(file_path, "w", encoding="utf-8", newline='') as f:
                    writer = csv.writer(f)
                    for line in content.split('\n'):
                        if line and not line.startswith(('-', '=', '*', '#')):
                            writer.writerow([line])
                self.update_status(f"Saved as CSV: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", f"Report saved as CSV:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save:\n{str(e)}")
    
    def return_to_viewer(self):
        """Close window and return to Database Viewer"""
        self.save_settings()
        self.root.quit()
    
    def run(self):
        """Start the application"""
        if self.saved_settings.get("window_geometry"):
            try:
                self.root.geometry(self.saved_settings["window_geometry"])
            except:
                pass
        self.root.mainloop()

    def print_to_pdf(self):
        """Print report directly to PDF file"""
        if not self.text_area.get("1.0", "end-1c").strip():
            messagebox.showwarning("Warning", "Generate a report first!")
            return
        
        # Ask for PDF file location
        file_path = filedialog.asksaveasfilename(
            title="Save PDF as...",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        
        if not file_path:
            return
        
        try:
            content = self.text_area.get("1.0", tk.END).strip()
            
            # Try to use reportlab if available
            try:
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import A4
                from reportlab.lib.units import inch
                
                c = canvas.Canvas(file_path, pagesize=A4)
                width, height = A4
                y = height - 40
                x = 40
                line_height = 12
                
                for line in content.split('\n'):
                    if y < 40:
                        c.showPage()
                        y = height - 40
                    c.setFont("Courier", 8)
                    # Split long lines
                    if len(line) > 100:
                        line = line[:100] + "..."
                    c.drawString(x, y, line)
                    y -= line_height
                
                c.save()
                self.update_status(f"PDF saved: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", f"PDF saved successfully:\n{file_path}")
                
                # Ask if user wants to open the PDF
                if messagebox.askyesno("Open PDF", "Open the PDF file now?"):
                    self.open_file(file_path)
                    
            except ImportError:
                # Fallback to simple text-to-PDF using system print
                messagebox.showinfo("Info", "reportlab not installed. Using system print dialog...")
                # Save as text and print using system's PDF printer
                temp_file = file_path.replace('.pdf', '.txt')
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(content)
                
                if os.name == 'nt':  # Windows
                    # Try to use Microsoft Print to PDF if available
                    os.startfile(temp_file, "print")
                else:
                    subprocess.run(["lp", "-d", "PDF", temp_file])
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create PDF:\n{str(e)}")

    def open_file(self, filepath):
        """Open file with default application"""
        try:
            if os.name == 'nt':
                os.startfile(filepath)
            elif os.name == 'posix':
                subprocess.call(('open', filepath) if sys.platform == 'darwin' 
                              else ('xdg-open', filepath))
        except:
            pass
    

if __name__ == "__main__":
    app = UltraDBReportPro()
    app.run()