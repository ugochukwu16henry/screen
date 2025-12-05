import threading
import time
import requests
import logging
import atexit
from screen_ocr import capture_and_ocr  # From Step 1
from overlay_display import AnswerOverlay  # From Step 3
from config import settings
from note_taker import NoteTaker
from voice_handler import VoiceHandler

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration from settings
MONITOR_REGION = settings.get("monitor_region", {"top": 200, "left": 300, "width": 700, "height": 200})
POLL_INTERVAL = settings.get("poll_interval", 3.0)
AI_MODEL = settings.get("ai_model", "phi3")

LAST_SEEN_TEXT = ""
OVERLAY = None
RUNNING = True
NOTE_TAKER = NoteTaker()  # Initialize note-taking system
VOICE_HANDLER = VoiceHandler()  # Initialize voice handler

# Register cleanup function
def cleanup():
    """Cleanup on exit."""
    if NOTE_TAKER:
        NOTE_TAKER.end_session()
    if VOICE_HANDLER:
        VOICE_HANDLER.cleanup()

atexit.register(cleanup)

def generate_ai_response(prompt: str) -> str:
    """Sends prompt to local Ollama and returns response."""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": AI_MODEL,
                "prompt": f"Answer concisely: {prompt}",
                "stream": False,
                "options": {"temperature": 0.2, "num_ctx": 512}
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            return "[AI Error] Failed to generate response."
    except Exception as e:
        return f"[AI Offline] {str(e)}"

def ai_worker(question: str):
    """Runs in background thread to avoid freezing overlay."""
    global OVERLAY, NOTE_TAKER, VOICE_HANDLER
    if OVERLAY:
        OVERLAY.update_text("🤖 Thinking...")
        answer = generate_ai_response(question)
        OVERLAY.update_text(f"❓ {question}\n\n💡 {answer}")
        
        # Save to notes if note-taking is enabled
        NOTE_TAKER.add_qa_note(question, answer)
        
        # Speak the answer if voice output is enabled
        if VOICE_HANDLER.voice_output_enabled and settings.get("voice.speak_answers", True):
            VOICE_HANDLER.speak_async(answer)

def voice_input_callback(text):
    """Callback for voice input - processes spoken text."""
    global NOTE_TAKER, VOICE_HANDLER
    print(f"🎤 Voice input: {text}")
    
    # Save voice note if enabled
    if NOTE_TAKER.enabled and settings.get("voice.record_voice_notes", True):
        NOTE_TAKER.add_voice_note(text)
    
    # Optionally process voice input as a question
    # (You can enable this if you want voice commands/questions)

def main_loop():
    global LAST_SEEN_TEXT, OVERLAY, RUNNING, NOTE_TAKER, VOICE_HANDLER
    note_status = "enabled" if NOTE_TAKER.enabled else "disabled"
    voice_input_status = "enabled" if VOICE_HANDLER.voice_input_enabled else "disabled"
    voice_output_status = "enabled" if VOICE_HANDLER.voice_output_enabled else "disabled"
    
    print(f"🔍 Starting AI Screen Assistant (Press Ctrl+C to quit)...")
    print(f"📝 Note-taking: {note_status}")
    print(f"🎤 Voice input: {voice_input_status}")
    print(f"🔊 Voice output: {voice_output_status}")
    if NOTE_TAKER.enabled:
        print(f"📁 Notes directory: {NOTE_TAKER.notes_directory}")
    
    # Start voice listening if enabled
    if VOICE_HANDLER.voice_input_enabled:
        VOICE_HANDLER.start_listening(callback=voice_input_callback)
    
    while True:
        try:
            if not RUNNING:
                time.sleep(1)
                continue
                
            # Step 1: Capture and extract text
            current_text = capture_and_ocr(MONITOR_REGION)
            
            # Save screen text to notes if enabled (even if unchanged, for context)
            if NOTE_TAKER.enabled and current_text:
                NOTE_TAKER.add_screen_text(current_text)
            
            # Check for voice input (non-blocking)
            if VOICE_HANDLER.voice_input_enabled:
                voice_text = VOICE_HANDLER.get_voice_input(timeout=0.1)
                if voice_text:
                    voice_input_callback(voice_text)
            
            # Process tkinter events and pending overlay updates
            if OVERLAY:
                try:
                    OVERLAY.process_updates()  # Process queued updates from background threads
                    OVERLAY.root.update_idletasks()
                except:
                    pass
            
            # Skip if no text or unchanged
            if not current_text or current_text == LAST_SEEN_TEXT:
                time.sleep(POLL_INTERVAL)
                continue

            # New question detected!
            LAST_SEEN_TEXT = current_text
            print(f"\n✅ New question detected:\n{current_text}\n")

            # Step 2+3: Generate response and show in overlay
            thread = threading.Thread(target=ai_worker, args=(current_text,))
            thread.daemon = True
            thread.start()

            time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            if OVERLAY:
                OVERLAY.update_text("⚠️ System error. Check logs.")
            time.sleep(5)

if __name__ == "__main__":
    # Initialize overlay (Step 3) with settings
    overlay_config = settings.get("overlay", {})
    OVERLAY = AnswerOverlay(
        x=overlay_config.get("x", 50),
        y=overlay_config.get("y", 50),
        width=overlay_config.get("width", 500),
        height=overlay_config.get("height", 200)
    )
    try:
        from overlay_display import enable_click_through_windows
        enable_click_through_windows(OVERLAY)
    except:
        pass

    # Update overlay with status
    note_status = "📝 Notes ON" if NOTE_TAKER.enabled else "📝 Notes OFF"
    voice_status = ""
    if VOICE_HANDLER.voice_input_enabled:
        voice_status += "🎤 Voice IN "
    if VOICE_HANDLER.voice_output_enabled:
        voice_status += "🔊 Voice OUT"
    
    status_text = f"🧠 AI Assistant Ready\n{note_status}"
    if voice_status:
        status_text += f"\n{voice_status}"
    status_text += "\nMonitoring screen..."
    
    OVERLAY.update_text(status_text)
    OVERLAY.show()

    # Start main loop
    try:
        main_loop()
    except KeyboardInterrupt:
        pass
    finally:
        # Save notes before exit
        if NOTE_TAKER:
            NOTE_TAKER.end_session()
        if VOICE_HANDLER:
            VOICE_HANDLER.cleanup()
        if OVERLAY:
            try:
                OVERLAY.root.quit()
            except:
                pass
            try:
                OVERLAY.root.destroy()
            except:
                pass

