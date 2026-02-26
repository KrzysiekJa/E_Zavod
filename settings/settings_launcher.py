#!/usr/bin/env python3
"""
Settings Launcher for E-Zavod Simulator
Central configuration and settings management
"""
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTabWidget, QGroupBox, QCheckBox,
    QSpinBox, QComboBox, QLineEdit, QMessageBox, QFileDialog,
    QListWidget, QListWidgetItem, QSplitter, QFrame, QScrollArea,
    QColorDialog, QFontDialog, QSlider
)
from PyQt6.QtGui import QIcon, QPixmap, QFont, QColor
from PyQt6.QtCore import Qt, QSettings, QTimer


class SettingsLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings_file = Path(__file__).parent / "simulator_settings.json"
        self.load_settings()
        self.init_ui()
        
    def init_ui(self):
        """Interface"""
        self.setWindowTitle("⚙ E-Zavod Simulator Settings")
        self.setGeometry(100, 100, 1000, 700)
        
        # Icone
        icon_path = Path(__file__).parent.parent / "icone.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("⚙ Simulator Settings")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #4A148C;
                padding: 20px;
                background: #f3e5f5;
                border-radius: 10px;
                margin: 10px;
            }
        """)
        main_layout.addWidget(title)
        
        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #ce93d8;
                border-radius: 10px;
                padding: 10px;
            }
            QTabBar::tab {
                background: #e1bee7;
                padding: 10px 20px;
                margin: 2px;
                border-radius: 5px;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background: #ba68c8;
                color: white;
            }
        """)
        
        # Tabs #2
        tabs.addTab(self.create_general_tab(), "🔧 General")
        tabs.addTab(self.create_database_tab(), "🗄 Database")
        tabs.addTab(self.create_simulator_tab(), "🏭 Simulator")
        tabs.addTab(self.create_interface_tab(), "🎨 Interface")
        tabs.addTab(self.create_modules_tab(), "📦 Modules")
        tabs.addTab(self.create_paths_tab(), "📁 Paths")
        tabs.addTab(self.create_advanced_tab(), "⚡ Advanced")
        
        main_layout.addWidget(tabs)
        
        # Buttons below
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #45a049;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        
        apply_btn = QPushButton("🔄 Apply Now")
        apply_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                font-size: 16px;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1e88e5;
            }
        """)
        apply_btn.clicked.connect(self.apply_settings)
        
        reset_btn = QPushButton("↺ Reset to Default")
        reset_btn.setStyleSheet("""
            QPushButton {
                background: #FF9800;
                color: white;
                font-size: 16px;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #fb8c00;
            }
        """)
        reset_btn.clicked.connect(self.reset_settings)
        
        close_btn = QPushButton("✖ Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background: #f44336;
                color: white;
                font-size: 16px;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #d32f2f;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666;
                padding: 5px;
                border-top: 1px solid #ce93d8;
                margin-top: 10px;
            }
        """)
        main_layout.addWidget(self.status_label)
        
    def create_general_tab(self):
        """Main options"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Language
        lang_group = QGroupBox("Language / Мова")
        lang_layout = QHBoxLayout()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Українська", "Dojcz"])
        self.lang_combo.setCurrentText(self.settings.get("language", "English"))
        lang_layout.addWidget(QLabel("Interface Language:"))
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        lang_group.setLayout(lang_layout)
        
        # Auto initiating
        auto_group = QGroupBox("Startup")
        auto_layout = QVBoxLayout()
        self.auto_check = QCheckBox("Auto-load last project on startup")
        self.auto_check.setChecked(self.settings.get("auto_load_last", True))
        auto_layout.addWidget(self.auto_check)
        
        self.auto_save = QCheckBox("Auto-save settings on exit")
        self.auto_save.setChecked(self.settings.get("auto_save", True))
        auto_layout.addWidget(self.auto_save)
        auto_group.setLayout(auto_layout)
        
        layout.addWidget(lang_group)
        layout.addWidget(auto_group)
        layout.addStretch()
        
        return tab
    
    def create_database_tab(self):
        """Database options"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Type of DB
        db_type_group = QGroupBox("Database Type")
        db_type_layout = QHBoxLayout()
        self.db_type_combo = QComboBox()
        self.db_type_combo.addItems(["SQLite", "MySQL", "PostgreSQL", "MongoDB"])
        self.db_type_combo.setCurrentText(self.settings.get("database_type", "SQLite"))
        db_type_layout.addWidget(QLabel("Database Engine:"))
        db_type_layout.addWidget(self.db_type_combo)
        db_type_group.setLayout(db_type_layout)
        
        # Way to DB
        db_path_group = QGroupBox("Database Location")
        db_path_layout = QHBoxLayout()
        self.db_path_edit = QLineEdit()
        self.db_path_edit.setText(self.settings.get("database_path", "data/simulator.db"))
        db_path_layout.addWidget(self.db_path_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_db_path)
        db_path_layout.addWidget(browse_btn)
        db_path_group.setLayout(db_path_layout)
        
        # Options of DB
        db_opts_group = QGroupBox("Database Options")
        db_opts_layout = QVBoxLayout()
        
        self.backup_check = QCheckBox("Auto-backup database")
        self.backup_check.setChecked(self.settings.get("auto_backup", True))
        db_opts_layout.addWidget(self.backup_check)
        
        backup_layout = QHBoxLayout()
        backup_layout.addWidget(QLabel("Backup interval (minutes):"))
        self.backup_spin = QSpinBox()
        self.backup_spin.setRange(1, 1440)
        self.backup_spin.setValue(self.settings.get("backup_interval", 60))
        backup_layout.addWidget(self.backup_spin)
        backup_layout.addStretch()
        db_opts_layout.addLayout(backup_layout)
        
        db_opts_group.setLayout(db_opts_layout)
        
        layout.addWidget(db_type_group)
        layout.addWidget(db_path_group)
        layout.addWidget(db_opts_group)
        layout.addStretch()
        
        return tab
    
    def create_simulator_tab(self):
        """Simulatior options"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        sim_group = QGroupBox("Simulation Parameters")
        sim_layout = QVBoxLayout()
        
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Time step (seconds):"))
        self.time_step = QSpinBox()
        self.time_step.setRange(1, 3600)
        self.time_step.setValue(self.settings.get("time_step", 60))
        time_layout.addWidget(self.time_step)
        time_layout.addStretch()
        sim_layout.addLayout(time_layout)
        
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Simulation speed:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(self.settings.get("sim_speed", 50))
        speed_layout.addWidget(self.speed_slider)
        self.speed_label = QLabel(f"{self.speed_slider.value()}%")
        speed_layout.addWidget(self.speed_label)
        self.speed_slider.valueChanged.connect(lambda v: self.speed_label.setText(f"{v}%"))
        sim_layout.addLayout(speed_layout)
        
        sim_group.setLayout(sim_layout)
        
        # restrictions
        limits_group = QGroupBox("Limits")
        limits_layout = QVBoxLayout()
        
        max_units = QHBoxLayout()
        max_units.addWidget(QLabel("Max units:"))
        self.max_units_spin = QSpinBox()
        self.max_units_spin.setRange(1, 1000000)
        self.max_units_spin.setValue(self.settings.get("max_units", 10000))
        max_units.addWidget(self.max_units_spin)
        max_units.addStretch()
        limits_layout.addLayout(max_units)
        
        limits_group.setLayout(limits_layout)
        
        layout.addWidget(sim_group)
        layout.addWidget(limits_group)
        layout.addStretch()
        
        return tab
    
    def create_interface_tab(self):
        """Налаштування інтерфейсу"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Theme
        theme_group = QGroupBox("Theme")
        theme_layout = QHBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Purple", "Blue", "System"])
        self.theme_combo.setCurrentText(self.settings.get("theme", "Purple"))
        theme_layout.addWidget(QLabel("Color theme:"))
        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)
        
        # Fonts
        font_group = QGroupBox("Fonts")
        font_layout = QVBoxLayout()
        
        font_btn = QPushButton("Select Font...")
        font_btn.clicked.connect(self.select_font)
        font_layout.addWidget(font_btn)
        
        self.font_label = QLabel(f"Current: {self.settings.get('font', 'Arial, 10pt')}")
        font_layout.addWidget(self.font_label)
        
        font_group.setLayout(font_layout)
        
        layout.addWidget(theme_group)
        layout.addWidget(font_group)
        layout.addStretch()
        
        return tab
    
    def create_modules_tab(self):
        """Simulator Modules"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        modules_group = QGroupBox("Enabled Modules")
        modules_layout = QVBoxLayout()
        
        self.modules_list = QListWidget()
        modules = {
            "Database Viewer": True,
            "Database Editor": True,
            "Checker": True,
            "Reports Generator": False,
            "Analytics": False,
            "User Management": False,
            "Factory Simulator": True,
            "Network Module": False,
            "API Interface": False,
            "Export/Import": True
        }
        
        saved_modules = self.settings.get("modules", {})
        
        for module, default in modules.items():
            item = QListWidgetItem(module)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            checked = saved_modules.get(module, default)
            item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
            self.modules_list.addItem(item)
        
        modules_layout.addWidget(self.modules_list)
        modules_group.setLayout(modules_layout)
        
        layout.addWidget(modules_group)
        
        return tab
    
    def create_paths_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        paths = [
            ("Data directory:", "data_path", "data"),
            ("Logs directory:", "logs_path", "logs"),
            ("Backup directory:", "backup_path", "backups"),
            ("Reports directory:", "reports_path", "reports"),
            ("Config directory:", "config_path", "config"),
            ("Temp directory:", "temp_path", "temp")
        ]
        
        self.path_edits = {}
        
        for label, key, default in paths:
            group = QGroupBox(label)
            group_layout = QHBoxLayout()
            
            edit = QLineEdit()
            edit.setText(self.settings.get(key, default))
            self.path_edits[key] = edit
            
            browse_btn = QPushButton("Browse...")
            browse_btn.clicked.connect(lambda checked, k=key: self.browse_path(k))
            
            group_layout.addWidget(edit)
            group_layout.addWidget(browse_btn)
            group.setLayout(group_layout)
            layout.addWidget(group)
        
        layout.addStretch()
        return tab
    
    def create_advanced_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Логування
        log_group = QGroupBox("Logging")
        log_layout = QVBoxLayout()
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_combo.setCurrentText(self.settings.get("log_level", "INFO"))
        log_layout.addWidget(QLabel("Log level:"))
        log_layout.addWidget(self.log_level_combo)
        
        self.log_to_file = QCheckBox("Save logs to file")
        self.log_to_file.setChecked(self.settings.get("log_to_file", True))
        log_layout.addWidget(self.log_to_file)
        
        log_group.setLayout(log_layout)
        
        # Perfomance
        perf_group = QGroupBox("Performance")
        perf_layout = QVBoxLayout()
        
        self.multithreading = QCheckBox("Enable multithreading")
        self.multithreading.setChecked(self.settings.get("multithreading", True))
        perf_layout.addWidget(self.multithreading)
        
        cache_layout = QHBoxLayout()
        cache_layout.addWidget(QLabel("Cache size (MB):"))
        self.cache_spin = QSpinBox()
        self.cache_spin.setRange(10, 10000)
        self.cache_spin.setValue(self.settings.get("cache_size", 500))
        cache_layout.addWidget(self.cache_spin)
        cache_layout.addStretch()
        perf_layout.addLayout(cache_layout)
        
        perf_group.setLayout(perf_layout)
        
        layout.addWidget(log_group)
        layout.addWidget(perf_group)
        layout.addStretch()
        
        return tab
    
    def browse_db_path(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Select Database File", 
            self.db_path_edit.text(),
            "Database files (*.db *.sqlite *.sqlite3);;All files (*.*)"
        )
        if path:
            self.db_path_edit.setText(path)
    
    def browse_path(self, key):
        path = QFileDialog.getExistingDirectory(
            self, f"Select {key} directory",
            self.path_edits[key].text()
        )
        if path:
            self.path_edits[key].setText(path)
    
    def select_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.settings["font"] = f"{font.family()}, {font.pointSize()}pt"
            self.font_label.setText(f"Current: {self.settings['font']}")
    
    def load_settings(self):
        default_settings = {
            "language": "English",
            "auto_load_last": True,
            "auto_save": True,
            "database_type": "SQLite",
            "database_path": "data/simulator.db",
            "auto_backup": True,
            "backup_interval": 60,
            "time_step": 60,
            "sim_speed": 50,
            "max_units": 10000,
            "theme": "Purple",
            "font": "Arial, 10pt",
            "log_level": "INFO",
            "log_to_file": True,
            "multithreading": True,
            "cache_size": 500,
            "data_path": "data",
            "logs_path": "logs",
            "backup_path": "backups",
            "reports_path": "reports",
            "config_path": "config",
            "temp_path": "temp",
            "modules": {
                "Database Viewer": True,
                "Database Editor": True,
                "Checker": True,
                "Reports Generator": False,
                "Analytics": False,
                "User Management": False,
                "Factory Simulator": True,
                "Network Module": False,
                "API Interface": False,
                "Export/Import": True
            }
        }
        
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.settings = {**default_settings, **loaded}
            except:
                self.settings = default_settings
        else:
            self.settings = default_settings
    
    def save_settings(self):
        self.update_settings_from_ui()
        
        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            
            self.status_label.setText(f"✅ Settings saved at {datetime.now().strftime('%H:%M:%S')}")
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save settings:\n{str(e)}")
    
    def update_settings_from_ui(self):
        # General
        self.settings["language"] = self.lang_combo.currentText()
        self.settings["auto_load_last"] = self.auto_check.isChecked()
        self.settings["auto_save"] = self.auto_save.isChecked()
        
        # Database
        self.settings["database_type"] = self.db_type_combo.currentText()
        self.settings["database_path"] = self.db_path_edit.text()
        self.settings["auto_backup"] = self.backup_check.isChecked()
        self.settings["backup_interval"] = self.backup_spin.value()
        
        # Simulator
        self.settings["time_step"] = self.time_step.value()
        self.settings["sim_speed"] = self.speed_slider.value()
        self.settings["max_units"] = self.max_units_spin.value()
        
        # Interface
        self.settings["theme"] = self.theme_combo.currentText()
        
        # Modules
        modules = {}
        for i in range(self.modules_list.count()):
            item = self.modules_list.item(i)
            modules[item.text()] = (item.checkState() == Qt.CheckState.Checked)
        self.settings["modules"] = modules
        
        # Paths
        for key, edit in self.path_edits.items():
            self.settings[key] = edit.text()
        
        # Advanced
        self.settings["log_level"] = self.log_level_combo.currentText()
        self.settings["log_to_file"] = self.log_to_file.isChecked()
        self.settings["multithreading"] = self.multithreading.isChecked()
        self.settings["cache_size"] = self.cache_spin.value()
    
    def apply_settings(self):
        self.update_settings_from_ui()
        self.status_label.setText(f"🔄 Settings applied at {datetime.now().strftime('%H:%M:%S')}")
        QMessageBox.information(self, "Applied", "Settings applied to current session!")
    
    def reset_settings(self):
        reply = QMessageBox.question(
            self, "Confirm Reset",
            "Are you sure you want to reset all settings to default?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings_file.unlink(missing_ok=True)
            self.load_settings()
            self.close()
            subprocess.Popen([sys.executable, __file__])
            self.close()


def main():
    app = QApplication(sys.argv)
    
    app.setStyle('Fusion')
    
    window = SettingsLauncher()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()