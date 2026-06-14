file = open("file.txt", "w")
file.write("Hello, World!")
file.close()

# To ensure that the file is properly closed we make it in a few ways:
# Method 1:
with open("file.txt", "w") as file:
    file.write("Hello, World!")

# Method2:
try:
    file.write("Hello, World!")
finally:
    file.close()

# Method 1 and 2 are identical


from contextlib import contextmanager
import time
import os


# Approach 1: Custom context manager class
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        return False  # Propagate any exceptions


# Approach 2: Generator-based context manager with yield
@contextmanager
def file_manager(filename, mode):
    file = open(filename, mode)
    try:
        yield file
    finally:
        file.close()


# Usage with custom context manager class
with FileManager("file.txt", "w") as file:
    file.write("Hello, World!")

# Usage with generator-based context manager
# with file_manager("file.txt", "w") as file:
#     file.write("Hello, World!")


# ========== EXPLANATION OF GENERATOR-BASED CONTEXT MANAGERS ==========
#
# How it works:
# 1. @contextmanager decorator wraps a generator function as a context manager
# 2. Code BEFORE yield: runs when entering the 'with' block (__enter__)
# 3. yield value: returns the value to the 'as' variable
# 4. Code AFTER yield: runs when exiting the 'with' block (__exit__)
# 5. try/finally: ensures cleanup happens even if exceptions occur


# ========== MORE EXAMPLES ==========


# Example 1: Database connection context manager
@contextmanager
def database_connection(db_url):
    """Manages database connection lifecycle"""
    print("Connecting to database...")
    conn = f"Connection to {db_url}"  # Simulated connection
    try:
        yield conn
    finally:
        print("Closing database connection...")
        # conn.close()


# Usage:
# with database_connection("postgresql://localhost") as conn:
#     print(f"Using {conn}")
#     # Do database operations


# Example 2: Timer context manager
@contextmanager
def timer(label):
    """Measures execution time of a code block"""
    print(f"Starting: {label}")
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        print(f"Finished: {label} - Time: {end - start:.2f}s")


# Usage:
# with timer("data processing"):
#     time.sleep(2)  # Simulated work


# Example 3: Lock/unlock resource
@contextmanager
def lock_resource(resource_name):
    """Simulates acquiring and releasing a lock"""
    print(f"Locking {resource_name}...")
    try:
        yield
    finally:
        print(f"Unlocking {resource_name}...")


# Usage:
# with lock_resource("file.txt"):
#     print("Resource is locked, doing work...")


# Example 4: Change working directory temporarily
@contextmanager
def change_directory(path):
    """Temporarily changes working directory"""
    original_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original_dir)


# Usage:
# with change_directory("/tmp"):
#     print(f"Current dir: {os.getcwd()}")  # /tmp
# print(f"Back to: {os.getcwd()}")  # original directory


# Example 5: Exception handling in context manager
@contextmanager
def safe_operation(name):
    """Handles exceptions gracefully"""
    try:
        yield
    except Exception as e:
        print(f"Error in {name}: {e}")
    finally:
        print(f"Cleanup for {name}")


# Usage:
# with safe_operation("my_task"):
#     # If error occurs, it's caught and logged
#     x = 1 / 0  # This error is caught
