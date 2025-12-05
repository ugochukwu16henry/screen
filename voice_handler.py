"""
Voice Handler Module
Handles speech-to-text (voice input) and text-to-speech (voice output) functionality.
"""
import threading
import queue
import time
from config import settings

# Try to import speech recognition
try:
    import speech_recognition as sr
    HAS_SPEECH_RECOGNITION = True
except ImportError:
    HAS_SPEECH_RECOGNITION = False
    print("[Warning] speech_recognition not installed. Voice input disabled.")

# Try to import text-to-speech
try:
    import pyttsx3
    HAS_TTS = True
except ImportError:
    HAS_TTS = False
    print("[Warning] pyttsx3 not installed. Voice output disabled.")


class VoiceHandler:
    """Manages voice input (speech-to-text) and output (text-to-speech)."""
    
    def __init__(self):
        self.voice_input_enabled = settings.get("voice.input_enabled", False)
        self.voice_output_enabled = settings.get("voice.output_enabled", False)
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        self.voice_queue = queue.Queue()
        self.listening_thread = None
        self.is_listening = False
        self.stop_listening = False
        
        # Initialize speech recognition
        if HAS_SPEECH_RECOGNITION and self.voice_input_enabled:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                # Adjust for ambient noise
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("🎤 Microphone initialized")
            except Exception as e:
                print(f"[Warning] Could not initialize microphone: {e}")
                self.voice_input_enabled = False
        
        # Initialize text-to-speech
        if HAS_TTS and self.voice_output_enabled:
            try:
                self.tts_engine = pyttsx3.init()
                # Configure TTS settings
                rate = settings.get("voice.speech_rate", 150)
                volume = settings.get("voice.volume", 0.8)
                self.tts_engine.setProperty('rate', rate)
                self.tts_engine.setProperty('volume', volume)
                
                # Try to set a better voice (if available)
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    # Prefer female voice if available
                    for voice in voices:
                        if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                            self.tts_engine.setProperty('voice', voice.id)
                            break
                
                print("🔊 Text-to-speech initialized")
            except Exception as e:
                print(f"[Warning] Could not initialize TTS: {e}")
                self.voice_output_enabled = False
    
    def start_listening(self, callback=None):
        """Start continuous voice listening in background thread."""
        if not self.voice_input_enabled or not HAS_SPEECH_RECOGNITION:
            return False
        
        if self.is_listening:
            return True
        
        if not self.recognizer or not self.microphone:
            return False
        
        self.stop_listening = False
        self.is_listening = True
        
        def listen_loop():
            """Background thread for continuous listening."""
            while not self.stop_listening:
                try:
                    with self.microphone as source:
                        # Listen for audio with timeout
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    try:
                        # Recognize speech using Google's free API (offline fallback available)
                        text = self.recognizer.recognize_google(audio)
                        if text and len(text.strip()) > 0:
                            self.voice_queue.put(text)
                            if callback:
                                callback(text)
                    except sr.UnknownValueError:
                        # Speech was unintelligible
                        pass
                    except sr.RequestError as e:
                        print(f"[Warning] Speech recognition error: {e}")
                    except Exception as e:
                        print(f"[Warning] Voice recognition error: {e}")
                
                except sr.WaitTimeoutError:
                    # Timeout is normal, continue listening
                    pass
                except Exception as e:
                    if not self.stop_listening:
                        print(f"[Warning] Listening error: {e}")
                    time.sleep(0.1)
            
            self.is_listening = False
        
        self.listening_thread = threading.Thread(target=listen_loop, daemon=True)
        self.listening_thread.start()
        print("🎤 Voice listening started")
        return True
    
    def stop_listening_background(self):
        """Stop background voice listening."""
        if self.is_listening:
            self.stop_listening = True
            if self.listening_thread:
                self.listening_thread.join(timeout=2)
            print("🎤 Voice listening stopped")
    
    def listen_once(self, timeout=5):
        """Listen for a single voice input."""
        if not self.voice_input_enabled or not HAS_SPEECH_RECOGNITION:
            return None
        
        if not self.recognizer or not self.microphone:
            return None
        
        try:
            with self.microphone as source:
                print("🎤 Listening... (speak now)")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            try:
                text = self.recognizer.recognize_google(audio)
                print(f"🎤 Heard: {text}")
                return text
            except sr.UnknownValueError:
                print("🎤 Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"[Error] Speech recognition service error: {e}")
                return None
        except sr.WaitTimeoutError:
            print("🎤 Listening timeout")
            return None
        except Exception as e:
            print(f"[Error] Voice input error: {e}")
            return None
    
    def speak(self, text, interrupt=True):
        """Speak text using text-to-speech."""
        if not self.voice_output_enabled or not HAS_TTS:
            return False
        
        if not self.tts_engine:
            return False
        
        try:
            if interrupt:
                # Stop any current speech
                self.tts_engine.stop()
            
            # Speak the text
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            print(f"[Error] TTS error: {e}")
            return False
    
    def speak_async(self, text):
        """Speak text asynchronously in a background thread."""
        if not self.voice_output_enabled:
            return
        
        def speak_thread():
            self.speak(text, interrupt=True)
        
        thread = threading.Thread(target=speak_thread, daemon=True)
        thread.start()
    
    def get_voice_input(self, timeout=None):
        """Get voice input from the queue (non-blocking)."""
        try:
            if timeout:
                return self.voice_queue.get(timeout=timeout)
            else:
                return self.voice_queue.get_nowait()
        except queue.Empty:
            return None
    
    def enable_voice_input(self):
        """Enable voice input."""
        if HAS_SPEECH_RECOGNITION:
            self.voice_input_enabled = True
            settings.set("voice.input_enabled", True)
            settings.save_settings()
            if not self.recognizer:
                try:
                    self.recognizer = sr.Recognizer()
                    self.microphone = sr.Microphone()
                    with self.microphone as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=1)
                except Exception as e:
                    print(f"[Error] Could not initialize microphone: {e}")
                    self.voice_input_enabled = False
            return True
        return False
    
    def disable_voice_input(self):
        """Disable voice input."""
        self.stop_listening_background()
        self.voice_input_enabled = False
        settings.set("voice.input_enabled", False)
        settings.save_settings()
    
    def enable_voice_output(self):
        """Enable voice output."""
        if HAS_TTS:
            self.voice_output_enabled = True
            settings.set("voice.output_enabled", True)
            settings.save_settings()
            if not self.tts_engine:
                try:
                    self.tts_engine = pyttsx3.init()
                    rate = settings.get("voice.speech_rate", 150)
                    volume = settings.get("voice.volume", 0.8)
                    self.tts_engine.setProperty('rate', rate)
                    self.tts_engine.setProperty('volume', volume)
                except Exception as e:
                    print(f"[Error] Could not initialize TTS: {e}")
                    self.voice_output_enabled = False
            return True
        return False
    
    def disable_voice_output(self):
        """Disable voice output."""
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
        self.voice_output_enabled = False
        settings.set("voice.output_enabled", False)
        settings.save_settings()
    
    def cleanup(self):
        """Cleanup resources."""
        self.stop_listening_background()
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass

