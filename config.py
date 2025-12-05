"""
Configuration and Settings Management
Handles loading and saving application settings to a local JSON file.
"""
import json
import os
from pathlib import Path

# Default settings
DEFAULT_SETTINGS = {
    "note_taking": {
        "enabled": False,
        "auto_save": True,
        "save_interval": 30,  # seconds
        "notes_directory": "notes",
        "include_timestamps": True,
        "include_questions": True,
        "include_answers": True
    },
    "monitor_region": {
        "top": 200,
        "left": 300,
        "width": 700,
        "height": 200
    },
    "poll_interval": 3.0,
    "ai_model": "phi3",
    "overlay": {
        "x": 50,
        "y": 50,
        "width": 500,
        "height": 200,
        "alpha": 0.85
    },
    "voice": {
        "input_enabled": False,
        "output_enabled": False,
        "speech_rate": 150,
        "volume": 0.8,
        "speak_answers": True,
        "record_voice_notes": True
    }
}

SETTINGS_FILE = "settings.json"

class Settings:
    """Manages application settings with persistence."""
    
    def __init__(self, settings_file=SETTINGS_FILE):
        self.settings_file = settings_file
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from file or return defaults."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    settings = DEFAULT_SETTINGS.copy()
                    settings.update(loaded)
                    # Deep merge for nested dicts
                    if "note_taking" in loaded:
                        settings["note_taking"].update(loaded["note_taking"])
                    if "monitor_region" in loaded:
                        settings["monitor_region"].update(loaded["monitor_region"])
                    if "overlay" in loaded:
                        settings["overlay"].update(loaded["overlay"])
                    return settings
            except Exception as e:
                print(f"Error loading settings: {e}. Using defaults.")
                return DEFAULT_SETTINGS.copy()
        return DEFAULT_SETTINGS.copy()
    
    def save_settings(self):
        """Save current settings to file."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key_path, default=None):
        """Get a setting value using dot notation (e.g., 'note_taking.enabled')."""
        keys = key_path.split('.')
        value = self.settings
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, key_path, value):
        """Set a setting value using dot notation."""
        keys = key_path.split('.')
        settings = self.settings
        for key in keys[:-1]:
            if key not in settings:
                settings[key] = {}
            settings = settings[key]
        settings[keys[-1]] = value
    
    def is_note_taking_enabled(self):
        """Check if note-taking is enabled."""
        return self.get("note_taking.enabled", False)
    
    def get_notes_directory(self):
        """Get the notes directory path, creating it if needed."""
        notes_dir = self.get("note_taking.notes_directory", "notes")
        path = Path(notes_dir)
        path.mkdir(parents=True, exist_ok=True)
        return str(path)

# Global settings instance
settings = Settings()

