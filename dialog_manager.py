import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk


class DialogManager:
    """Handles dialog windows and settings UI"""
    
    def __init__(self, parent_window, settings_manager, image_exporter, storage):
        self.root = parent_window
        self.settings = settings_manager
        self.image_exporter = image_exporter
        self.storage = storage
        self.selected_date = None
    
    def show_export_settings(self, selected_date):
        """Show the export settings dialog with live preview"""
        self.selected_date = selected_date
        
        # Load actual activities for preview
        try:
            actual_activities = self.storage.load_activities(selected_date)
        except:
            actual_activities = []
        
        options_window = tk.Toplevel(self.root)
        options_window.title("Export Settings")
        options_window.geometry("900x700")
        options_window.transient(self.root)
        options_window.grab_set()
        
        # Create main horizontal layout
        main_container = ttk.Frame(options_window)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side with notebook
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(left_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Font sizes tab
        font_frame = ttk.Frame(notebook, padding=15)
        notebook.add(font_frame, text="Font Sizes")
        
        ttk.Label(font_frame, text="Title Font Size:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        title_var = tk.IntVar(value=self.settings.get("title_font_size"))
        ttk.Spinbox(font_frame, from_=8, to=48, textvariable=title_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(font_frame, text="Header Font Size:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        header_var = tk.IntVar(value=self.settings.get("header_font_size"))
        ttk.Spinbox(font_frame, from_=8, to=48, textvariable=header_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(font_frame, text="Body Font Size:", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        body_var = tk.IntVar(value=self.settings.get("body_font_size"))
        ttk.Spinbox(font_frame, from_=8, to=48, textvariable=body_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(font_frame, text="Summary Font Size:", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        summary_var = tk.IntVar(value=self.settings.get("summary_font_size"))
        ttk.Spinbox(font_frame, from_=8, to=48, textvariable=summary_var, width=10).grid(row=3, column=1, sticky=tk.W, padx=10)
        
        # Column widths tab
        col_frame = ttk.Frame(notebook, padding=15)
        notebook.add(col_frame, text="Column Widths")
        
        col_vars = []
        columns = ["Proyecto/Area", "Avance", "Impacto", "Estado"]
        for i, col_name in enumerate(columns):
            ttk.Label(col_frame, text=f"{col_name} Width:", font=("Arial", 10)).grid(row=i, column=0, sticky=tk.W, pady=5)
            col_var = tk.IntVar(value=self.settings.get("column_widths")[i])
            col_vars.append(col_var)
            ttk.Spinbox(col_frame, from_=50, to=500, textvariable=col_var, width=10).grid(row=i, column=1, sticky=tk.W, padx=10)
        
        # Spacing tab
        space_frame = ttk.Frame(notebook, padding=15)
        notebook.add(space_frame, text="Spacing")
        
        ttk.Label(space_frame, text="Cell Padding:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        padding_var = tk.IntVar(value=self.settings.get("cell_padding"))
        ttk.Spinbox(space_frame, from_=5, to=30, textvariable=padding_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(space_frame, text="Minimum Row Height:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        row_height_var = tk.IntVar(value=self.settings.get("min_row_height"))
        ttk.Spinbox(space_frame, from_=30, to=150, textvariable=row_height_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(space_frame, text="Padding (Overall):", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        overall_padding_var = tk.IntVar(value=self.settings.get("padding"))
        ttk.Spinbox(space_frame, from_=5, to=50, textvariable=overall_padding_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=10)
        
        # Right side with preview
        preview_frame = ttk.LabelFrame(main_container, text="Preview", padding=10)
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        preview_label = ttk.Label(preview_frame)
        preview_label.pack(fill=tk.BOTH, expand=True)
        
        def update_preview(*args):
            """Update the preview with current settings"""
            preview_settings = {
                "title_font_size": title_var.get(),
                "header_font_size": header_var.get(),
                "body_font_size": body_var.get(),
                "summary_font_size": summary_var.get(),
                "column_widths": [cv.get() for cv in col_vars],
                "cell_padding": padding_var.get(),
                "min_row_height": row_height_var.get(),
                "padding": overall_padding_var.get()
            }
            
            try:
                preview_img = self.image_exporter.generate_preview_image(preview_settings, actual_activities if actual_activities else None)
                photo = ImageTk.PhotoImage(preview_img)
                preview_label.config(image=photo)
                preview_label.image = photo
            except Exception as e:
                preview_label.config(text=f"Preview Error: {str(e)}")
        
        # Bind all variables to update preview instantly
        title_var.trace("w", update_preview)
        header_var.trace("w", update_preview)
        body_var.trace("w", update_preview)
        summary_var.trace("w", update_preview)
        padding_var.trace("w", update_preview)
        row_height_var.trace("w", update_preview)
        overall_padding_var.trace("w", update_preview)
        for cv in col_vars:
            cv.trace("w", update_preview)
        
        # Initial preview
        update_preview()
        
        # Buttons
        button_frame = ttk.Frame(options_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_settings():
            self.settings.update({
                "title_font_size": title_var.get(),
                "header_font_size": header_var.get(),
                "body_font_size": body_var.get(),
                "summary_font_size": summary_var.get(),
                "column_widths": [cv.get() for cv in col_vars],
                "cell_padding": padding_var.get(),
                "min_row_height": row_height_var.get(),
                "padding": overall_padding_var.get()
            })
            self.settings.save()
            messagebox.showinfo("Success", "Settings saved successfully!")
            options_window.destroy()
        
        def reset_defaults():
            defaults = self.settings.reset_to_defaults()
            title_var.set(defaults["title_font_size"])
            header_var.set(defaults["header_font_size"])
            body_var.set(defaults["body_font_size"])
            summary_var.set(defaults["summary_font_size"])
            for i, cv in enumerate(col_vars):
                cv.set(defaults["column_widths"][i])
            padding_var.set(defaults["cell_padding"])
            row_height_var.set(defaults["min_row_height"])
            overall_padding_var.set(defaults["padding"])
            update_preview()
        
        ttk.Button(button_frame, text="Save", command=save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", command=reset_defaults).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=options_window.destroy).pack(side=tk.LEFT, padx=5)
