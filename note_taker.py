"""
Note-Taking Module
Captures and saves notes during meetings with timestamps and context.
"""
import os
import json
from datetime import datetime
from pathlib import Path
from threading import Lock
from config import settings

class NoteTaker:
    """Manages note-taking functionality with auto-save capabilities."""
    
    def __init__(self):
        self.enabled = settings.is_note_taking_enabled()
        self.notes_directory = settings.get_notes_directory()
        self.current_session_file = None
        self.notes_buffer = []
        self.lock = Lock()
        self.session_start_time = None
        self.last_save_time = datetime.now()
        self.save_interval = settings.get("note_taking.save_interval", 30)
        
        if self.enabled:
            self.start_session()
    
    def start_session(self):
        """Start a new note-taking session."""
        if not self.enabled:
            return
        
        self.session_start_time = datetime.now()
        timestamp = self.session_start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"meeting_notes_{timestamp}.md"
        self.current_session_file = os.path.join(self.notes_directory, filename)
        
        # Create initial note file with header
        header = f"""# Meeting Notes
**Date:** {self.session_start_time.strftime("%Y-%m-%d %H:%M:%S")}
**Session Started:** {self.session_start_time.strftime("%H:%M:%S")}

---

"""
        with open(self.current_session_file, 'w', encoding='utf-8') as f:
            f.write(header)
        
        print(f"📝 Note-taking started: {self.current_session_file}")
    
    def add_note(self, content, note_type="general", question=None, answer=None):
        """Add a note to the current session."""
        if not self.enabled or not self.current_session_file:
            return
        
        with self.lock:
            timestamp = datetime.now().strftime("%H:%M:%S")
            note_entry = {
                "timestamp": timestamp,
                "type": note_type,
                "content": content,
                "question": question,
                "answer": answer
            }
            self.notes_buffer.append(note_entry)
            
            # Auto-save if interval has passed
            now = datetime.now()
            if (now - self.last_save_time).total_seconds() >= self.save_interval:
                self.save_notes()
    
    def add_qa_note(self, question, answer):
        """Add a question-answer pair to notes."""
        if not self.enabled:
            return
        
        include_questions = settings.get("note_taking.include_questions", True)
        include_answers = settings.get("note_taking.include_answers", True)
        
        if include_questions and include_answers:
            content = f"**Q:** {question}\n**A:** {answer}"
        elif include_questions:
            content = f"**Q:** {question}"
        elif include_answers:
            content = f"**A:** {answer}"
        else:
            return
        
        self.add_note(content, note_type="qa", question=question, answer=answer)
    
    def add_screen_text(self, text):
        """Add captured screen text to notes."""
        if not self.enabled:
            return
        
        # Only add if text is meaningful (not empty, not too short)
        if text and len(text.strip()) > 10:
            self.add_note(text, note_type="screen_capture")
    
    def add_voice_note(self, text):
        """Add a voice note to the session."""
        if not self.enabled:
            return
        
        if text and len(text.strip()) > 0:
            self.add_note(f"**Voice Note:** {text}", note_type="voice")
    
    def save_notes(self):
        """Save buffered notes to file."""
        if not self.enabled or not self.current_session_file or not self.notes_buffer:
            return
        
        with self.lock:
            try:
                with open(self.current_session_file, 'a', encoding='utf-8') as f:
                    for note in self.notes_buffer:
                        include_timestamps = settings.get("note_taking.include_timestamps", True)
                        
                        if note["type"] == "qa":
                            if include_timestamps:
                                f.write(f"\n### [{note['timestamp']}] Q&A\n\n")
                            else:
                                f.write(f"\n### Q&A\n\n")
                            f.write(f"{note['content']}\n")
                        elif note["type"] == "screen_capture":
                            if include_timestamps:
                                f.write(f"\n### [{note['timestamp']}] Screen Capture\n\n")
                            else:
                                f.write(f"\n### Screen Capture\n\n")
                            f.write(f"{note['content']}\n")
                        elif note["type"] == "voice":
                            if include_timestamps:
                                f.write(f"\n### [{note['timestamp']}] Voice Note\n\n")
                            else:
                                f.write(f"\n### Voice Note\n\n")
                            f.write(f"{note['content']}\n")
                        else:
                            if include_timestamps:
                                f.write(f"\n### [{note['timestamp']}] Note\n\n")
                            else:
                                f.write(f"\n### Note\n\n")
                            f.write(f"{note['content']}\n")
                        f.write("\n---\n")
                
                self.notes_buffer.clear()
                self.last_save_time = datetime.now()
                print(f"💾 Notes saved to {self.current_session_file}")
            except Exception as e:
                print(f"Error saving notes: {e}")
    
    def end_session(self):
        """End the current session and save all notes."""
        if not self.enabled:
            return
        
        self.save_notes()
        
        if self.current_session_file:
            # Add session end time
            end_time = datetime.now()
            duration = end_time - self.session_start_time if self.session_start_time else None
            
            with open(self.current_session_file, 'a', encoding='utf-8') as f:
                f.write(f"\n\n---\n\n")
                f.write(f"**Session Ended:** {end_time.strftime('%H:%M:%S')}\n")
                if duration:
                    f.write(f"**Duration:** {str(duration).split('.')[0]}\n")
            
            print(f"📝 Note-taking session ended: {self.current_session_file}")
            self.current_session_file = None
    
    def enable(self):
        """Enable note-taking."""
        self.enabled = True
        settings.set("note_taking.enabled", True)
        settings.save_settings()
        self.start_session()
    
    def disable(self):
        """Disable note-taking and save current session."""
        if self.enabled:
            self.end_session()
        self.enabled = False
        settings.set("note_taking.enabled", False)
        settings.save_settings()

