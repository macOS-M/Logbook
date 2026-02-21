import json
from pathlib import Path


class SettingsManager:
    """Manages export settings for image generation"""
    
    def __init__(self):
        self.settings = self._load_settings()
    
    def _get_settings_file(self):
        """Get the path to the settings file"""
        settings_dir = Path.home() / ".logbook"
        settings_dir.mkdir(exist_ok=True)
        return settings_dir / "image_settings.json"
    
    def _load_settings(self):
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
    
    def save(self):
        """Save image export settings to file"""
        settings_file = self._get_settings_file()
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save settings: {e}")
            return False
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
    
    def update(self, updates):
        """Update multiple settings"""
        self.settings.update(updates)
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = {
            "title_font_size": 24,
            "header_font_size": 18,
            "body_font_size": 16,
            "summary_font_size": 14,
            "column_widths": [320, 280, 250, 160],
            "cell_padding": 15,
            "min_row_height": 60,
            "padding": 20
        }
        return self.settings
