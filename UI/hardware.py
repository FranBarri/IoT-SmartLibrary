import threading
import time

# Check if we are on a Raspberry Pi
try:
    import RPi.GPIO as GPIO
    from mfrc522 import SimpleMFRC522
    IS_PI = True
except ImportError:
    IS_PI = False

class RFIDReader:
    def __init__(self, callback_function):
        """
        :param callback_function: The function to call when a card is scanned.
        """
        self.callback = callback_function
        self.running = True
        if IS_PI:
            self.reader = SimpleMFRC522()

    def start(self):
        """Starts the background listening thread."""
        thread = threading.Thread(target=self._scan_loop, daemon=True)
        thread.start()

    def _scan_loop(self):
        while self.running:
            if IS_PI:
                try:
                    # Blocking call on the Pi
                    id, text = self.reader.read()
                    self.callback(str(id))
                    time.sleep(2) # Prevent double scanning
                except Exception as e:
                    print(f"Hardware Error: {e}")
                    time.sleep(1)
            else:
                # On PC, we do nothing loop (simulation is manual buttons)
                time.sleep(1)