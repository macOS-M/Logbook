import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageTk
import subprocess
import platform
import json
from pathlib import Path

try:
    from tkcalendar import Calendar
except ImportError:
    Calendar = None

try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class DailyLogbookUI:
    
    def __init__(self, root, storage):
        self.root = root
        self.storage = storage     
        self.root.title("Daily Logbook")
        self.root.geometry("800x700")
        self.root.resizable(True, True)       
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.selected_date = self.today
        
        # Image export settings
        self.image_settings = self._load_image_settings()
        
        self.setup_ui()
        self.load_activities()
    
    def _get_settings_file(self):
        """Get the path to the settings file"""
        settings_dir = Path.home() / ".logbook"
        settings_dir.mkdir(exist_ok=True)
        return settings_dir / "image_settings.json"
    
    def _load_image_settings(self):
        """Load image export settings from file"""
        settings_file = self._get_settings_file()
        default_settings = {
            "title_font_size": 24,
            "header_font_size": 18,
            "body_font_size": 16,
            "summary_font_size": 14,
            "column_widths": [320, 280, 250, 160],
            "cell_padding": 15,
            "min_row_height": 60,
            "padding": 20
        }
        
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    loaded = json.load(f)
                    default_settings.update(loaded)
            except:
                pass
        
        return default_settings
    
    def _save_image_settings(self):
        """Save image export settings to file"""
        settings_file = self._get_settings_file()
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.image_settings, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def _generate_preview_image(self, settings_dict, activities=None):
        """Generate a preview image with given settings and optional activities"""
        padding = settings_dict["padding"]
        cell_padding = settings_dict["cell_padding"]
        min_row_height = settings_dict["min_row_height"]
        col_widths = settings_dict["column_widths"]
        
        header_bg = (44, 62, 80)
        header_fg = (255, 255, 255)
        row_bg = (255, 255, 255)
        border_color = (220, 220, 220)
        text_color = (51, 51, 51)
        title_color = (51, 51, 51)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", settings_dict["title_font_size"])
            header_font = ImageFont.truetype("arial.ttf", settings_dict["header_font_size"])
            body_font = ImageFont.truetype("arial.ttf", settings_dict["body_font_size"])
        except:
            title_font = header_font = body_font = ImageFont.load_default()
        
        # Use actual activities if provided, otherwise use sample data
        if activities is None:
            activities = [
                {"proyecto_area": "Website Redesign", "avance": "60% Complete", "impacto": "High Priority", "estado": "en progreso"},
                {"proyecto_area": "Database Migration", "avance": "Testing Phase", "impacto": "Critical", "estado": "en progreso"},
            ]
        else:
            # Limit to first 10 activities for preview
            activities = activities[:10]
        
        temp_img = Image.new("RGB", (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        line_height = self._get_line_height(temp_draw, body_font)
        
        # Calculate row heights with text wrapping
        row_heights = []
        wrapped_content = []
        
        for activity in activities:
            proyecto_lines = self._wrap_text_for_image(activity.get("proyecto_area", ""), None, col_widths[0], temp_draw, body_font)
            avance_lines = self._wrap_text_for_image(activity.get("avance", ""), None, col_widths[1], temp_draw, body_font)
            impacto_lines = self._wrap_text_for_image(activity.get("impacto", ""), None, col_widths[2], temp_draw, body_font)
            estado_lines = [activity.get("estado", "pendiente")]
            
            max_lines = max(len(proyecto_lines), len(avance_lines), len(impacto_lines), len(estado_lines))
            row_height = max(min_row_height, (max_lines * line_height) + (cell_padding * 2))
            
            row_heights.append(row_height)
            wrapped_content.append({
                'proyecto': proyecto_lines,
                'avance': avance_lines,
                'impacto': impacto_lines,
                'estado': estado_lines
            })
        
        # Calculate dimensions
        title_height = 60
        header_height = 50
        content_height = sum(row_heights)
        summary_height = 40
        total_height = title_height + header_height + content_height + summary_height + (padding * 2)
        total_width = sum(col_widths) + (padding * 2) + 2
        
        # Create image
        img = Image.new("RGB", (total_width, total_height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        y = padding
        
        # Draw title
        draw.text((padding + 10, y), "Daily Logbook - Preview", fill=title_color, font=title_font)
        y += title_height
        
        # Draw header
        x = padding
        headers = ["Proyecto/Area", "Avance", "Impacto", "Estado"]
        draw.rectangle(
            [(padding, y), (total_width - padding, y + header_height)],
            fill=header_bg, outline=border_color
        )
        
        for i, header in enumerate(headers):
            draw.text((x + cell_padding, y + cell_padding), header, fill=header_fg, font=header_font)
            x += col_widths[i]
        
        y += header_height
        
        # Draw data rows
        for idx, activity in enumerate(activities):
            row_height = row_heights[idx]
            bg_color = row_bg
            draw.rectangle(
                [(padding, y), (total_width - padding, y + row_height)],
                fill=bg_color, outline=border_color
            )
            
            content = wrapped_content[idx]
            x = padding
            
            # Draw each cell with wrapped text
            for col_idx, (lines, col_width) in enumerate(zip(
                [content['proyecto'], content['avance'], content['impacto'], content['estado']],
                col_widths
            )):
                text_y = y + cell_padding
                for line in lines:
                    draw.text((x + cell_padding, text_y), line, fill=text_color, font=body_font)
                    text_y += line_height
                
                x += col_width
            
            y += row_height
        
        # Resize for display (max 800x600 for dialog)
        max_width = 800
        max_height = 600
        if total_width > max_width or total_height > max_height:
            scale = min(max_width / total_width, max_height / total_height)
            new_size = (int(total_width * scale), int(total_height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        return img
    
    def show_options(self):
        """Show the options/settings dialog"""
        # Load actual activities for preview
        try:
            actual_activities = self.storage.load_activities(self.selected_date)
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
        title_var = tk.IntVar(value=self.image_settings["title_font_size"])
        ttk.Spinbox(font_frame, from_=8, to=48, textvariable=title_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(font_frame, text="Header Font Size:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        header_var = tk.IntVar(value=self.image_settings["header_font_size"])
        ttk.Spinbox(font_frame, from_=8, to=48, textvariable=header_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(font_frame, text="Body Font Size:", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        body_var = tk.IntVar(value=self.image_settings["body_font_size"])
        ttk.Spinbox(font_frame, from_=8, to=48, textvariable=body_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(font_frame, text="Summary Font Size:", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        summary_var = tk.IntVar(value=self.image_settings["summary_font_size"])
        ttk.Spinbox(font_frame, from_=8, to=48, textvariable=summary_var, width=10).grid(row=3, column=1, sticky=tk.W, padx=10)
        
        # Column widths tab
        col_frame = ttk.Frame(notebook, padding=15)
        notebook.add(col_frame, text="Column Widths")
        
        col_vars = []
        columns = ["Proyecto/Area", "Avance", "Impacto", "Estado"]
        for i, col_name in enumerate(columns):
            ttk.Label(col_frame, text=f"{col_name} Width:", font=("Arial", 10)).grid(row=i, column=0, sticky=tk.W, pady=5)
            col_var = tk.IntVar(value=self.image_settings["column_widths"][i])
            col_vars.append(col_var)
            ttk.Spinbox(col_frame, from_=50, to=500, textvariable=col_var, width=10).grid(row=i, column=1, sticky=tk.W, padx=10)
        
        # Spacing tab
        space_frame = ttk.Frame(notebook, padding=15)
        notebook.add(space_frame, text="Spacing")
        
        ttk.Label(space_frame, text="Cell Padding:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        padding_var = tk.IntVar(value=self.image_settings["cell_padding"])
        ttk.Spinbox(space_frame, from_=5, to=30, textvariable=padding_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(space_frame, text="Minimum Row Height:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        row_height_var = tk.IntVar(value=self.image_settings["min_row_height"])
        ttk.Spinbox(space_frame, from_=30, to=150, textvariable=row_height_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(space_frame, text="Padding (Overall):", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        overall_padding_var = tk.IntVar(value=self.image_settings["padding"])
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
                preview_img = self._generate_preview_image(preview_settings, actual_activities if actual_activities else None)
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
            self.image_settings["title_font_size"] = title_var.get()
            self.image_settings["header_font_size"] = header_var.get()
            self.image_settings["body_font_size"] = body_var.get()
            self.image_settings["summary_font_size"] = summary_var.get()
            self.image_settings["column_widths"] = [cv.get() for cv in col_vars]
            self.image_settings["cell_padding"] = padding_var.get()
            self.image_settings["min_row_height"] = row_height_var.get()
            self.image_settings["padding"] = overall_padding_var.get()
            
            self._save_image_settings()
            messagebox.showinfo("Success", "Settings saved successfully!")
            options_window.destroy()
        
        def reset_defaults():
            defaults = {
                "title_font_size": 24,
                "header_font_size": 18,
                "body_font_size": 16,
                "summary_font_size": 14,
                "column_widths": [320, 280, 250, 160],
                "cell_padding": 15,
                "min_row_height": 60,
                "padding": 20
            }
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
    
    def setup_ui(self):
        """Create all UI components"""
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Options menu
        options_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Options", menu=options_menu)
        options_menu.add_command(label="Export Settings", command=self.show_options)
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self._setup_calendar_panel(main_frame)
        
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self._setup_header(right_panel)
        self._setup_input_section(right_panel)
        self._setup_action_buttons(right_panel)
        self._setup_activities_list(right_panel)
        
        if Calendar and hasattr(self, 'calendar'):
            self.calendar.bind('<<CalendarSelected>>', self.on_date_selected)
    
    def _setup_calendar_panel(self, parent):
        """Setup calendar widget"""
        left_panel = ttk.Frame(parent, width=380)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False) 
        
        ttk.Label(left_panel, text="Calendar", font=("Arial", 11, "bold")).pack(pady=10)
        
        if Calendar:
            self.calendar = Calendar(
                left_panel,
                selectmode='day',
                year=int(self.today.split('-')[0]),
                month=int(self.today.split('-')[1]),
                day=int(self.today.split('-')[2])
            )
            self.calendar.pack(pady=(0, 10), padx=5)
        else:
            ttk.Label(
                left_panel,
                text="Calendar not available.\nInstall: pip install tkcalendar",
                font=("Arial", 9)
            ).pack(pady=10)
        
        self._setup_graph_panel(left_panel)
    
    def _setup_graph_panel(self, parent):
        """Setup graph panel for visualizing statistics"""
        if not MATPLOTLIB_AVAILABLE:
            return
            
        graph_frame = ttk.LabelFrame(parent, text="📈 Activity Trends", padding=10)
        graph_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create matplotlib figure
        self.trend_figure = Figure(figsize=(2.8, 5.5), dpi=80)
        self.trend_figure.patch.set_facecolor('#f0f0f0')
        self.trend_ax = self.trend_figure.add_subplot(311)
        self.hourly_ax = self.trend_figure.add_subplot(312)
        self.common_ax = self.trend_figure.add_subplot(313)
        
        # Create canvas
        self.trend_canvas = FigureCanvasTkAgg(self.trend_figure, master=graph_frame)
        self.trend_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.update_graph()


    
    def update_graph(self):
        """Update the activity graph with latest data"""
        if not MATPLOTLIB_AVAILABLE or not hasattr(self, 'trend_ax'):
            return
            
        try:
            self.trend_ax.clear()
            self.hourly_ax.clear()
            
            # Get last 7 days of data
            base_date = datetime.strptime(self.selected_date, "%Y-%m-%d")
            dates = []
            counts = []
            labels = []
            date_strings = []
            
            for i in range(6, -1, -1):
                date = base_date - timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")
                activities = self.storage.load_activities(date_str)
                
                dates.append(date)
                counts.append(len(activities))
                labels.append(date.strftime("%a"))
                date_strings.append(date_str)
            
            # Create bar chart - highlight the selected date in red
            colors = ['#e74c3c' if date_str == self.selected_date else '#3498db' 
                     for date_str in date_strings]
            bars = self.trend_ax.bar(labels, counts, color=colors, alpha=0.8, edgecolor='white', linewidth=1.5)
            
            # Customize the graph
            self.trend_ax.set_ylabel('Activities', fontsize=8)
            self.trend_ax.set_title('Last 7 Days', fontsize=9, fontweight='bold', pad=8)
            self.trend_ax.tick_params(axis='both', labelsize=7)
            self.trend_ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
            self.trend_ax.set_axisbelow(True)
            
            # Set y-axis to start at 0 and use integers only
            max_count = max(counts) if counts else 1
            self.trend_ax.set_ylim(0, max(max_count + 1, 5))
            self.trend_ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    self.trend_ax.text(bar.get_x() + bar.get_width()/2., height,
                               f'{int(height)}',
                               ha='center', va='bottom', fontsize=7, fontweight='bold')
            
            # Hourly pattern (last 7 days)
            hour_counts = [0] * 24
            for i in range(7):
                date = base_date - timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")
                activities = self.storage.load_activities(date_str)
                for activity in activities:
                    try:
                        hour = int(activity["time"].split(":")[0])
                        if 0 <= hour <= 23:
                            hour_counts[hour] += 1
                    except Exception:
                        continue
            
            hour_labels = [str(h) for h in range(24)]
            self.hourly_ax.bar(hour_labels, hour_counts, color='#9b59b6', alpha=0.8, edgecolor='white', linewidth=0.8)
            self.hourly_ax.set_title('Hourly Pattern (7d)', fontsize=9, fontweight='bold', pad=6)
            self.hourly_ax.tick_params(axis='x', labelsize=6, rotation=0)
            self.hourly_ax.tick_params(axis='y', labelsize=7)
            self.hourly_ax.grid(axis='y', alpha=0.25, linestyle='--', linewidth=0.5)
            self.hourly_ax.set_axisbelow(True)
            
            max_count = max(hour_counts) if hour_counts else 1
            self.hourly_ax.set_ylim(0, max(max_count + 1, 5))
            self.hourly_ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
            
            # Plot most common activities in the same figure
            self.common_ax.clear()
            activities_dict = self.storage.get_activities_by_date_range(base_date - timedelta(days=29), base_date)
            
            counts = {}
            labels = {}
            for activities in activities_dict.values():
                for activity in activities:
                    text = activity.get("text", "").strip()
                    if not text:
                        continue
                    key = text.lower()
                    counts[key] = counts.get(key, 0) + 1
                    if key not in labels:
                        labels[key] = text
            
            if not counts:
                self.common_ax.text(0.5, 0.5, "No activity data", ha='center', va='center', fontsize=8)
                self.common_ax.set_axis_off()
            else:
                self.common_ax.set_axis_on()
                top_items = sorted(counts.items(), key=lambda item: item[1], reverse=True)[:5]
                top_labels = [labels[key] for key, _ in top_items]
                top_values = [value for _, value in top_items]
                
                self.common_ax.barh(top_labels, top_values, color='#1abc9c', alpha=0.85, edgecolor='white', linewidth=1.0)
                self.common_ax.invert_yaxis()
                self.common_ax.set_title('Top activities (Last 30 Days)', fontsize=9, fontweight='bold', pad=6)
                self.common_ax.tick_params(axis='both', labelsize=7)
                self.common_ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
                self.common_ax.grid(axis='x', alpha=0.25, linestyle='--', linewidth=0.5)
                self.common_ax.set_axisbelow(True)
                
                for label, value in zip(top_labels, top_values):
                    self.common_ax.text(value + 0.05, label, f"{value}", va='center', fontsize=7, fontweight='bold')
            
            self.trend_figure.tight_layout(pad=0.5)
            self.trend_canvas.draw()
            
        except Exception as e:
            pass


    
    def update_insights(self):
        """Update the insights panel with current data"""
        try:
            self.update_graph()
            
        except Exception as e:
            pass 
    
    def _setup_header(self, parent):
        """Setup header with title and date"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ttk.Label(header_frame, text="Daily Logbook", font=("Arial", 20, "bold")).pack()
        
        self.date_label = ttk.Label(
            header_frame,
            text=datetime.now().strftime("%A, %B %d, %Y"),
            font=("Arial", 10)
        )
        self.date_label.pack()
    
    def _setup_input_section(self, parent):
        """Setup project/area and progress input fields"""
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Label(input_frame, text="Proyecto/Area:", font=("Arial", 9)).pack(anchor=tk.W)
        self.proyecto_input = ttk.Entry(input_frame, font=("Arial", 11))
        self.proyecto_input.pack(fill=tk.X, pady=(0, 8))
        self.proyecto_input.bind('<Return>', lambda e: self.add_activity())
        
        ttk.Label(input_frame, text="Avance:", font=("Arial", 9)).pack(anchor=tk.W)
        self.avance_input = ttk.Entry(input_frame, font=("Arial", 11))
        self.avance_input.pack(fill=tk.X, pady=(0, 8))
        self.avance_input.bind('<Return>', lambda e: self.add_activity())
        
        ttk.Label(input_frame, text="Impacto:", font=("Arial", 9)).pack(anchor=tk.W)
        self.impacto_input = ttk.Entry(input_frame, font=("Arial", 11))
        self.impacto_input.pack(fill=tk.X, pady=(0, 8))
        self.impacto_input.bind('<Return>', lambda e: self.add_activity())
        
        ttk.Label(input_frame, text="Estado:", font=("Arial", 9)).pack(anchor=tk.W)
        self.estado_input = ttk.Combobox(input_frame, font=("Arial", 11), state="readonly", values=["pendiente", "en progreso", "pendiente revision", "completado"])
        self.estado_input.set("pendiente")
        self.estado_input.pack(fill=tk.X, pady=(0, 8))
        self.estado_input.bind('<Return>', lambda e: self.add_activity())
        
        ttk.Button(input_frame, text="Add Activity", command=self.add_activity).pack(side=tk.LEFT)
    
    def _setup_action_buttons(self, parent):
        """Setup export and clear buttons"""
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Button(action_frame, text="Copy as Image", command=self.copy_as_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Copy as Text", command=self.copy_as_text).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Export as CSV", command=self.export_to_csv).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Clear Day", command=self.clear_today).pack(side=tk.LEFT)
        
        view_frame = ttk.Frame(parent)
        view_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        ttk.Button(view_frame, text="View This Week", command=self.view_by_week).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(view_frame, text="View This Month", command=self.view_by_month).pack(side=tk.LEFT)
    
    def _setup_activities_list(self, parent):
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        ttk.Label(list_frame, text="Activities", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        columns = ("Proyecto/Area", "Avance", "Impacto", "Estado", "Actions")
        self.tree = ttk.Treeview(list_frame, columns=columns, height=12, show="tree headings")
        
        # Configure style for text wrapping
        style = ttk.Style()
        style.configure('Treeview', rowheight=60)  # Increase row height to allow wrapped text
        
        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("Proyecto/Area", anchor=tk.NW, width=100, stretch=True)  # Changed to NW for top-left alignment
        self.tree.column("Avance", anchor=tk.NW, width=300, stretch=True)  # Changed to NW for top-left alignment
        self.tree.column("Impacto", anchor=tk.NW, width=300, stretch=True)  # Changed to NW for top-left alignment
        self.tree.column("Estado", anchor=tk.CENTER, width=100, stretch=True)
        self.tree.column("Actions", anchor=tk.CENTER, width=80, stretch=False)
        
        self.tree.heading("Proyecto/Area", text="Proyecto/Area")
        self.tree.heading("Avance", text="Avance")
        self.tree.heading("Impacto", text="Impacto")
        self.tree.heading("Estado", text="Estado")
        self.tree.heading("Actions", text="Actions")
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Button-1>", self.on_tree_click)
    
    def on_tree_click(self, event):
        item = self.tree.identify('item', event.x, event.y)
        column = self.tree.identify_column(event.x)
        
        if not item:
            return
        
        values = self.tree.item(item)['values']
        if not values or len(values) < 1:
            return
        
        proyecto_area = values[0]
        
        try:
            activities = self.storage.load_activities(self.selected_date)
            activity = next((a for a in activities if a.get("proyecto_area") == proyecto_area), None)
            if not activity:
                return
            activity_time = activity["time"]
        except:
            return
        
        if column == "#5":
            col_box = self.tree.bbox(item, column)
            if col_box:
                x_relative = event.x - col_box[0]
                col_width = col_box[2]
                mid_point = col_width / 2               
                if x_relative < mid_point:
                    self.edit_activity(activity_time)
                else:
                    if messagebox.askyesno("Confirm Delete", "Delete this activity?"):
                        self.delete_activity(activity_time)
    
    def on_date_selected(self, event):
        if not Calendar or not hasattr(self, 'calendar'):
            return
        
        try:
            calendar_date = self.calendar.get_date()           
            date_obj = datetime.strptime(calendar_date, "%m/%d/%y")
            normalized_date = date_obj.strftime("%Y-%m-%d")
            if normalized_date == self.selected_date:
                return
            
            self.selected_date = normalized_date        
            self.date_label.config(text=date_obj.strftime("%A, %B %d, %Y"))
            self.load_activities()
        except Exception as e:
            pass
    
    def add_activity(self):
        proyecto_area = self.proyecto_input.get().strip()
        avance = self.avance_input.get().strip()
        impacto = self.impacto_input.get().strip()
        estado = self.estado_input.get().strip()
        
        if not proyecto_area:
            messagebox.showwarning("Empty Project", "Please enter a project/area!")
            return
        
        try:
            self.storage.add_activity(self.selected_date, proyecto_area, avance, impacto, estado)
            self.proyecto_input.delete(0, tk.END)
            self.avance_input.delete(0, tk.END)
            self.impacto_input.delete(0, tk.END)
            self.estado_input.set("pendiente")
            self.proyecto_input.focus()
            self.load_activities()
            self.update_insights()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add activity: {e}")
    
    def _wrap_text(self, text, max_width=30):
        """Wrap text to fit within column width"""
        if not text:
            return text
        
        # Split text into lines if it contains newlines already
        lines = text.split('\n')
        wrapped_lines = []
        
        for line in lines:
            if len(line) <= max_width:
                wrapped_lines.append(line)
            else:
                # Break long lines into multiple shorter lines
                words = line.split()
                current_line = ""
                for word in words:
                    if len(current_line) + len(word) + 1 <= max_width:
                        current_line += word + " "
                    else:
                        if current_line:
                            wrapped_lines.append(current_line.strip())
                        current_line = word + " "
                if current_line:
                    wrapped_lines.append(current_line.strip())
        
        return "\n".join(wrapped_lines)
    
    def load_activities(self):
        """Display activities in the tree"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            activities = self.storage.load_activities(self.selected_date)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load activities: {e}")
            return
        
        if not activities:
            self.tree.insert("", tk.END, values=("", "", "", "", ""))
            self.update_insights()
            return
        
        for activity in activities:
            proyecto = self._wrap_text(activity.get("proyecto_area", ""), max_width=10)
            avance = self._wrap_text(activity.get("avance", ""), max_width=100)
            impacto = self._wrap_text(activity.get("impacto", ""), max_width=100)
            estado = activity.get("estado", "pendiente")
            self.tree.insert("", tk.END, values=(proyecto, avance, impacto, estado, "✎ ✕"))
        
        self.update_insights()
    
    def edit_activity(self, activity_time):
        try:
            activities = self.storage.load_activities(self.selected_date)
            base_time = activity_time.split(" ")[0]
            activity = next((a for a in activities if a["time"] == base_time), None)
            
            if not activity:
                return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load activity: {e}")
            return
            
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Activity")
        edit_window.geometry("400x300")
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Proyecto/Area
        ttk.Label(edit_window, text="Proyecto/Area:", font=("Arial", 10)).pack(anchor=tk.W, padx=15, pady=(15, 5))
        proyecto_var = ttk.Entry(edit_window, font=("Arial", 11))
        proyecto_var.insert(0, activity.get("proyecto_area", ""))
        proyecto_var.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Avance
        ttk.Label(edit_window, text="Avance:", font=("Arial", 10)).pack(anchor=tk.W, padx=15, pady=(0, 5))
        avance_var = ttk.Entry(edit_window, font=("Arial", 11))
        avance_var.insert(0, activity.get("avance", ""))
        avance_var.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Impacto
        ttk.Label(edit_window, text="Impacto:", font=("Arial", 10)).pack(anchor=tk.W, padx=15, pady=(0, 5))
        impacto_var = ttk.Entry(edit_window, font=("Arial", 11))
        impacto_var.insert(0, activity.get("impacto", ""))
        impacto_var.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Estado
        ttk.Label(edit_window, text="Estado:", font=("Arial", 10)).pack(anchor=tk.W, padx=15, pady=(0, 5))
        estado_var = ttk.Combobox(edit_window, font=("Arial", 11), state="readonly", values=["pendiente", "en progreso", "pendiente revision", "completado"])
        estado_var.set(activity.get("estado", "pendiente"))
        estado_var.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        def save_changes():
            new_proyecto = proyecto_var.get().strip()
            if not new_proyecto:
                messagebox.showwarning("Empty Project", "Proyecto/Area cannot be empty!")
                return
            
            try:
                self.storage.update_activity(
                    self.selected_date,
                    base_time,
                    new_proyecto,
                    avance_var.get().strip(),
                    impacto_var.get().strip(),
                    estado_var.get().strip()
                )
                edit_window.destroy()
                self.load_activities()
                self.update_insights()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update activity: {e}")
        
        ttk.Button(edit_window, text="Save", command=save_changes).pack(pady=10)
    
    def delete_activity(self, activity_time):
        """Delete an activity"""
        try:
            base_time = activity_time.split(" ")[0]
            self.storage.delete_activity(self.selected_date, base_time)
            self.load_activities()
            self.update_insights()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete activity: {e}")
    
    def copy_as_text(self):
        try:
            activities = self.storage.load_activities(self.selected_date)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load activities: {e}")
            return
        
        if not activities:
            messagebox.showwarning("No Activities", "No activities to copy!")
            return
        try:
            date_obj = datetime.strptime(self.selected_date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%Y-%m-%d")
        except:
            formatted_date = self.selected_date
        
        lines = []
        lines.append("📋 Daily Logbook")
        lines.append(formatted_date)
        lines.append("=" * 90)
        lines.append("")
        lines.append(f"{'Proyecto/Area':<25} | {'Avance':<20} | {'Impacto':<15} | {'Estado':<15}")
        lines.append("-" * 90)       
        for activity in activities:
            proyecto = activity.get("proyecto_area", "")[:25].ljust(25)
            avance = activity.get("avance", "")[:20].ljust(20)
            impacto = activity.get("impacto", "")[:15].ljust(15)
            estado = activity.get("estado", "pendiente")[:15].ljust(15)
            lines.append(f"{proyecto} | {avance} | {impacto} | {estado}")
        
        lines.append("")
        lines.append("=" * 90)
        lines.append(f"Total: {len(activities)} activities logged")        
        output = "\n".join(lines)
        self.root.clipboard_clear()
        self.root.clipboard_append(output)
        self.root.update()
        
        messagebox.showinfo("Copied", "Activities copied to clipboard as text!")
    
    def copy_as_image(self):
        try:
            activities = self.storage.load_activities(self.selected_date)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load activities: {e}")
            return
        
        if not activities:
            messagebox.showwarning("No Activities", "No activities to copy!")
            return
        try:
            date_obj = datetime.strptime(self.selected_date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%Y-%m-%d")
        except:
            formatted_date = self.selected_date       
        try:
            img = self._create_table_image(formatted_date, activities)
            self._copy_image_to_clipboard(img)
            messagebox.showinfo("Copied", "Table image copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy table: {e}")
    
    def _wrap_text_for_image(self, text, max_char_width, col_width, draw, font):
        """Wrap text to fit within a column width and return list of lines with their heights"""
        if not text:
            return []
        
        lines = []
        words = text.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]
            
            if line_width <= col_width - 20:  # Leave padding for cell margins
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
    
    def _get_line_height(self, draw, font):
        """Get the height of a single line of text"""
        bbox = draw.textbbox((0, 0), "Agy", font=font)
        return bbox[3] - bbox[1] + 5  # Add small spacing
    
    def _create_table_image(self, date_str, activities):
        # Get settings from self.image_settings
        padding = self.image_settings["padding"]
        cell_padding = self.image_settings["cell_padding"]
        min_row_height = self.image_settings["min_row_height"]
        header_bg = (44, 62, 80)  
        header_fg = (255, 255, 255) 
        row_bg_odd = (255, 255, 255)
        row_bg_even = (249, 249, 249)  
        border_color = (220, 220, 220)  
        text_color = (51, 51, 51) 
        title_color = (51, 51, 51)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", self.image_settings["title_font_size"])
            header_font = ImageFont.truetype("arial.ttf", self.image_settings["header_font_size"])
            body_font = ImageFont.truetype("arial.ttf", self.image_settings["body_font_size"])
            summary_font = ImageFont.truetype("arial.ttf", self.image_settings["summary_font_size"])
        except:
            title_font = header_font = body_font = summary_font = ImageFont.load_default()
        
        temp_img = Image.new("RGB", (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # Set fixed reasonable column widths for wrapping
        col_widths = self.image_settings["column_widths"]  # Use settings
        
        # Calculate actual row heights based on wrapped content
        row_heights = []
        wrapped_content = []
        line_height = self._get_line_height(temp_draw, body_font)
        
        for activity in activities:
            proyecto_lines = self._wrap_text_for_image(activity.get("proyecto_area", ""), 25, col_widths[0], temp_draw, body_font)
            avance_lines = self._wrap_text_for_image(activity.get("avance", ""), 20, col_widths[1], temp_draw, body_font)
            impacto_lines = self._wrap_text_for_image(activity.get("impacto", ""), 20, col_widths[2], temp_draw, body_font)
            estado_lines = [activity.get("estado", "pendiente")]
            
            max_lines = max(len(proyecto_lines), len(avance_lines), len(impacto_lines), len(estado_lines))
            row_height = max(min_row_height, (max_lines * line_height) + (cell_padding * 2))
            
            row_heights.append(row_height)
            wrapped_content.append({
                'proyecto': proyecto_lines,
                'avance': avance_lines,
                'impacto': impacto_lines,
                'estado': estado_lines
            })
        
        # Calculate dimensions
        title_height = 80
        header_height = 70
        content_height = sum(row_heights)
        summary_height = 60
        total_height = title_height + header_height + content_height + summary_height + (padding * 2)
        total_width = sum(col_widths) + (padding * 2) + 2 
        
        # Create image
        img = Image.new("RGB", (total_width, total_height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        y = padding
        
        # Draw title
        draw.text((padding + 10, y), f"Daily Logbook - {date_str}", fill=title_color, font=title_font)
        y += title_height
        
        # Draw header
        x = padding
        headers = ["Proyecto/Area", "Avance", "Impacto", "Estado"]
        draw.rectangle(
            [(padding, y), (total_width - padding, y + header_height)],
            fill=header_bg, outline=border_color
        )
        
        for i, header in enumerate(headers):
            draw.text((x + cell_padding, y + cell_padding), header, fill=header_fg, font=header_font)
            x += col_widths[i]
        
        y += header_height
        
        # Draw data rows
        for idx, (activity, row_height) in enumerate(zip(activities, row_heights)):
            bg_color = row_bg_even if idx % 2 == 0 else row_bg_odd
            draw.rectangle(
                [(padding, y), (total_width - padding, y + row_height)],
                fill=bg_color, outline=border_color
            )
            
            content = wrapped_content[idx]
            x = padding
            
            # Draw each cell with wrapped text
            for col_idx, (lines, col_width) in enumerate(zip(
                [content['proyecto'], content['avance'], content['impacto'], content['estado']],
                col_widths
            )):
                text_y = y + cell_padding
                for line in lines:
                    draw.text((x + cell_padding, text_y), line, fill=text_color, font=body_font)
                    text_y += line_height
                
                x += col_width
            
            y += row_height
        
        draw.text((padding + 10, y + 10), f"Total: {len(activities)} activities logged", fill=text_color, font=summary_font)
        
        return img
    
    def _copy_image_to_clipboard(self, image):
        """Copy PIL Image to clipboard (cross-platform)"""
        import os
        from pathlib import Path
        temp_path = Path.home() / ".logbook" / "temp_table.png"
        temp_path.parent.mkdir(exist_ok=True)
        image.save(temp_path, "PNG")
        
        system = platform.system()
        
        try:
            if system == "Windows":
                ps_cmd = f"""
                Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.Clipboard]::SetImage([System.Drawing.Image]::FromFile('{temp_path}'))
                """
                subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, check=True)
            
            elif system == "Darwin":
                subprocess.run([
                    "osascript", "-e",
                    f'set the clipboard to (read (POSIX file "{temp_path}") as PNG picture)'
                ], check=True)
            
            elif system == "Linux":
                try:
                    subprocess.run([
                        "xclip", "-selection", "clipboard", "-t", "image/png", "-i", str(temp_path)
                    ], check=True)
                except FileNotFoundError:
                    subprocess.run([
                        "xsel", "--clipboard", "--input"
                    ], stdin=open(temp_path, 'rb'), check=True)
            
            else:
                raise NotImplementedError(f"Clipboard copy not supported on {system}")
        
        except Exception as e:
            desktop = Path.home() / "Desktop" / f"logbook_table_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            image.save(desktop, "PNG")
            raise Exception(f"Clipboard not available. Image saved to: {desktop}")
        
        finally:
            try:
                os.remove(temp_path)
            except:
                pass
    
    def _create_multi_day_table_image(self, title_text, activities_dict, total_count):
        """Create an image for multi-day activities view with day groupings"""
        padding = 20
        cell_padding = 10
        row_height = 35
        day_header_height = 40
        header_bg = (44, 62, 80)
        header_fg = (255, 255, 255)
        day_header_bg = (70, 130, 180)  # Steel blue for day headers
        day_header_fg = (255, 255, 255)
        row_bg_odd = (255, 255, 255)
        row_bg_even = (249, 249, 249)
        border_color = (220, 220, 220)
        text_color = (51, 51, 51)
        title_color = (51, 51, 51)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 16)
            header_font = ImageFont.truetype("arial.ttf", 12)
            day_header_font = ImageFont.truetype("arialbd.ttf", 11)
            body_font = ImageFont.truetype("arial.ttf", 11)
            summary_font = ImageFont.truetype("arial.ttf", 10)
        except:
            title_font = header_font = day_header_font = body_font = summary_font = ImageFont.load_default()
        
        # Calculate column widths
        temp_img = Image.new("RGB", (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        headers = ["Proyecto/Area", "Avance", "Impacto", "Estado"]
        
        col_widths = [150, 100, 100, 100]  # Starting widths
        
        # Check all activities to determine column widths
        for date_str, activities in activities_dict.items():
            for activity in activities:
                # Proyecto/Area
                bbox = temp_draw.textbbox((0, 0), activity.get("proyecto_area", ""), font=body_font)
                width = bbox[2] - bbox[0] + cell_padding * 2
                col_widths[0] = max(col_widths[0], width)
                
                # Avance
                bbox = temp_draw.textbbox((0, 0), activity.get("avance", ""), font=body_font)
                width = bbox[2] - bbox[0] + cell_padding * 2
                col_widths[1] = max(col_widths[1], width)
                
                # Impacto
                bbox = temp_draw.textbbox((0, 0), activity.get("impacto", ""), font=body_font)
                width = bbox[2] - bbox[0] + cell_padding * 2
                col_widths[2] = max(col_widths[2], width)
                
                # Estado
                bbox = temp_draw.textbbox((0, 0), activity.get("estado", "pendiente"), font=body_font)
                width = bbox[2] - bbox[0] + cell_padding * 2
                col_widths[3] = max(col_widths[3], width)
        
        col_widths = [max(w, 80) for w in col_widths]
        
        # Calculate dimensions
        title_height = 60
        column_header_height = row_height
        
        # Count rows: day headers + activities
        content_rows = 0
        for activities in activities_dict.values():
            content_rows += 1  # Day header
            content_rows += len(activities)  # Activities
        
        content_height = (len(activities_dict) * day_header_height) + ((content_rows - len(activities_dict)) * row_height)
        summary_height = 50
        total_height = title_height + column_header_height + content_height + summary_height + (padding * 2)
        total_width = sum(col_widths) + (padding * 2) + 2
        
        # Create image
        img = Image.new("RGB", (total_width, total_height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        y = padding
        
        # Draw title
        draw.text((padding + 10, y), title_text, fill=title_color, font=title_font)
        y += title_height
        
        # Draw column headers
        x = padding
        draw.rectangle(
            [(padding, y), (total_width - padding, y + row_height)],
            fill=header_bg, outline=border_color
        )
        
        for i, header in enumerate(headers):
            draw.text((x + cell_padding, y + cell_padding), header, fill=header_fg, font=header_font)
            x += col_widths[i]
        
        y += row_height
        
        # Draw activities grouped by day
        for date_str, activities in sorted(activities_dict.items()):
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            day_header_text = date_obj.strftime("%A, %B %d, %Y")
            
            # Draw day header row
            draw.rectangle(
                [(padding, y), (total_width - padding, y + day_header_height)],
                fill=day_header_bg, outline=border_color
            )
            draw.text((padding + cell_padding, y + cell_padding + 5), day_header_text, fill=day_header_fg, font=day_header_font)
            y += day_header_height
            
            # Draw activities for this day
            for idx, activity in enumerate(activities):
                bg_color = row_bg_even if idx % 2 == 0 else row_bg_odd
                draw.rectangle(
                    [(padding, y), (total_width - padding, y + row_height)],
                    fill=bg_color, outline=border_color
                )
                
                x = padding
                # Proyecto/Area
                proyecto = activity.get("proyecto_area", "")
                draw.text((x + cell_padding, y + cell_padding), proyecto, fill=text_color, font=body_font)
                x += col_widths[0]
                
                # Avance
                avance = activity.get("avance", "")
                draw.text((x + cell_padding, y + cell_padding), avance, fill=text_color, font=body_font)
                x += col_widths[1]
                
                # Impacto
                impacto = activity.get("impacto", "")
                draw.text((x + cell_padding, y + cell_padding), impacto, fill=text_color, font=body_font)
                x += col_widths[2]
                
                # Estado
                estado = activity.get("estado", "pendiente")
                draw.text((x + cell_padding, y + cell_padding), estado, fill=text_color, font=body_font)
                
                y += row_height
        
        # Draw summary
        draw.text((padding + 10, y + 10), f"Total: {total_count} activities", fill=text_color, font=summary_font)
        
        return img
    
    def export_to_csv(self):
        """Export activities to CSV"""
        try:
            activities = self.storage.load_activities(self.selected_date)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load activities: {e}")
            return
        
        if not activities:
            messagebox.showwarning("No Activities", "No activities to export!")
            return
        
        date_for_file = self.selected_date
        if len(date_for_file) == 8 and "/" in date_for_file:
            date_obj = datetime.strptime(self.selected_date, "%m/%d/%y")
            date_for_file = date_obj.strftime("%Y-%m-%d")
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"logbook_{date_for_file}.csv"
        )
        
        if not file_path:
            return
        
        try:
            self.storage.export_to_csv(self.selected_date, file_path)
            messagebox.showinfo("Success", f"Exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")
    
    def clear_today(self):
        """Clear all activities for selected date"""
        if messagebox.askyesno("Confirm", "Clear all activities for this date?"):
            try:
                self.storage.clear_date(self.selected_date)
                self.load_activities()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear activities: {e}")
    
    def view_by_week(self):
        """Display all activities for the week"""
        try:
            activities_dict = self.storage.get_activities_by_week(self.selected_date)
            date_obj = datetime.strptime(self.selected_date, "%Y-%m-%d")
            from datetime import timedelta
            start_of_week = date_obj - timedelta(days=date_obj.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            title = f"Week View: {start_of_week.strftime('%B %d')} - {end_of_week.strftime('%B %d, %Y')}"
            self._show_view_window(title, activities_dict)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load week activities: {e}")
    
    def view_by_month(self):
        """Display all activities for the month"""
        try:
            date_obj = datetime.strptime(self.selected_date, "%Y-%m-%d")
            activities_dict = self.storage.get_activities_by_month(date_obj.year, date_obj.month)
            title = f"Month View: {date_obj.strftime('%B %Y')}"
            self._show_view_window(title, activities_dict)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load month activities: {e}")
    
    def _show_view_window(self, title, activities_dict):
        """Show a window with activities in a table format"""
        view_window = tk.Toplevel(self.root)
        view_window.title(title)
        view_window.geometry("900x600")
        view_window.transient(self.root)
        
        # Create frame
        frame = ttk.Frame(view_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add title label
        title_label = ttk.Label(frame, text=title, font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Check if there are activities
        if not activities_dict:
            ttk.Label(frame, text="No activities found for this period.", font=("Arial", 11)).pack(pady=20)
            ttk.Button(view_window, text="Close", command=view_window.destroy).pack(pady=10)
            return
        
        # Create table frame with scrollbar
        table_frame = ttk.Frame(frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create Treeview
        columns = ("Proyecto/Area", "Avance", "Impacto", "Estado")
        tree = ttk.Treeview(table_frame, columns=columns, show="tree headings", yscrollcommand=scrollbar.set)
        
        tree.column("#0", anchor=tk.W, width=200)
        tree.column("Proyecto/Area", anchor=tk.W, width=150)
        tree.column("Avance", anchor=tk.W, width=150)
        tree.column("Impacto", anchor=tk.W, width=150)
        tree.column("Estado", anchor=tk.W, width=150)
        
        tree.heading("#0", text="Date")
        tree.heading("Proyecto/Area", text="Proyecto/Area")
        tree.heading("Avance", text="Avance")
        tree.heading("Impacto", text="Impacto")
        tree.heading("Estado", text="Estado")
        
        scrollbar.config(command=tree.yview)
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Populate table with day groupings
        total_count = 0
        for date_str, activities in sorted(activities_dict.items()):
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%m/%d/%Y")
            day_name = date_obj.strftime("%A")
            
            # Insert day header as parent
            day_header = f"{day_name}, {date_obj.strftime('%B %d, %Y')}"
            parent = tree.insert("", tk.END, text=day_header, values=("", "", ""), tags=("header",))
            
            # Insert activities under the day header
            for activity in activities:
                tree.insert(parent, tk.END, text="", values=(
                    activity.get("proyecto_area", ""),
                    activity.get("avance", ""),
                    activity.get("impacto", ""),
                    activity.get("estado", "pendiente")
                ))
                total_count += 1
        
        # Style the header rows
        tree.tag_configure("header", font=("Arial", 10, "bold"))
        
        # Add summary label
        summary_label = ttk.Label(frame, text=f"Total: {total_count} activities", font=("Arial", 10))
        summary_label.pack(pady=(10, 0))
        
        # Add button frame
        button_frame = ttk.Frame(view_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def copy_as_text():
            """Copy table content as formatted text"""
            lines = []
            lines.append(title)
            lines.append("=" * 80)
            lines.append("")
            
            for date_str, activities in sorted(activities_dict.items()):
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                lines.append(f"--- {date_obj.strftime('%A, %B %d, %Y')} ---")
                for activity in activities:
                    lines.append(f"  {activity['time']} - {activity['text']}")
                    if activity.get('description'):
                        lines.append(f"    Description: {activity['description']}")
                lines.append("")
            
            lines.append(f"Total: {total_count} activities")
            content = "\n".join(lines)
            
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.root.update()
            messagebox.showinfo("Copied", "Content copied to clipboard!")
            
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.root.update()
            messagebox.showinfo("Copied", "Content copied to clipboard!")
        
        def export_to_csv():
            """Export table to CSV"""
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"logbook_{title.replace(' ', '_').replace(':', '')}.csv"
            )
            
            if not file_path:
                return
            
            try:
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Date", "Proyecto/Area", "Avance", "Impacto", "Estado"])
                    
                    for date_str, activities in sorted(activities_dict.items()):
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        day_header = f"{date_obj.strftime('%A, %B %d, %Y')}"
                        
                        # Write day header row
                        writer.writerow([day_header, "", "", "", ""])
                        
                        # Write activities for this day
                        for activity in activities:
                            writer.writerow([
                                "",
                                activity.get("proyecto_area", ""),
                                activity.get("avance", ""),
                                activity.get("impacto", ""),
                                activity.get("estado", "pendiente")
                            ])
                        
                        # Add blank row between days
                        writer.writerow(["", "", "", "", ""])
                
                messagebox.showinfo("Success", f"Exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
        
        def copy_as_image():
            """Copy table as image"""
            try:
                img = self._create_multi_day_table_image(title, activities_dict, total_count)
                self._copy_image_to_clipboard(img)
                messagebox.showinfo("Copied", "Table image copied to clipboard!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy image: {e}")
        
        ttk.Button(button_frame, text="Copy as Image", command=copy_as_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Copy as Text", command=copy_as_text).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Export as CSV", command=export_to_csv).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Close", command=view_window.destroy).pack(side=tk.RIGHT)
