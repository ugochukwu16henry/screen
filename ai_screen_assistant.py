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

def monitor_loop():
    """Background thread that monitors screen and processes OCR."""
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
    
    while RUNNING:
        try:
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
            
            # Skip if no text or unchanged
            if not current_text or current_text == LAST_SEEN_TEXT:
                time.sleep(POLL_INTERVAL)
                continue
            
            # Filter out very short or mostly non-alphanumeric text (likely OCR noise)
            clean_text = current_text.strip()
            # Count meaningful characters (letters, numbers, common punctuation)
            meaningful_chars = sum(1 for c in clean_text if c.isalnum() or c in ' .,!?;:-()[]{}')
            if len(clean_text) < 10 or meaningful_chars < len(clean_text) * 0.3:
                # Likely OCR noise, skip
                time.sleep(POLL_INTERVAL)
                continue

            # New question detected!
            LAST_SEEN_TEXT = current_text
            print(f"\n✅ New question detected:\n{clean_text[:200]}\n")  # Show first 200 chars

            # Step 2+3: Generate response and show in overlay
            thread = threading.Thread(target=ai_worker, args=(current_text,))
            thread.daemon = True
            thread.start()

            time.sleep(POLL_INTERVAL)

        except Exception as e:
            logging.error(f"Unexpected error in monitor loop: {e}")
            if OVERLAY:
                OVERLAY.update_text("⚠️ System error. Check logs.")
            time.sleep(5)

if __name__ == "__main__":
    print("🚀 Initializing AI Screen Assistant...")
    
    # Get screen dimensions for fullscreen overlay
    import tkinter as tk
    temp_root = tk.Tk()
    screen_width = temp_root.winfo_screenwidth()
    screen_height = temp_root.winfo_screenheight()
    temp_root.destroy()
    
    # Initialize overlay (Step 3) with settings - make it fullscreen
    # Access overlay settings directly from settings dict
    overlay_config = settings.settings.get("overlay", {})
    
    # Make overlay fullscreen by default
    overlay_x = overlay_config.get("x", 0)
    overlay_y = overlay_config.get("y", 0)
    overlay_width = overlay_config.get("width", screen_width)
    overlay_height = overlay_config.get("height", screen_height)
    
    # If overlay config doesn't specify fullscreen, use fullscreen
    if overlay_width < screen_width * 0.8 or overlay_height < screen_height * 0.8:
        overlay_width = screen_width
        overlay_height = screen_height
        overlay_x = 0
        overlay_y = 0
        print("📺 Using fullscreen overlay")
    
    print(f"📐 Overlay config: {overlay_x}, {overlay_y}, {overlay_width}x{overlay_height}")
    print(f"🖥️ Screen size: {screen_width}x{screen_height}")
    
    try:
        OVERLAY = AnswerOverlay(
            x=overlay_x,
            y=overlay_y,
            width=overlay_width,
            height=overlay_height,
            fullscreen=(overlay_width == screen_width and overlay_height == screen_height)
        )
        print("✅ Overlay window created")
    except Exception as e:
        print(f"❌ Error creating overlay: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    
    try:
        from overlay_display import enable_click_through_windows
        enable_click_through_windows(OVERLAY)
        print("✅ Click-through enabled")
    except Exception as e:
        print(f"⚠️ Could not enable click-through: {e}")

    # Get monitor region info
    monitor_region = settings.settings.get("monitor_region", {
        "top": 200,
        "left": 300,
        "width": 700,
        "height": 200
    })
    
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
    status_text += f"\n\n📊 Monitoring Region:"
    status_text += f"\n  Position: ({monitor_region.get('left', 0)}, {monitor_region.get('top', 0)})"
    status_text += f"\n  Size: {monitor_region.get('width', 0)}x{monitor_region.get('height', 0)}"
    status_text += f"\n\n💡 Configure region:"
    status_text += f"\n  python settings_manager.py"
    
    try:
        OVERLAY.update_text(status_text)
        OVERLAY.show()
        # Force window to front and make sure it's visible
        OVERLAY.root.lift()
        OVERLAY.root.focus_force()
        print("✅ Overlay window shown")
        print(f"📍 Overlay window: {overlay_x}, {overlay_y}, {overlay_width}x{overlay_height}")
        print(f"📊 Monitoring region: ({monitor_region.get('left', 0)}, {monitor_region.get('top', 0)}) {monitor_region.get('width', 0)}x{monitor_region.get('height', 0)}")
        print("💡 To change the monitoring region, run: python settings_manager.py")
    except Exception as e:
        print(f"❌ Error showing overlay: {e}")
        import traceback
        traceback.print_exc()

    # Handle window close event
    def on_closing():
        global RUNNING
        RUNNING = False
        OVERLAY.root.quit()
    
    OVERLAY.root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start monitoring in background thread
    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()

    # Run tkinter mainloop in main thread (required for Windows)
    # This keeps the window responsive
    try:
        # Schedule periodic updates to process queued overlay updates
        def periodic_update():
            if OVERLAY and RUNNING:
                try:
                    OVERLAY.process_updates()
                except:
                    pass
                # Schedule next update
                OVERLAY.root.after(100, periodic_update)
            elif not RUNNING:
                OVERLAY.root.quit()
        
        # Start periodic updates
        OVERLAY.root.after(100, periodic_update)
        
        # Run tkinter mainloop (this is the main event loop)
        OVERLAY.root.mainloop()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        RUNNING = False
    except Exception as e:
        logging.error(f"Error in main loop: {e}")
    finally:
        RUNNING = False
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

