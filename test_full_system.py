"""
Quick test to verify all components work together without errors.
"""
import sys
import time

print("Testing system components...\n")

# Test 1: Imports
print("1. Testing imports...")
try:
    from screen_ocr import capture_and_ocr
    from overlay_display import AnswerOverlay
    from config import settings
    from note_taker import NoteTaker
    from voice_handler import VoiceHandler
    print("   ✅ All imports successful")
except Exception as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Test 2: Settings
print("\n2. Testing settings...")
try:
    model = settings.get("ai_model", "phi3")
    note_enabled = settings.get("note_taking.enabled", False)
    print(f"   ✅ Settings loaded - Model: {model}, Notes: {note_enabled}")
except Exception as e:
    print(f"   ❌ Settings error: {e}")
    sys.exit(1)

# Test 3: Overlay
print("\n3. Testing overlay...")
try:
    overlay = AnswerOverlay(x=100, y=100, width=300, height=100)
    overlay.update_text("Test message")
    print("   ✅ Overlay created and updated")
    overlay.root.destroy()
except Exception as e:
    print(f"   ❌ Overlay error: {e}")
    sys.exit(1)

# Test 4: Note Taker
print("\n4. Testing note taker...")
try:
    note_taker = NoteTaker()
    print(f"   ✅ Note taker initialized - Enabled: {note_taker.enabled}")
    if note_taker.enabled:
        note_taker.end_session()
except Exception as e:
    print(f"   ❌ Note taker error: {e}")
    sys.exit(1)

# Test 5: Voice Handler
print("\n5. Testing voice handler...")
try:
    voice_handler = VoiceHandler()
    print(f"   ✅ Voice handler initialized")
    print(f"      Input enabled: {voice_handler.voice_input_enabled}")
    print(f"      Output enabled: {voice_handler.voice_output_enabled}")
    voice_handler.cleanup()
except Exception as e:
    print(f"   ❌ Voice handler error: {e}")
    sys.exit(1)

# Test 6: AI Connection
print("\n6. Testing AI connection...")
try:
    import requests
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code == 200:
        print("   ✅ Ollama server is accessible")
    else:
        print(f"   ⚠️  Ollama responded with status {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ⚠️  Ollama server not running (this is OK if you're not using AI)")
except Exception as e:
    print(f"   ⚠️  AI connection check error: {e}")

print("\n" + "="*50)
print("✅ All component tests passed!")
print("="*50)
print("\nSystem is ready to use. Run 'python ai_screen_assistant.py' to start.")


