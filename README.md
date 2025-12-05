# Local AI Screen Assistant

A privacy-focused, offline AI assistant that captures screen content, extracts text via OCR, and displays AI-generated responses in a transparent overlay—entirely on your local machine.

## Features

- ✅ **100% Local & Private**: No data leaves your computer
- ✅ **Screen OCR**: Captures and reads text from any screen region
- ✅ **Local AI**: Uses Ollama with Phi-3 model (offline)
- ✅ **Transparent Overlay**: Non-intrusive display of AI responses
- ✅ **Real-time Monitoring**: Continuously watches for new questions
- ✅ **Note-Taking**: Automatically saves meeting notes with Q&A pairs (optional)
- ✅ **Voice Input**: Speech-to-text for voice notes during meetings
- ✅ **Voice Output**: Text-to-speech for AI answers (hands-free)
- ✅ **Settings Manager**: Easy GUI to configure all options

## Prerequisites

### 1. Python 3.8+

```bash
python --version
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Tesseract OCR

**Windows:**

- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Run installer and **check the box to add Tesseract to PATH**

**macOS:**

```bash
brew install tesseract
```

**Linux:**

```bash
sudo apt-get install tesseract-ocr  # Debian/Ubuntu
```

Verify installation:

```bash
tesseract --version
```

### 4. Install Ollama

Download from: https://ollama.com/download

After installation, pull the Phi-3 model:

```bash
ollama pull phi3
```

Test it:

```bash
ollama run phi3
```

## Project Structure

```
screen/
├── screen_ocr.py          # Step 1: Screen capture & OCR
├── local_ai_response.py   # Step 2: Local AI integration
├── overlay_display.py     # Step 3: Transparent overlay window
├── ai_screen_assistant.py # Step 4: Full integrated system
├── config.py              # Settings management
├── note_taker.py          # Note-taking functionality
├── voice_handler.py       # Voice input/output handling
├── settings_manager.py    # GUI settings manager
├── requirements.txt       # Python dependencies
├── settings.json          # Saved settings (created automatically)
├── notes/                 # Notes directory (created automatically)
└── README.md             # This file
```

## Usage

### Step 1: Test Screen OCR

```bash
python screen_ocr.py
```

Adjust `target_region` in the script to match your screen area.

### Step 2: Test Local AI

Make sure Ollama is running, then:

```bash
python local_ai_response.py
```

### Step 3: Test Overlay

```bash
python overlay_display.py
```

### Step 4: Configure Settings (Optional)

Use the Settings Manager to configure the application:

```bash
python settings_manager.py
```

This opens a GUI where you can:

- Enable/disable note-taking
- Configure note-taking options (timestamps, Q&A inclusion)
- Set screen capture region
- Adjust poll interval and AI model
- Set notes directory

### Step 5: Run Full System

1. **Start Ollama** (keep it running):

   - Windows/macOS: Open Ollama app
   - Or run: `ollama serve`

2. **Configure settings** (optional):

   - Run `python settings_manager.py` to configure via GUI
   - Or edit `settings.json` directly (created after first run)

3. **Run the assistant**:

   ```bash
   python ai_screen_assistant.py
   ```

4. **Press Ctrl+C** to stop (notes will be saved automatically)

## Configuration

### Using the Settings Manager (Recommended)

The easiest way to configure the application is using the GUI:

```bash
python settings_manager.py
```

### Manual Configuration

You can also edit `settings.json` directly (created after first run):

```json
{
  "note_taking": {
    "enabled": true,
    "auto_save": true,
    "save_interval": 30,
    "notes_directory": "notes",
    "include_timestamps": true,
    "include_questions": true,
    "include_answers": true
  },
  "monitor_region": {
    "top": 200,
    "left": 300,
    "width": 700,
    "height": 200
  },
  "poll_interval": 3.0,
  "ai_model": "phi3"
}
```

### Note-Taking Settings

- **enabled**: Enable/disable automatic note-taking during meetings
- **save_interval**: How often to auto-save notes (in seconds)
- **notes_directory**: Where to save notes (default: "notes")
- **include_timestamps**: Add timestamps to each note entry
- **include_questions**: Include questions in notes
- **include_answers**: Include AI answers in notes

### Screen Capture Region

Use Windows Snipping Tool or similar to find coordinates:

- `top`: Y coordinate of top-left corner
- `left`: X coordinate of top-left corner
- `width`: Width of capture area
- `height`: Height of capture area

### AI Model

Supported models: `phi3`, `llama3`, `mistral`, `gemma`, `qwen`

Make sure you've pulled the model in Ollama first:

```bash
ollama pull phi3
```

## Troubleshooting

### OCR Not Working

- Verify Tesseract is installed: `tesseract --version`
- On Windows, uncomment and set the path in `screen_ocr.py`:
  ```python
  pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
  ```

### AI Not Responding

- Ensure Ollama is running: `ollama list`
- Check if Phi-3 is installed: `ollama pull phi3`
- Test connection: `python local_ai_response.py`

### Overlay Not Visible

- Check if window is behind other apps (should be topmost)
- Adjust transparency: `self.root.attributes("-alpha", 0.85)`
- On Windows, install pywin32 for click-through: `pip install pywin32`

## Note-Taking Feature

The application can automatically take notes during meetings:

- **Automatic Capture**: Saves questions and AI responses as they occur
- **Screen Text**: Optionally captures screen text for context
- **Markdown Format**: Notes are saved as readable Markdown files
- **Auto-Save**: Notes are saved periodically and on exit
- **Local Storage**: All notes are saved locally in the `notes/` directory

### Enabling Note-Taking

1. Run the settings manager:

   ```bash
   python settings_manager.py
   ```

2. Check "Enable Note-Taking" and configure options

3. Start the assistant - notes will be automatically saved

### Note Files

Notes are saved in the `notes/` directory with filenames like:

```
meeting_notes_20240115_143022.md
```

Each file includes:

- Session start time
- Timestamped Q&A pairs
- Screen captures (if enabled)
- Voice notes (if voice input enabled)
- Session duration

## Voice Features

The application supports both voice input (speech-to-text) and voice output (text-to-speech):

### Voice Input (Speech-to-Text)

- **Continuous Listening**: Background listening for voice notes during meetings
- **Automatic Transcription**: Converts speech to text automatically
- **Voice Notes**: Spoken notes are saved to meeting notes
- **Privacy**: Uses Google's free speech recognition API (can be configured for offline)

### Voice Output (Text-to-Speech)

- **AI Answer Narration**: Speaks AI-generated answers aloud
- **Hands-Free Operation**: Listen to answers without looking at screen
- **Configurable**: Adjustable speech rate and volume
- **Local Processing**: Uses system TTS (no internet required)

### Enabling Voice Features

1. **Install Voice Dependencies**:

   ```bash
   pip install SpeechRecognition pyttsx3 pyaudio
   ```

   **Note**: On Windows, PyAudio may require additional setup:

   - Download wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
   - Or use: `pip install pipwin && pipwin install pyaudio`

2. **Configure in Settings Manager**:

   ```bash
   python settings_manager.py
   ```

3. **Enable Voice Features**:
   - Check "Enable Voice Input" for speech-to-text
   - Check "Enable Voice Output" for text-to-speech
   - Configure options:
     - **Speak AI Answers**: Automatically speak AI responses
     - **Record Voice Notes**: Save spoken notes to meeting notes
     - **Speech Rate**: Words per minute (default: 150)
     - **Volume**: 0.0 to 1.0 (default: 0.8)

### Using Voice Input

When voice input is enabled:

- The app continuously listens in the background
- Speak naturally - your words will be transcribed
- Voice notes are automatically saved to meeting notes
- No need to press any buttons or activate recording

### Using Voice Output

When voice output is enabled:

- AI answers are automatically spoken aloud
- You can listen while focusing on other tasks
- Speech rate and volume can be adjusted in settings

### Troubleshooting Voice Features

**Microphone Not Working**:

- Check microphone permissions in system settings
- Ensure microphone is not muted
- Try adjusting microphone sensitivity in system settings

**Speech Recognition Errors**:

- Ensure internet connection (for Google API) or configure offline recognition
- Speak clearly and reduce background noise
- Adjust microphone position

**TTS Not Working**:

- Check system TTS voices are installed
- On Windows: Settings > Time & Language > Speech
- Try different voice settings in the settings manager

## Privacy & Security

- All processing happens locally on your machine
- No internet connection required (after initial setup, except for speech recognition)
- No data is sent to external servers (except speech recognition uses Google's free API)
- Screen captures are processed in memory only
- Notes are stored locally on your device
- Voice recordings are processed in real-time and not stored

## License

This project is for educational and research purposes.
