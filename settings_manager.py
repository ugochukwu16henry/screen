"""
Settings Manager - GUI for managing application settings
Allows users to toggle note-taking and configure other options.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from config import settings

class SettingsWindow:
    """GUI window for managing application settings."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Assistant Settings")
        self.root.geometry("500x750")
        self.root.resizable(False, False)
        
        self.create_widgets()
        self.load_current_settings()
    
    def create_widgets(self):
        """Create the settings UI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="AI Assistant Settings", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Note-Taking Section
        note_frame = ttk.LabelFrame(main_frame, text="Note-Taking", padding="10")
        note_frame.pack(fill="x", pady=5)
        
        self.note_enabled = tk.BooleanVar()
        note_check = ttk.Checkbutton(note_frame, text="Enable Note-Taking", 
                                    variable=self.note_enabled,
                                    command=self.on_note_toggle)
        note_check.pack(anchor="w", pady=5)
        
        # Note-taking options (disabled when note-taking is off)
        self.note_options_frame = ttk.Frame(note_frame)
        self.note_options_frame.pack(fill="x", pady=5)
        
        self.include_timestamps = tk.BooleanVar()
        ttk.Checkbutton(self.note_options_frame, text="Include Timestamps",
                       variable=self.include_timestamps).pack(anchor="w", pady=2)
        
        self.include_questions = tk.BooleanVar()
        ttk.Checkbutton(self.note_options_frame, text="Include Questions",
                       variable=self.include_questions).pack(anchor="w", pady=2)
        
        self.include_answers = tk.BooleanVar()
        ttk.Checkbutton(self.note_options_frame, text="Include Answers",
                       variable=self.include_answers).pack(anchor="w", pady=2)
        
        ttk.Label(self.note_options_frame, text="Auto-save Interval (seconds):").pack(anchor="w", pady=(5, 2))
        self.save_interval = tk.StringVar()
        ttk.Entry(self.note_options_frame, textvariable=self.save_interval, width=10).pack(anchor="w", pady=2)
        
        ttk.Label(self.note_options_frame, text="Notes Directory:").pack(anchor="w", pady=(5, 2))
        self.notes_directory = tk.StringVar()
        ttk.Entry(self.note_options_frame, textvariable=self.notes_directory, width=40).pack(anchor="w", pady=2)
        
        # Monitor Region Section
        monitor_frame = ttk.LabelFrame(main_frame, text="Screen Capture Region", padding="10")
        monitor_frame.pack(fill="x", pady=5)
        
        ttk.Label(monitor_frame, text="Top:").grid(row=0, column=0, sticky="w", pady=2)
        self.monitor_top = tk.StringVar()
        ttk.Entry(monitor_frame, textvariable=self.monitor_top, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(monitor_frame, text="Left:").grid(row=0, column=2, sticky="w", padx=(10, 0), pady=2)
        self.monitor_left = tk.StringVar()
        ttk.Entry(monitor_frame, textvariable=self.monitor_left, width=10).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(monitor_frame, text="Width:").grid(row=1, column=0, sticky="w", pady=2)
        self.monitor_width = tk.StringVar()
        ttk.Entry(monitor_frame, textvariable=self.monitor_width, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(monitor_frame, text="Height:").grid(row=1, column=2, sticky="w", padx=(10, 0), pady=2)
        self.monitor_height = tk.StringVar()
        ttk.Entry(monitor_frame, textvariable=self.monitor_height, width=10).grid(row=1, column=3, padx=5, pady=2)
        
        # Other Settings
        other_frame = ttk.LabelFrame(main_frame, text="Other Settings", padding="10")
        other_frame.pack(fill="x", pady=5)
        
        ttk.Label(other_frame, text="Poll Interval (seconds):").pack(anchor="w", pady=2)
        self.poll_interval = tk.StringVar()
        ttk.Entry(other_frame, textvariable=self.poll_interval, width=10).pack(anchor="w", pady=2)
        
        ttk.Label(other_frame, text="AI Model:").pack(anchor="w", pady=(5, 2))
        self.ai_model = tk.StringVar()
        model_combo = ttk.Combobox(other_frame, textvariable=self.ai_model, width=20)
        model_combo['values'] = ('phi3', 'llama3', 'mistral', 'gemma', 'qwen')
        model_combo.pack(anchor="w", pady=2)
        
        # Voice Settings Section
        voice_frame = ttk.LabelFrame(main_frame, text="Voice Features", padding="10")
        voice_frame.pack(fill="x", pady=5)
        
        self.voice_input_enabled = tk.BooleanVar()
        voice_input_check = ttk.Checkbutton(voice_frame, text="Enable Voice Input (Speech-to-Text)",
                                           variable=self.voice_input_enabled,
                                           command=self.on_voice_toggle)
        voice_input_check.pack(anchor="w", pady=5)
        
        self.voice_output_enabled = tk.BooleanVar()
        voice_output_check = ttk.Checkbutton(voice_frame, text="Enable Voice Output (Text-to-Speech)",
                                            variable=self.voice_output_enabled)
        voice_output_check.pack(anchor="w", pady=5)
        
        # Voice options
        self.voice_options_frame = ttk.Frame(voice_frame)
        self.voice_options_frame.pack(fill="x", pady=5)
        
        self.speak_answers = tk.BooleanVar()
        ttk.Checkbutton(self.voice_options_frame, text="Speak AI Answers",
                       variable=self.speak_answers).pack(anchor="w", pady=2)
        
        self.record_voice_notes = tk.BooleanVar()
        ttk.Checkbutton(self.voice_options_frame, text="Record Voice Notes",
                       variable=self.record_voice_notes).pack(anchor="w", pady=2)
        
        ttk.Label(self.voice_options_frame, text="Speech Rate (words/min):").pack(anchor="w", pady=(5, 2))
        self.speech_rate = tk.StringVar()
        ttk.Entry(self.voice_options_frame, textvariable=self.speech_rate, width=10).pack(anchor="w", pady=2)
        
        ttk.Label(self.voice_options_frame, text="Volume (0.0-1.0):").pack(anchor="w", pady=(5, 2))
        self.volume = tk.StringVar()
        ttk.Entry(self.voice_options_frame, textvariable=self.volume, width=10).pack(anchor="w", pady=2)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=20)
        
        ttk.Button(button_frame, text="Save Settings", 
                  command=self.save_settings).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", 
                  command=self.reset_defaults).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Close", 
                  command=self.root.destroy).pack(side="right", padx=5)
    
    def load_current_settings(self):
        """Load current settings into the UI."""
        # Note-taking
        self.note_enabled.set(settings.get("note_taking.enabled", False))
        self.include_timestamps.set(settings.get("note_taking.include_timestamps", True))
        self.include_questions.set(settings.get("note_taking.include_questions", True))
        self.include_answers.set(settings.get("note_taking.include_answers", True))
        self.save_interval.set(str(settings.get("note_taking.save_interval", 30)))
        self.notes_directory.set(settings.get("note_taking.notes_directory", "notes"))
        
        # Monitor region
        monitor = settings.get("monitor_region", {})
        self.monitor_top.set(str(monitor.get("top", 200)))
        self.monitor_left.set(str(monitor.get("left", 300)))
        self.monitor_width.set(str(monitor.get("width", 700)))
        self.monitor_height.set(str(monitor.get("height", 200)))
        
        # Other
        self.poll_interval.set(str(settings.get("poll_interval", 3.0)))
        self.ai_model.set(settings.get("ai_model", "phi3"))
        
        # Voice settings
        self.voice_input_enabled.set(settings.get("voice.input_enabled", False))
        self.voice_output_enabled.set(settings.get("voice.output_enabled", False))
        self.speak_answers.set(settings.get("voice.speak_answers", True))
        self.record_voice_notes.set(settings.get("voice.record_voice_notes", True))
        self.speech_rate.set(str(settings.get("voice.speech_rate", 150)))
        self.volume.set(str(settings.get("voice.volume", 0.8)))
        
        self.on_note_toggle()
    
    def on_note_toggle(self):
        """Enable/disable note-taking options based on checkbox."""
        enabled = self.note_enabled.get()
        for widget in self.note_options_frame.winfo_children():
            widget.configure(state="normal" if enabled else "disabled")
    
    def on_voice_toggle(self):
        """Enable/disable voice options based on checkbox."""
        # Voice options are always enabled, but this can be used for validation
        pass
    
    def save_settings(self):
        """Save settings from UI to config file."""
        try:
            # Note-taking
            settings.set("note_taking.enabled", self.note_enabled.get())
            settings.set("note_taking.include_timestamps", self.include_timestamps.get())
            settings.set("note_taking.include_questions", self.include_questions.get())
            settings.set("note_taking.include_answers", self.include_answers.get())
            settings.set("note_taking.save_interval", int(self.save_interval.get()))
            settings.set("note_taking.notes_directory", self.notes_directory.get())
            
            # Monitor region
            settings.set("monitor_region.top", int(self.monitor_top.get()))
            settings.set("monitor_region.left", int(self.monitor_left.get()))
            settings.set("monitor_region.width", int(self.monitor_width.get()))
            settings.set("monitor_region.height", int(self.monitor_height.get()))
            
            # Other
            settings.set("poll_interval", float(self.poll_interval.get()))
            settings.set("ai_model", self.ai_model.get())
            
            # Voice settings
            settings.set("voice.input_enabled", self.voice_input_enabled.get())
            settings.set("voice.output_enabled", self.voice_output_enabled.get())
            settings.set("voice.speak_answers", self.speak_answers.get())
            settings.set("voice.record_voice_notes", self.record_voice_notes.get())
            settings.set("voice.speech_rate", int(self.speech_rate.get()))
            settings.set("voice.volume", float(self.volume.get()))
            
            if settings.save_settings():
                messagebox.showinfo("Success", "Settings saved successfully!")
            else:
                messagebox.showerror("Error", "Failed to save settings.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving settings: {e}")
    
    def reset_defaults(self):
        """Reset all settings to defaults."""
        if messagebox.askyesno("Confirm", "Reset all settings to defaults?"):
            from config import DEFAULT_SETTINGS
            settings.settings = DEFAULT_SETTINGS.copy()
            settings.save_settings()
            self.load_current_settings()
            messagebox.showinfo("Success", "Settings reset to defaults!")
    
    def run(self):
        """Start the settings window."""
        self.root.mainloop()

if __name__ == "__main__":
    app = SettingsWindow()
    app.run()

