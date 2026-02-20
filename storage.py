import json
import csv
from pathlib import Path
from datetime import datetime, timedelta


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
    
    def add_activity(self, date_str, proyecto_area, avance, impacto, estado="pendiente"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        activities = self.load_activities(date_str)
        
        activity_data = {
            "time": timestamp,
            "proyecto_area": proyecto_area,
            "avance": avance,
            "impacto": impacto,
            "estado": estado
        }
        
        activities.append(activity_data)
        self.save_activities(date_str, activities)
    
    def update_activity(self, date_str, activity_time, proyecto_area, avance, impacto, estado="pendiente"):
        activities = self.load_activities(date_str)
        activity = next((a for a in activities if a["time"] == activity_time), None)
        
        if activity:
            activity["proyecto_area"] = proyecto_area
            activity["avance"] = avance
            activity["impacto"] = impacto
            activity["estado"] = estado
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
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Time", "Proyecto/Area", "Avance", "Impacto", "Estado"])
            
            for activity in activities:
                writer.writerow([
                    date_str,
                    activity["time"],
                    activity.get("proyecto_area", ""),
                    activity.get("avance", ""),
                    activity.get("impacto", ""),
                    activity.get("estado", "pendiente")
                ])
    
    def get_activities_by_date_range(self, start_date, end_date):
        """Get all activities within a date range (inclusive)"""
        all_activities = {}
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            activities = self.load_activities(date_str)
            if activities:
                all_activities[date_str] = activities
            current_date += timedelta(days=1)
        
        return all_activities
    
    def get_activities_by_week(self, date_str):
        """Get all activities for the week containing the given date (Monday-Sunday)"""
        if len(date_str) == 8 and "/" in date_str:
            date_obj = datetime.strptime(date_str, "%m/%d/%y")
        else:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Find Monday of the week
        start_of_week = date_obj - timedelta(days=date_obj.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        return self.get_activities_by_date_range(start_of_week, end_of_week)
    
    def get_activities_by_month(self, year, month):
        """Get all activities for a specific month"""
        start_date = datetime(year, month, 1)
        
        # Get last day of month
        if month == 12:
            end_date = datetime(year, 12, 31)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        return self.get_activities_by_date_range(start_date, end_date)
    
    def print_activities_by_week(self, date_str):
        """Print all activities for the week containing the given date"""
        activities_dict = self.get_activities_by_week(date_str)
        
        if not activities_dict:
            return "No activities found for this week."
        
        # Parse the date to determine week range
        if len(date_str) == 8 and "/" in date_str:
            date_obj = datetime.strptime(date_str, "%m/%d/%y")
        else:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        
        start_of_week = date_obj - timedelta(days=date_obj.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        output = f"\n=== Week of {start_of_week.strftime('%B %d, %Y')} to {end_of_week.strftime('%B %d, %Y')} ===\n\n"
        
        for date_str, activities in sorted(activities_dict.items()):
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            output += f"--- {date_obj.strftime('%A, %B %d, %Y')} ---\n"
            
            for activity in activities:
                output += f"  {activity['time']} - {activity.get('proyecto_area', 'N/A')}"
                output += f" | Avance: {activity.get('avance', '')} | Impacto: {activity.get('impacto', '')} | Estado: {activity.get('estado', 'pendiente')}"
                output += "\n"
            output += "\n"
        
        return output
    
    def print_activities_by_month(self, year, month):
        """Print all activities for a specific month"""
        activities_dict = self.get_activities_by_month(year, month)
        
        if not activities_dict:
            return f"No activities found for {datetime(year, month, 1).strftime('%B %Y')}."
        
        output = f"\n=== {datetime(year, month, 1).strftime('%B %Y')} ===\n\n"
        
        for date_str, activities in sorted(activities_dict.items()):
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            output += f"--- {date_obj.strftime('%A, %B %d, %Y')} ---\n"
            
            for activity in activities:
                output += f"  {activity['time']} - {activity.get('proyecto_area', 'N/A')}"
                output += f" | Avance: {activity.get('avance', '')} | Impacto: {activity.get('impacto', '')} | Estado: {activity.get('estado', 'pendiente')}"
                output += "\n"
            output += "\n"
        
        return output
