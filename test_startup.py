"""
Test script to diagnose startup issues
Tests each component individually to find what's causing the hang
"""
import time
import sys

print("🔍 Starting diagnostic tests...\n")

# Test 1: Basic imports
print("Test 1: Basic imports...")
start = time.time()
try:
    import threading
    import time as t
    import requests
    import logging
    print(f"  ✅ Basic imports: {time.time() - start:.2f}s")
except Exception as e:
    print(f"  ❌ Basic imports failed: {e}")
    sys.exit(1)

# Test 2: Config loading
print("\nTest 2: Config loading...")
start = time.time()
try:
    from config import settings
    print(f"  ✅ Config loaded: {time.time() - start:.2f}s")
except Exception as e:
    print(f"  ❌ Config failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Tkinter (overlay)
print("\nTest 3: Tkinter overlay creation...")
start = time.time()
try:
    import tkinter as tk
    temp_root = tk.Tk()
    temp_root.withdraw()  # Hide it
    screen_width = temp_root.winfo_screenwidth()
    screen_height = temp_root.winfo_screenheight()
    print(f"  ✅ Screen size: {screen_width}x{screen_height}")
    print(f"  ✅ Tkinter init: {time.time() - start:.2f}s")
    temp_root.destroy()
except Exception as e:
    print(f"  ❌ Tkinter failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Overlay display
print("\nTest 4: Overlay display module...")
start = time.time()
try:
    from overlay_display import AnswerOverlay
    print(f"  ✅ Overlay import: {time.time() - start:.2f}s")
except Exception as e:
    print(f"  ❌ Overlay import failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Screen OCR
print("\nTest 5: Screen OCR module...")
start = time.time()
try:
    from screen_ocr import capture_and_ocr
    print(f"  ✅ OCR import: {time.time() - start:.2f}s")
except Exception as e:
    print(f"  ❌ OCR import failed: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Note taker
print("\nTest 6: Note taker...")
start = time.time()
try:
    from note_taker import NoteTaker
    note_taker = NoteTaker()
    print(f"  ✅ Note taker init: {time.time() - start:.2f}s")
except Exception as e:
    print(f"  ❌ Note taker failed: {e}")
    import traceback
    traceback.print_exc()

# Test 7: Voice handler
print("\nTest 7: Voice handler...")
start = time.time()
try:
    from voice_handler import VoiceHandler
    voice_handler = VoiceHandler()
    print(f"  ✅ Voice handler init: {time.time() - start:.2f}s")
except Exception as e:
    print(f"  ❌ Voice handler failed: {e}")
    import traceback
    traceback.print_exc()

# Test 8: Actual OCR capture (this might be slow)
print("\nTest 8: OCR capture test (this may take a moment)...")
start = time.time()
try:
    from screen_ocr import capture_and_ocr
    # Test with a small region
    test_region = {"top": 0, "left": 0, "width": 100, "height": 100}
    print("  ⏳ Capturing screen region...")
    text = capture_and_ocr(test_region)
    elapsed = time.time() - start
    print(f"  ✅ OCR capture: {elapsed:.2f}s")
    if elapsed > 5:
        print(f"  ⚠️ WARNING: OCR is very slow ({elapsed:.2f}s)!")
except Exception as e:
    print(f"  ❌ OCR capture failed: {e}")
    import traceback
    traceback.print_exc()

# Test 9: Ollama connection
print("\nTest 9: Ollama connection...")
start = time.time()
try:
    import requests
    response = requests.get("http://localhost:11434/api/tags", timeout=2)
    if response.status_code == 200:
        print(f"  ✅ Ollama connected: {time.time() - start:.2f}s")
    else:
        print(f"  ⚠️ Ollama returned status {response.status_code}")
except requests.exceptions.ConnectionError:
    print(f"  ⚠️ Ollama not running (this is OK if you're not using AI)")
except Exception as e:
    print(f"  ⚠️ Ollama check failed: {e}")

print("\n" + "="*50)
print("✅ Diagnostic tests complete!")
print("="*50)
print("\nIf any test took more than 5 seconds, that's likely the issue.")
print("Check the output above to identify the slow component.")

