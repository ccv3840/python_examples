import time
from threading import Thread
from typing import Callable


GLOBAL: int = 1


class ClassA:
    def __init__(self, var1: str):
        self.var1 = var1
        self._class_b = ClassB(done_action_callback=self.on_b_finished)

    def on_b_finished(self, result: str):
        """Called by B when async work is done."""
        print(f"📞 A: Callback! B finished with: {result}")
        self.var1 = result

    def start_async_work(self):
        """Start B's work asynchronously."""
        print("A: Requesting async work from B... Current Global:", GLOBAL)

        self._class_b.process_async(self.var1)
        print("A: Requested. Continuing other work...")
        time.sleep(3)
        print("A: Doing other work...")
        print("A: Current Global:", GLOBAL)

class ClassB:
    def __init__(self, done_action_callback: Callable) -> None:
        self.done_action_callback = done_action_callback

    def process_async(self, var1: str):
        """Process asynchronously and call callback when done."""

        def do_work():
            print(f"B: Starting async work on '{var1}'...")
            time.sleep(2)  # Simulate long operation
            result = var1.upper()
            global GLOBAL
            GLOBAL = 2  # Modify global variable
            print(f"B: Work done! Calling callback...")
            self.done_action_callback(result)  # ← Call A's callback

        # Start in background thread
        thread = Thread(target=do_work)
        thread.start()


# Usage
class_a = ClassA("hello")

print("Before:", class_a.var1)
class_a.start_async_work()
print("After:", class_a.var1)
