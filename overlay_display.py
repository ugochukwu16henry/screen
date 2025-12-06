import tkinter as tk
from tkinter import font as tkfont
import threading
import queue

class AnswerOverlay:
    def __init__(self, x=100, y=100, width=500, height=150, fullscreen=False):
        self.root = tk.Tk()
        self.root.title("AI Assistant (Private)")
        
        # Make window transparent and click-through
        # For fullscreen, make window visible but not too opaque
        # The label will have its own background for readability
        if fullscreen:
            # For fullscreen, make window semi-transparent so it's visible
            self.root.attributes("-alpha", 0.4)  # Visible but not blocking (40% opacity)
            self.root.configure(bg='black')
        else:
            self.root.attributes("-alpha", 0.9)
            self.root.configure(bg='black')
        self.root.attributes("-topmost", True)        # Always on top
        self.root.overrideredirect(True)             # No title bar/borders
        
        # CRITICAL: Make window not steal focus or block input
        # This prevents freezing other applications
        try:
            if self.root.tk.call('tk', 'windowingsystem') == 'win32':
                # Don't focus the window - let other apps work
                self.root.attributes("-disabled", False)
                # Make sure it doesn't grab focus
                self.root.focus_set = lambda: None  # Disable focus stealing
        except:
            pass
        
        # If fullscreen, get screen dimensions
        if fullscreen:
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x, y = 0, 0
            width, height = screen_width, screen_height
        
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
        
        # Create label for text - position in top-left for fullscreen
        # Use solid background for text readability (window itself is transparent)
        self.text_label = tk.Label(
            self.root,
            text="",
            bg="#1a1a1a",  # Dark gray background for better visibility
            fg="#ffffff",  # White text
            justify="left",
            anchor="nw",  # Anchor to top-left
            wraplength=min(width - 40, 600),  # Limit width for readability
            padx=20,
            pady=20,
            font=("Arial", 12, "bold"),  # Larger, bold font for better visibility
            relief="raised",  # Add border for visibility
            bd=2  # Border width
        )
        # Pack to top-left instead of filling entire window
        self.text_label.pack(anchor="nw", fill="none")
        
        # Custom font (already set in Label creation, but can override here if needed)
        # custom_font = tkfont.Font(family="Arial", size=11)
        # self.text_label.config(font=custom_font)
        
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
        import win32api
        hwnd = window.root.winfo_id()
        
        # Get current window style
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        
        # Enable click-through: WS_EX_LAYERED | WS_EX_TRANSPARENT
        # This allows clicks to pass through to apps behind
        new_style = style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
        
        # Also prevent window from stealing focus
        new_style |= win32con.WS_EX_NOACTIVATE
        
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_style)
        
        # Make sure window doesn't block input
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | 
            win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW
        )
        
        print("✅ Click-through enabled - window won't block other apps")
    except ImportError:
        print("[Warning] pywin32 not available - window may block clicks")
        print("          Install: pip install pywin32")
    except Exception as e:
        print(f"[Warning] Could not enable click-through: {e}")
        print("          Window may block other applications")

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

