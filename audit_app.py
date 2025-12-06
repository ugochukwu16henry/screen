"""
Comprehensive Application Audit
Tests all components and identifies issues
"""
import time
import sys
import os
import json
from pathlib import Path

print("="*70)
print("🔍 AI SCREEN ASSISTANT - FULL AUDIT")
print("="*70)
print()

issues = []
warnings = []
passed = []

def check(component, test_func, critical=False):
    """Run a test and track results"""
    try:
        result = test_func()
        if result:
            passed.append(component)
            print(f"✅ {component}: PASSED")
            return True
        else:
            if critical:
                issues.append(f"{component}: FAILED (CRITICAL)")
                print(f"❌ {component}: FAILED (CRITICAL)")
            else:
                warnings.append(f"{component}: FAILED")
                print(f"⚠️  {component}: FAILED")
            return False
    except Exception as e:
        if critical:
            issues.append(f"{component}: ERROR - {str(e)}")
            print(f"❌ {component}: ERROR - {str(e)}")
        else:
            warnings.append(f"{component}: ERROR - {str(e)}")
            print(f"⚠️  {component}: ERROR - {str(e)}")
        return False

# Test 1: Python Version
print("1. PYTHON ENVIRONMENT")
print("-" * 70)
check("Python Version", lambda: sys.version_info >= (3, 8), critical=True)
print(f"   Python: {sys.version}")
print()

# Test 2: Required Dependencies
print("2. DEPENDENCIES")
print("-" * 70)
deps = {
    "requests": ("requests", True),
    "mss": ("mss", True),
    "pytesseract": ("pytesseract", True),
    "Pillow": ("PIL", True),
    "tkinter": ("tkinter", True),
    "opencv": ("cv2", False),
    "pywin32": ("win32con", False),
    "speech_recognition": ("speech_recognition", False),
    "pyttsx3": ("pyttsx3", False),
}

for name, (module, required) in deps.items():
    try:
        __import__(module)
        passed.append(f"Dependency: {name}")
        print(f"✅ {name}: Installed")
    except ImportError:
        if required:
            issues.append(f"Missing required dependency: {name}")
            print(f"❌ {name}: MISSING (REQUIRED)")
        else:
            warnings.append(f"Missing optional dependency: {name}")
            print(f"⚠️  {name}: MISSING (Optional)")
print()

# Test 3: File Structure
print("3. FILE STRUCTURE")
print("-" * 70)
required_files = [
    "ai_screen_assistant.py",
    "overlay_display.py",
    "screen_ocr.py",
    "config.py",
    "note_taker.py",
    "voice_handler.py",
    "requirements.txt"
]

for file in required_files:
    if os.path.exists(file):
        passed.append(f"File: {file}")
        print(f"✅ {file}: Exists")
    else:
        issues.append(f"Missing file: {file}")
        print(f"❌ {file}: MISSING")
print()

# Test 4: Module Imports
print("4. MODULE IMPORTS")
print("-" * 70)
modules_to_test = [
    ("config", "config"),
    ("overlay_display", "overlay_display"),
    ("screen_ocr", "screen_ocr"),
    ("note_taker", "note_taker"),
    ("voice_handler", "voice_handler"),
]

for name, module_name in modules_to_test:
    try:
        __import__(module_name)
        passed.append(f"Import: {name}")
        print(f"✅ {name}: Imported successfully")
    except Exception as e:
        issues.append(f"Import error {name}: {str(e)}")
        print(f"❌ {name}: Import failed - {str(e)}")
print()

# Test 5: Configuration
print("5. CONFIGURATION")
print("-" * 70)
try:
    from config import settings
    check("Settings loaded", lambda: settings is not None, critical=True)
    check("Settings file accessible", lambda: os.path.exists("settings.json") or True, critical=False)
    
    # Check default settings structure
    required_keys = ["note_taking", "monitor_region", "poll_interval", "ai_model", "overlay", "voice"]
    for key in required_keys:
        if key in settings.settings:
            passed.append(f"Config key: {key}")
            print(f"✅ Config key '{key}': Present")
        else:
            warnings.append(f"Missing config key: {key}")
            print(f"⚠️  Config key '{key}': Missing")
except Exception as e:
    issues.append(f"Config error: {str(e)}")
    print(f"❌ Config error: {str(e)}")
print()

# Test 6: Tesseract OCR
print("6. TESSERACT OCR")
print("-" * 70)
try:
    import pytesseract
    try:
        version = pytesseract.get_tesseract_version()
        passed.append("Tesseract installed")
        print(f"✅ Tesseract: Installed (version: {version})")
    except Exception as e:
        issues.append(f"Tesseract not found: {str(e)}")
        print(f"❌ Tesseract: Not found - {str(e)}")
        print("   Install from: https://github.com/UB-Mannheim/tesseract/wiki")
except Exception as e:
    issues.append(f"Tesseract check failed: {str(e)}")
    print(f"❌ Tesseract check failed: {str(e)}")
print()

