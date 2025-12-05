import tkinter as tk
from tkinter import font as tkfont
import threading
import queue

class AnswerOverlay:
    def __init__(self, x=100, y=100, width=500, height=150):
        self.root = tk.Tk()
        self.root.title("AI Assistant (Private)")
        
        # Make window transparent and click-through
        self.root.attributes("-alpha", 0.85)          # Transparency (0–1)
        self.root.attributes("-topmost", True)        # Always on top
        self.root.overrideredirect(True)             # No title bar/borders
        
        # Enable click-through (platform-specific)
        try:
            if self.root.tk.call('tk', 'windowingsystem') == 'win32':
                # Windows: enable click-through
                import ctypes
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                # Actually, we'll set it after window creation
                # We'll use a different method below
            elif self.root.tk.call('tk', 'windowingsystem') == 'aqua':
                # macOS: harder to do click-through reliably in tkinter
                pass
        except:
            pass

        # Set geometry
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create label for text
        self.text_label = tk.Label(
            self.root,
            text="",
            bg="black",
            fg="white",
            justify="left",
            wraplength=width - 20,
            padx=10,
            pady=10
        )
        self.text_label.pack(fill="both", expand=True)
        
        # Custom font
        custom_font = tkfont.Font(family="Helvetica", size=12)
        self.text_label.config(font=custom_font)
        
        # Thread-safe update mechanism using queue
        self._update_queue = queue.Queue()
        self._main_thread_id = threading.get_ident()

    def _update_text_safe(self, text: str):
        """Internal method to update text - must be called from main thread."""
        try:
            self.text_label.config(text=text)
            self.root.update_idletasks()
        except Exception as e:
            print(f"[Warning] Overlay update error: {e}")

    def update_text(self, text: str):
        """Thread-safe text update. Can be called from any thread."""
        # Check if we're in the main thread
        if threading.get_ident() == self._main_thread_id:
            # Direct update if in main thread
            self._update_text_safe(text)
        else:
            # Put update request in queue for main thread to process
            try:
                self._update_queue.put(text, block=False)
            except queue.Full:
                # Queue full, skip this update
                pass
    
    def process_updates(self):
        """Process pending updates from queue. Call this periodically from main thread."""
        try:
            while True:
                text = self._update_queue.get_nowait()
                self._update_text_safe(text)
        except queue.Empty:
            pass

    def hide(self):
        self.root.withdraw()

    def show(self):
        self.root.deiconify()

    def run(self):
        self.root.mainloop()

# Optional: Windows-specific click-through (requires pywin32)
def enable_click_through_windows(window):
    try:
        import win32con
        import win32gui
        hwnd = window.root.winfo_id()
        win32gui.SetWindowLong(
            hwnd,
            win32con.GWL_EXSTYLE,
            win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) |
            win32con.WS_EX_LAYERED |
            win32con.WS_EX_TRANSPARENT
        )
    except ImportError:
        print("[Info] Install 'pywin32' for click-through on Windows:")
        print("      pip install pywin32")

# Example usage
if __name__ == "__main__":
    overlay = AnswerOverlay(x=50, y=50, width=400, height=120)
    
    # Enable click-through on Windows (optional but recommended)
    try:
        enable_click_through_windows(overlay)
    except:
        pass

    overlay.update_text("🤖 Ready! Ask a question on screen...")
    overlay.show()
    
    # Keep window open for 10 seconds as demo
    import time
    time.sleep(10)
    overlay.root.destroy()

