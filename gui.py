import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import subprocess
import platform

try:
    from tkcalendar import Calendar
except ImportError:
    Calendar = None


class DailyLogbookUI:
    
    def __init__(self, root, storage):
        self.root = root
        self.storage = storage     
        self.root.title("Daily Logbook")
        self.root.geometry("800x700")
        self.root.resizable(True, True)       
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.selected_date = self.today       
        self.setup_ui()
        self.load_activities()
    
    def setup_ui(self):
        """Create all UI components"""
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
        left_panel = ttk.Frame(parent, width=250)
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
        
        self._setup_insights_panel(left_panel)
    
    def _setup_insights_panel(self, parent):
        """Setup productivity insights panel"""
        insights_frame = ttk.LabelFrame(parent, text="📊 Activity Stats", padding=10)
        insights_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))       
        ttk.Label(insights_frame, text="Today:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        self.daily_count_label = ttk.Label(insights_frame, text="0 entries", font=("Arial", 9))
        self.daily_count_label.pack(anchor=tk.W, pady=(0, 5))      
        ttk.Label(insights_frame, text="This Week:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(5, 0))
        self.weekly_count_label = ttk.Label(insights_frame, text="0 entries", font=("Arial", 9))
        self.weekly_count_label.pack(anchor=tk.W, pady=(0, 10))
    
    def update_insights(self):
        """Update the insights panel with current data"""
        try:
            today_activities = self.storage.load_activities(self.today)
            today_count = len(today_activities)
            
            from datetime import timedelta
            today_date = datetime.strptime(self.today, "%Y-%m-%d")
            week_start = today_date - timedelta(days=today_date.weekday())
            week_count = 0
            
            for i in range(7):
                date = (week_start + timedelta(days=i)).strftime("%Y-%m-%d")
                week_count += len(self.storage.load_activities(date))
            
            self.daily_count_label.config(text=f"📊 {today_count} entries")
            
            self.weekly_count_label.config(text=f"📈 {week_count} entries")
            
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
        """Setup activity and description input fields"""
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Label(input_frame, text="Activity:", font=("Arial", 9)).pack(anchor=tk.W)
        self.activity_input = ttk.Entry(input_frame, font=("Arial", 11))
        self.activity_input.pack(fill=tk.X, pady=(0, 8))
        self.activity_input.bind('<Return>', lambda e: self.add_activity())
        
        ttk.Label(input_frame, text="Description (optional):", font=("Arial", 9)).pack(anchor=tk.W)
        self.description_input = ttk.Entry(input_frame, font=("Arial", 11))
        self.description_input.pack(fill=tk.X, pady=(0, 8))
        self.description_input.bind('<Return>', lambda e: self.add_activity())
        
        ttk.Button(input_frame, text="Add Activity", command=self.add_activity).pack(side=tk.LEFT)
    
    def _setup_action_buttons(self, parent):
        """Setup export and clear buttons"""
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Button(action_frame, text="Copy as Image", command=self.copy_as_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Copy as Text", command=self.copy_as_text).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Export as CSV", command=self.export_to_csv).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Clear Today", command=self.clear_today).pack(side=tk.LEFT)
    
    def _setup_activities_list(self, parent):
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        ttk.Label(list_frame, text="Activities", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        columns = ("Date", "Activity", "Description", "Actions")
        self.tree = ttk.Treeview(list_frame, columns=columns, height=12, show="tree headings")
        
        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("Date", anchor=tk.W, width=120)
        self.tree.column("Activity", anchor=tk.W, width=130)
        self.tree.column("Description", anchor=tk.W, width=130)
        self.tree.column("Actions", anchor=tk.CENTER, width=80)
        
        self.tree.heading("Date", text="Date")
        self.tree.heading("Activity", text="Activity")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Actions", text="Actions")
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Button-1>", self.on_tree_click)
    
    def on_tree_click(self, event):
        item = self.tree.identify('item', event.x, event.y)
        column = self.tree.identify_column(event.x)
        
        if not item:
            return
        
        values = self.tree.item(item)['values']
        if not values or len(values) < 2:
            return
        
        activity_text = values[1]
        description = values[2] if len(values) > 2 else ""
        
        try:
            activities = self.storage.load_activities(self.selected_date)
            activity = next((a for a in activities if a["text"] == activity_text and a.get("description", "") == description), None)
            if not activity:
                return
            activity_time = activity["time"]
        except:
            return
        
        if column == "#4":
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
        activity = self.activity_input.get().strip()
        description = self.description_input.get().strip()
        
        if not activity:
            messagebox.showwarning("Empty Activity", "Please enter an activity!")
            return
        
        try:
            self.storage.add_activity(self.selected_date, activity, description)
            self.activity_input.delete(0, tk.END)
            self.description_input.delete(0, tk.END)
            self.activity_input.focus()
            self.load_activities()
            self.update_insights()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add activity: {e}")
    
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
            self.tree.insert("", tk.END, values=("", "No activities yet", "", ""))
            self.update_insights()
            return
        
        for activity in activities:
            description = activity.get("description", "")
            self.tree.insert("", tk.END, values=(self.selected_date, activity["text"], description, "✎ ✕"))
        
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
        edit_window.geometry("400x200")
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Activity
        ttk.Label(edit_window, text="Activity:", font=("Arial", 10)).pack(anchor=tk.W, padx=15, pady=(15, 5))
        activity_var = ttk.Entry(edit_window, font=("Arial", 11))
        activity_var.insert(0, activity["text"])
        activity_var.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Description
        ttk.Label(edit_window, text="Description:", font=("Arial", 10)).pack(anchor=tk.W, padx=15, pady=(0, 5))
        description_var = ttk.Entry(edit_window, font=("Arial", 11))
        description_var.insert(0, activity.get("description", ""))
        description_var.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        def save_changes():
            new_activity = activity_var.get().strip()
            if not new_activity:
                messagebox.showwarning("Empty Activity", "Activity cannot be empty!")
                return
            
            try:
                self.storage.update_activity(
                    self.selected_date,
                    base_time,
                    new_activity,
                    description_var.get().strip()
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
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"{'Date':<10} | {'Activity':<30} | Description")
        lines.append("-" * 70)       
        for activity in activities:
            date_display = self.selected_date
            text = activity["text"][:30].ljust(30)
            desc = activity.get("description", "")[:30]
            lines.append(f"{date_display:<10} | {text} | {desc}")
        
        lines.append("")
        lines.append("=" * 70)
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
    
    def _create_table_image(self, date_str, activities):
        padding = 20
        cell_padding = 10
        row_height = 35
        header_bg = (44, 62, 80)  
        header_fg = (255, 255, 255) 
        row_bg_odd = (255, 255, 255)
        row_bg_even = (249, 249, 249)  
        border_color = (220, 220, 220)  
        text_color = (51, 51, 51) 
        title_color = (51, 51, 51)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 16)
            header_font = ImageFont.truetype("arial.ttf", 12)
            body_font = ImageFont.truetype("arial.ttf", 11)
            summary_font = ImageFont.truetype("arial.ttf", 10)
        except:
            title_font = header_font = body_font = summary_font = ImageFont.load_default()
        
        temp_img = Image.new("RGB", (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        headers = ["Date", "Activity", "Description"]
        
        col_widths = []
        for header in headers:
            bbox = temp_draw.textbbox((0, 0), header, font=header_font)
            col_widths.append(bbox[2] - bbox[0] + cell_padding * 2)
        
        for activity in activities:
            # Date column
            bbox = temp_draw.textbbox((0, 0), date_str, font=body_font)
            width = bbox[2] - bbox[0] + cell_padding * 2
            col_widths[0] = max(col_widths[0], width)
            
            # Activity
            bbox = temp_draw.textbbox((0, 0), activity["text"], font=body_font)
            width = bbox[2] - bbox[0] + cell_padding * 2
            col_widths[1] = max(col_widths[1], width)
            
            desc = activity.get("description", "")
            if desc:
                bbox = temp_draw.textbbox((0, 0), desc, font=body_font)
                width = bbox[2] - bbox[0] + cell_padding * 2
                col_widths[2] = max(col_widths[2], width)
        
        col_widths = [max(w, 100) for w in col_widths]
        
        # Calculate dimensions
        title_height = 60
        header_height = row_height
        content_height = row_height * len(activities)
        summary_height = 50
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
        headers = ["Date", "Activity", "Description"]
        draw.rectangle(
            [(padding, y), (total_width - padding, y + row_height)],
            fill=header_bg, outline=border_color
        )
        
        for i, header in enumerate(headers):
            draw.text((x + cell_padding, y + cell_padding), header, fill=header_fg, font=header_font)
            x += col_widths[i]
        
        y += row_height
        
        for idx, activity in enumerate(activities):
            bg_color = row_bg_even if idx % 2 == 0 else row_bg_odd
            draw.rectangle(
                [(padding, y), (total_width - padding, y + row_height)],
                fill=bg_color, outline=border_color
            )
            
            x = padding
            # Date
            draw.text((x + cell_padding, y + cell_padding), date_str, fill=text_color, font=body_font)
            x += col_widths[0]
            
            # Activity
            text = activity["text"]
            draw.text((x + cell_padding, y + cell_padding), text, fill=text_color, font=body_font)
            x += col_widths[1]
            
            # Description
            desc = activity.get("description", "")
            draw.text((x + cell_padding, y + cell_padding), desc, fill=text_color, font=body_font)
            
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