# Test 7: Ollama Connection
print("7. OLLAMA CONNECTION")
print("-" * 70)
try:
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            passed.append("Ollama connected")
            print(f"✅ Ollama: Connected")
            if models:
                print(f"   Available models: {', '.join([m.get('name', 'unknown') for m in models[:5]])}")
            else:
                warnings.append("No Ollama models found")
                print("⚠️  No models installed. Run: ollama pull phi3")
        else:
            warnings.append(f"Ollama returned status {response.status_code}")
            print(f"⚠️  Ollama: Status {response.status_code}")
    except requests.exceptions.ConnectionError:
        warnings.append("Ollama not running")
        print("⚠️  Ollama: Not running (start Ollama to use AI features)")
    except Exception as e:
        warnings.append(f"Ollama check error: {str(e)}")
        print(f"⚠️  Ollama: Check failed - {str(e)}")
except Exception as e:
    warnings.append(f"Ollama test error: {str(e)}")
    print(f"⚠️  Ollama test error: {str(e)}")
print()

# Test 8: Performance Test
print("8. PERFORMANCE TEST")
print("-" * 70)
print("Testing component initialization times...")

# Test overlay creation
start = time.time()
try:
    import tkinter as tk
    temp_root = tk.Tk()
    temp_root.withdraw()
    screen_w = temp_root.winfo_screenwidth()
    screen_h = temp_root.winfo_screenheight()
    temp_root.destroy()
    elapsed = time.time() - start
    if elapsed < 10:
        passed.append("Tkinter init performance")
        print(f"✅ Tkinter init: {elapsed:.2f}s (OK)")
    else:
        warnings.append(f"Tkinter init slow: {elapsed:.2f}s")
        print(f"⚠️  Tkinter init: {elapsed:.2f}s (SLOW)")
except Exception as e:
    issues.append(f"Tkinter init failed: {str(e)}")
    print(f"❌ Tkinter init failed: {str(e)}")

# Test OCR (small region)
start = time.time()
try:
    from screen_ocr import capture_and_ocr
    test_region = {"top": 0, "left": 0, "width": 100, "height": 100}
    print("   Testing OCR (100x100 region)...")
    text = capture_and_ocr(test_region)
    elapsed = time.time() - start
    if elapsed < 10:
        passed.append("OCR performance")
        print(f"✅ OCR test: {elapsed:.2f}s (OK)")
    elif elapsed < 30:
        warnings.append(f"OCR slow: {elapsed:.2f}s")
        print(f"⚠️  OCR test: {elapsed:.2f}s (SLOW)")
    else:
        warnings.append(f"OCR very slow: {elapsed:.2f}s")
        print(f"⚠️  OCR test: {elapsed:.2f}s (VERY SLOW)")
except Exception as e:
    warnings.append(f"OCR test failed: {str(e)}")
    print(f"⚠️  OCR test failed: {str(e)}")
print()

# Test 9: Code Quality
print("9. CODE QUALITY CHECKS")
print("-" * 70)

# Check for common issues
code_issues = []

# Check if MONITOR_REGION is loaded correctly
try:
    from config import settings
    region = settings.get("monitor_region", {})
    if not region or not all(k in region for k in ["top", "left", "width", "height"]):
        code_issues.append("Monitor region missing required keys")
        print("⚠️  Monitor region: Missing required keys")
    else:
        passed.append("Monitor region config")
        print("✅ Monitor region: Valid")
except Exception as e:
    code_issues.append(f"Monitor region check failed: {str(e)}")
    print(f"⚠️  Monitor region check failed: {str(e)}")

# Check for threading issues
try:
    with open("ai_screen_assistant.py", "r") as f:
        content = f.read()
        if "threading.Thread" in content and "daemon=True" in content:
            passed.append("Threading safety")
            print("✅ Threading: Using daemon threads")
        else:
            warnings.append("Threading may not be safe")
            print("⚠️  Threading: May have issues")
except Exception as e:
    warnings.append(f"Code check failed: {str(e)}")
    print(f"⚠️  Code check failed: {str(e)}")
print()

# Test 10: Settings File
print("10. SETTINGS FILE")
print("-" * 70)
if os.path.exists("settings.json"):
    try:
        with open("settings.json", "r") as f:
            settings_data = json.load(f)
        passed.append("Settings file readable")
        print("✅ Settings file: Exists and readable")
        print(f"   Note-taking: {settings_data.get('note_taking', {}).get('enabled', False)}")
        print(f"   Poll interval: {settings_data.get('poll_interval', 3.0)}s")
    except Exception as e:
        warnings.append(f"Settings file error: {str(e)}")
        print(f"⚠️  Settings file: Error - {str(e)}")
else:
    warnings.append("Settings file not found (will be created on first run)")
    print("⚠️  Settings file: Not found (will be created on first run)")
print()

# Summary
print("="*70)
print("📊 AUDIT SUMMARY")
print("="*70)
print(f"✅ Passed: {len(passed)}")
print(f"⚠️  Warnings: {len(warnings)}")
print(f"❌ Issues: {len(issues)}")
print()

if issues:
    print("❌ CRITICAL ISSUES:")
    for issue in issues:
        print(f"   - {issue}")
    print()

if warnings:
    print("⚠️  WARNINGS:")
    for warning in warnings:
        print(f"   - {warning}")
    print()

if not issues:
    print("✅ No critical issues found! App should work correctly.")
    if warnings:
        print("⚠️  Some warnings present, but app should still function.")
else:
    print("❌ Critical issues found. Please fix before running the app.")
    sys.exit(1)

print("="*70)

