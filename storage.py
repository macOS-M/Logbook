import json
import csv
from pathlib import Path
from datetime import datetime


class DataStorage:
    
    def __init__(self):
        self.data_dir = Path.home() / ".logbook"
        self.data_dir.mkdir(exist_ok=True)
    
    def get_data_file(self, date_str):
        if len(date_str) == 8 and "/" in date_str:
            date_obj = datetime.strptime(date_str, "%m/%d/%y")
            date_str = date_obj.strftime("%Y-%m-%d")
        
        return self.data_dir / f"logbook_{date_str}.json"
    
    def load_activities(self, date_str):
        data_file = self.get_data_file(date_str)
        
        if data_file.exists():
            with open(data_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_activities(self, date_str, activities):
        data_file = self.get_data_file(date_str)
        
        with open(data_file, 'w') as f:
            json.dump(activities, f, indent=2)
    
    def add_activity(self, date_str, activity_text, description=""):
        timestamp = datetime.now().strftime("%H:%M:%S")
        activities = self.load_activities(date_str)
        
        activity_data = {
            "time": timestamp,
            "text": activity_text,
            "description": description
        }
        
        activities.append(activity_data)
        self.save_activities(date_str, activities)
    
    def update_activity(self, date_str, activity_time, activity_text, description=""):
        activities = self.load_activities(date_str)
        activity = next((a for a in activities if a["time"] == activity_time), None)
        
        if activity:
            activity["text"] = activity_text
            activity["description"] = description
            self.save_activities(date_str, activities)
    
    def delete_activity(self, date_str, activity_time):
        activities = self.load_activities(date_str)
        activities = [a for a in activities if a["time"] != activity_time]
        self.save_activities(date_str, activities)
    
    def clear_date(self, date_str):
        data_file = self.get_data_file(date_str)
        
        if data_file.exists():
            data_file.unlink()
    
    def export_to_csv(self, date_str, file_path):
        activities = self.load_activities(date_str)
        
        if not activities:
            raise ValueError("No activities to export")
        
        if len(date_str) == 8 and "/" in date_str:
            date_obj = datetime.strptime(date_str, "%m/%d/%y")
            date_str = date_obj.strftime("%Y-%m-%d")
        
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Time", "Activity", "Description"])
            
            for activity in activities:
                writer.writerow([
                    date_str,
                    activity["time"],
                    activity["text"],
                    activity.get("description", "")
                ])
