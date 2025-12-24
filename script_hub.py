#!/usr/bin/env python3
"""
Script Hub - A central launcher for PowerShell and Batch scripts
Uses CustomTkinter for a modern dark-themed GUI
"""

import customtkinter as ctk
import os
import subprocess
import json
import platform
from pathlib import Path
from tkinter import filedialog, messagebox
import threading
from datetime import datetime

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ScriptHub(ctk.CTk):
    """Main application window for Script Hub"""

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("Script Hub - Central Script Launcher")
        self.geometry("1200x800")
        self.minsize(900, 600)

        # Configuration
        self.scripts_folder = None
        self.scripts = {}  # category -> list of scripts
        self.current_working_dir = os.getcwd()
        self.config_file = Path.home() / ".script_hub_config.json"
        self.output_history = []

        # Load saved configuration
        self.load_config()

        # Create UI
        self.create_widgets()

        # Load scripts if folder is set
        if self.scripts_folder and os.path.exists(self.scripts_folder):
            self.scan_scripts()

    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.scripts_folder = config.get('scripts_folder')
                    self.current_working_dir = config.get('working_dir', os.getcwd())
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self):
        """Save configuration to file"""
        try:
            config = {
                'scripts_folder': self.scripts_folder,
                'working_dir': self.current_working_dir
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def create_widgets(self):
        """Create all UI widgets"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left sidebar
        self.create_sidebar()

        # Main content area
        self.create_main_area()

        # Bottom output panel
        self.create_output_panel()

    def create_sidebar(self):
        """Create the left sidebar with categories and controls"""
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        # App title
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="Script Hub",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Scripts folder selection
        self.folder_frame = ctk.CTkFrame(self.sidebar)
        self.folder_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.folder_label = ctk.CTkLabel(
            self.folder_frame,
            text="Scripts Folder:",
            font=ctk.CTkFont(size=12)
        )
        self.folder_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.folder_path_label = ctk.CTkLabel(
            self.folder_frame,
            text=self.scripts_folder or "Not set",
            font=ctk.CTkFont(size=10),
            wraplength=240
        )
        self.folder_path_label.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")

        self.browse_btn = ctk.CTkButton(
            self.folder_frame,
            text="Browse Scripts Folder",
            command=self.browse_scripts_folder,
            height=32
        )
        self.browse_btn.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")

        # Working directory
        self.workdir_frame = ctk.CTkFrame(self.sidebar)
        self.workdir_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.workdir_label = ctk.CTkLabel(
            self.workdir_frame,
            text="Working Directory:",
            font=ctk.CTkFont(size=12)
        )
        self.workdir_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.workdir_path_label = ctk.CTkLabel(
            self.workdir_frame,
            text=self.current_working_dir,
            font=ctk.CTkFont(size=10),
            wraplength=240
        )
        self.workdir_path_label.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")

        self.workdir_btn = ctk.CTkButton(
            self.workdir_frame,
            text="Change Working Dir",
            command=self.browse_working_dir,
            height=32
        )
        self.workdir_btn.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")

        # Search box
        self.search_var = ctk.StringVar()
        self.search_var.trace('w', self.filter_scripts)

        self.search_entry = ctk.CTkEntry(
            self.sidebar,
            placeholder_text="Search scripts...",
            textvariable=self.search_var,
            height=35
        )
        self.search_entry.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        # Categories scrollable frame
        self.categories_label = ctk.CTkLabel(
            self.sidebar,
            text="Categories",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.categories_label.grid(row=4, column=0, padx=10, pady=(10, 5), sticky="nw")

        self.categories_frame = ctk.CTkScrollableFrame(self.sidebar, width=240)
        self.categories_frame.grid(row=5, column=0, padx=10, pady=5, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)

        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            self.sidebar,
            text="Refresh Scripts",
            command=self.scan_scripts,
            height=35,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.refresh_btn.grid(row=6, column=0, padx=10, pady=10, sticky="ew")

    def create_main_area(self):
        """Create the main content area"""
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Header
        self.header_frame = ctk.CTkFrame(self.main_frame)
        self.header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.current_category_label = ctk.CTkLabel(
            self.header_frame,
            text="All Scripts",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.current_category_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Quick actions frame
        self.quick_actions_frame = ctk.CTkFrame(self.header_frame)
        self.quick_actions_frame.grid(row=0, column=1, padx=10, pady=5, sticky="e")

        self.run_selected_btn = ctk.CTkButton(
            self.quick_actions_frame,
            text="Run Selected",
            command=self.run_selected_script,
            width=120,
            fg_color="#2563eb",
            hover_color="#1d4ed8"
        )
        self.run_selected_btn.grid(row=0, column=0, padx=5, pady=5)

        self.edit_selected_btn = ctk.CTkButton(
            self.quick_actions_frame,
            text="Edit Script",
            command=self.edit_selected_script,
            width=100,
            fg_color="#7c3aed",
            hover_color="#6d28d9"
        )
        self.edit_selected_btn.grid(row=0, column=1, padx=5, pady=5)

        # Scripts list
        self.scripts_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.scripts_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.scripts_frame.grid_columnconfigure(0, weight=1)

        self.script_widgets = []
        self.selected_script = None

    def create_output_panel(self):
        """Create the bottom output panel"""
        self.output_frame = ctk.CTkFrame(self)
        self.output_frame.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="nsew")
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_frame.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=0, minsize=200)

        # Output header
        self.output_header = ctk.CTkFrame(self.output_frame)
        self.output_header.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.output_header.grid_columnconfigure(0, weight=1)

        self.output_label = ctk.CTkLabel(
            self.output_header,
            text="Output",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.output_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.clear_output_btn = ctk.CTkButton(
            self.output_header,
            text="Clear",
            command=self.clear_output,
            width=60,
            height=25,
            fg_color="gray",
            hover_color="darkgray"
        )
        self.clear_output_btn.grid(row=0, column=1, padx=10, pady=5, sticky="e")

        # Output textbox
        self.output_text = ctk.CTkTextbox(
            self.output_frame,
            height=150,
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.output_text.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

    def browse_scripts_folder(self):
        """Open dialog to select scripts folder"""
        folder = filedialog.askdirectory(
            title="Select Scripts Folder",
            initialdir=self.scripts_folder or os.path.expanduser("~")
        )
        if folder:
            self.scripts_folder = folder
            self.folder_path_label.configure(text=folder)
            self.save_config()
            self.scan_scripts()

    def browse_working_dir(self):
        """Open dialog to select working directory"""
        folder = filedialog.askdirectory(
            title="Select Working Directory",
            initialdir=self.current_working_dir
        )
        if folder:
            self.current_working_dir = folder
            self.workdir_path_label.configure(text=folder)
            self.save_config()
            self.log_output(f"Working directory changed to: {folder}")

    def scan_scripts(self):
        """Scan the scripts folder for .ps1 and .bat files"""
        if not self.scripts_folder or not os.path.exists(self.scripts_folder):
            self.log_output("No scripts folder set or folder doesn't exist")
            return

        self.scripts = {}
        script_extensions = ('.ps1', '.bat', '.cmd', '.sh', '.py')

        # Scan folder structure
        for root, dirs, files in os.walk(self.scripts_folder):
            for file in files:
                if file.lower().endswith(script_extensions):
                    # Get relative path from scripts folder
                    rel_path = os.path.relpath(root, self.scripts_folder)
                    category = rel_path if rel_path != '.' else 'Uncategorized'

                    if category not in self.scripts:
                        self.scripts[category] = []

                    script_path = os.path.join(root, file)
                    script_info = {
                        'name': file,
                        'path': script_path,
                        'type': os.path.splitext(file)[1].lower(),
                        'category': category,
                        'size': os.path.getsize(script_path),
                        'modified': datetime.fromtimestamp(os.path.getmtime(script_path))
                    }
                    self.scripts[category].append(script_info)

        self.update_categories_list()
        self.show_all_scripts()
        self.log_output(f"Found {sum(len(s) for s in self.scripts.values())} scripts in {len(self.scripts)} categories")

    def update_categories_list(self):
        """Update the categories list in sidebar"""
        # Clear existing
        for widget in self.categories_frame.winfo_children():
            widget.destroy()

        # Add "All Scripts" option
        all_btn = ctk.CTkButton(
            self.categories_frame,
            text=f"All Scripts ({sum(len(s) for s in self.scripts.values())})",
            command=self.show_all_scripts,
            anchor="w",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30")
        )
        all_btn.pack(fill="x", pady=2)

        # Add each category
        for category in sorted(self.scripts.keys()):
            count = len(self.scripts[category])
            btn = ctk.CTkButton(
                self.categories_frame,
                text=f"{category} ({count})",
                command=lambda c=category: self.show_category(c),
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30")
            )
            btn.pack(fill="x", pady=2)

    def show_all_scripts(self):
        """Show all scripts in the main area"""
        self.current_category_label.configure(text="All Scripts")
        all_scripts = []
        for category_scripts in self.scripts.values():
            all_scripts.extend(category_scripts)
        self.display_scripts(all_scripts)

    def show_category(self, category):
        """Show scripts from a specific category"""
        self.current_category_label.configure(text=category)
        self.display_scripts(self.scripts.get(category, []))

    def display_scripts(self, scripts_list):
        """Display scripts in the main area"""
        # Clear existing
        for widget in self.scripts_frame.winfo_children():
            widget.destroy()
        self.script_widgets = []

        if not scripts_list:
            empty_label = ctk.CTkLabel(
                self.scripts_frame,
                text="No scripts found",
                font=ctk.CTkFont(size=14)
            )
            empty_label.pack(pady=20)
            return

        for script in scripts_list:
            self.create_script_card(script)

    def create_script_card(self, script):
        """Create a card widget for a script"""
        card = ctk.CTkFrame(self.scripts_frame, corner_radius=8)
        card.pack(fill="x", pady=5, padx=5)
        card.grid_columnconfigure(1, weight=1)

        # Script type indicator
        type_colors = {
            '.ps1': '#0078d4',  # PowerShell blue
            '.bat': '#4a4a4a',  # Batch gray
            '.cmd': '#4a4a4a',
            '.sh': '#4e9a06',   # Shell green
            '.py': '#3776ab'   # Python blue
        }
        type_color = type_colors.get(script['type'], '#666666')

        type_indicator = ctk.CTkFrame(card, width=8, corner_radius=4, fg_color=type_color)
        type_indicator.grid(row=0, column=0, rowspan=2, padx=(5, 10), pady=10, sticky="ns")

        # Script info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        info_frame.grid_columnconfigure(0, weight=1)

        name_label = ctk.CTkLabel(
            info_frame,
            text=script['name'],
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        name_label.grid(row=0, column=0, sticky="w")

        details_text = f"{script['category']} | {script['type'].upper()[1:]} | {script['modified'].strftime('%Y-%m-%d %H:%M')}"
        details_label = ctk.CTkLabel(
            info_frame,
            text=details_text,
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w"
        )
        details_label.grid(row=1, column=0, sticky="w")

        # Action buttons
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=10)

        run_btn = ctk.CTkButton(
            actions_frame,
            text="Run",
            command=lambda s=script: self.run_script(s),
            width=70,
            height=28,
            fg_color="#22c55e",
            hover_color="#16a34a"
        )
        run_btn.grid(row=0, column=0, padx=2, pady=2)

        edit_btn = ctk.CTkButton(
            actions_frame,
            text="Edit",
            command=lambda s=script: self.open_script_editor(s),
            width=70,
            height=28,
            fg_color="#6366f1",
            hover_color="#4f46e5"
        )
        edit_btn.grid(row=0, column=1, padx=2, pady=2)

        view_btn = ctk.CTkButton(
            actions_frame,
            text="View",
            command=lambda s=script: self.view_script(s),
            width=70,
            height=28,
            fg_color="#64748b",
            hover_color="#475569"
        )
        view_btn.grid(row=0, column=2, padx=2, pady=2)

        # Make card selectable
        def select_card(event, s=script, c=card):
            self.select_script(s, c)

        card.bind("<Button-1>", select_card)
        name_label.bind("<Button-1>", select_card)
        details_label.bind("<Button-1>", select_card)

        # Double-click to run
        def run_on_double_click(event, s=script):
            self.run_script(s)

        card.bind("<Double-Button-1>", run_on_double_click)
        name_label.bind("<Double-Button-1>", run_on_double_click)

        self.script_widgets.append({'card': card, 'script': script})

    def select_script(self, script, card):
        """Select a script card"""
        # Deselect all
        for widget_info in self.script_widgets:
            widget_info['card'].configure(fg_color=("gray85", "gray17"))

        # Select this one
        card.configure(fg_color=("gray75", "gray25"))
        self.selected_script = script

    def run_selected_script(self):
        """Run the currently selected script"""
        if self.selected_script:
            self.run_script(self.selected_script)
        else:
            messagebox.showwarning("No Selection", "Please select a script to run")

    def edit_selected_script(self):
        """Edit the currently selected script"""
        if self.selected_script:
            self.open_script_editor(self.selected_script)
        else:
            messagebox.showwarning("No Selection", "Please select a script to edit")

    def run_script(self, script):
        """Execute a script"""
        self.log_output(f"\n{'='*50}")
        self.log_output(f"Running: {script['name']}")
        self.log_output(f"Working Directory: {self.current_working_dir}")
        self.log_output(f"{'='*50}\n")

        def execute():
            try:
                system = platform.system()
                script_type = script['type']
                script_path = script['path']

                if script_type == '.ps1':
                    if system == 'Windows':
                        cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path]
                    else:
                        cmd = ['pwsh', '-File', script_path]
                elif script_type in ('.bat', '.cmd'):
                    if system == 'Windows':
                        cmd = ['cmd', '/c', script_path]
                    else:
                        self.log_output("Error: .bat/.cmd files can only run on Windows")
                        return
                elif script_type == '.sh':
                    cmd = ['bash', script_path]
                elif script_type == '.py':
                    cmd = ['python', script_path]
                else:
                    cmd = [script_path]

                process = subprocess.Popen(
                    cmd,
                    cwd=self.current_working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=False
                )

                stdout, stderr = process.communicate()

                if stdout:
                    self.log_output(stdout)
                if stderr:
                    self.log_output(f"STDERR:\n{stderr}")

                self.log_output(f"\n[Exit Code: {process.returncode}]")

            except Exception as e:
                self.log_output(f"Error executing script: {str(e)}")

        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=execute)
        thread.daemon = True
        thread.start()

    def open_script_editor(self, script):
        """Open script in system default editor"""
        try:
            system = platform.system()
            if system == 'Windows':
                os.startfile(script['path'])
            elif system == 'Darwin':
                subprocess.run(['open', script['path']])
            else:
                subprocess.run(['xdg-open', script['path']])
            self.log_output(f"Opened {script['name']} in default editor")
        except Exception as e:
            self.log_output(f"Error opening editor: {str(e)}")

    def view_script(self, script):
        """View script content in a popup"""
        viewer = ctk.CTkToplevel(self)
        viewer.title(f"View: {script['name']}")
        viewer.geometry("800x600")
        viewer.transient(self)

        # Read script content
        try:
            with open(script['path'], 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception as e:
            content = f"Error reading file: {str(e)}"

        # Textbox for content
        textbox = ctk.CTkTextbox(viewer, font=ctk.CTkFont(family="Consolas", size=12))
        textbox.pack(fill="both", expand=True, padx=10, pady=10)
        textbox.insert("1.0", content)
        textbox.configure(state="disabled")

        # Close button
        close_btn = ctk.CTkButton(viewer, text="Close", command=viewer.destroy)
        close_btn.pack(pady=10)

    def filter_scripts(self, *args):
        """Filter scripts based on search query"""
        query = self.search_var.get().lower()

        if not query:
            self.show_all_scripts()
            return

        filtered = []
        for category_scripts in self.scripts.values():
            for script in category_scripts:
                if query in script['name'].lower() or query in script['category'].lower():
                    filtered.append(script)

        self.current_category_label.configure(text=f"Search: '{query}'")
        self.display_scripts(filtered)

    def log_output(self, message):
        """Log message to output panel"""
        self.output_text.configure(state="normal")
        self.output_text.insert("end", message + "\n")
        self.output_text.see("end")
        self.output_history.append(message)

    def clear_output(self):
        """Clear the output panel"""
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_history = []


def main():
    app = ScriptHub()
    app.mainloop()


if __name__ == "__main__":
    main()
