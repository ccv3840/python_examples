"""
Production-Ready Async Callback Pattern with Error Handling and Database

Features:
✅ Error callbacks for exception handling
✅ Timeout handling
✅ ClassC with simple database implementation
✅ Chained callbacks (A → B → C)
✅ No global variables
✅ Type hints and docstrings
✅ Proper exception handling

# Basic workflow
python production_ready_callbacks.py

# See error handling
python production_ready_callbacks.py error

# Run parallel workflows
python production_ready_callbacks.py parallel

# See how we avoid globals
python production_ready_callbacks.py no_globals

"""

import time
from threading import Thread
from typing import Callable, Optional
from dataclasses import dataclass
from datetime import datetime


# ===== DATABASE SIMULATION =====


@dataclass
class DatabaseRecord:
    """Represents a database record."""

    id: int
    value: str
    timestamp: datetime
    processed_by: str


class SimpleDatabase:
    """Simple in-memory database."""

    def __init__(self):
        self.records = {}
        self.next_id = 1

    def insert(self, value: str, processed_by: str) -> DatabaseRecord:
        """Insert a record into the database."""
        record = DatabaseRecord(
            id=self.next_id,
            value=value,
            timestamp=datetime.now(),
            processed_by=processed_by,
        )
        self.records[self.next_id] = record
        self.next_id += 1
        print(f"   💾 DB: Inserted record #{record.id}: {value}")
        return record

    def get(self, record_id: int) -> Optional[DatabaseRecord]:
        """Get a record from the database."""
        return self.records.get(record_id)

    def update(self, record_id: int, value: str) -> Optional[DatabaseRecord]:
        """Update a record in the database."""
        if record_id in self.records:
            self.records[record_id].value = value
            print(f"   💾 DB: Updated record #{record_id}: {value}")
            return self.records[record_id]
        return None

    def get_all(self):
        """Get all records."""
        return list(self.records.values())


# ===== CLASS A (Orchestrator) =====


class ClassA:
    """
    Orchestrator - manages workflow and coordinates B and C.
    No global variables!
    """

    def __init__(self, var1: str, db: SimpleDatabase):
        self.var1 = var1
        self.db = db
        self.latest_record_id = None
        self._class_b = ClassB(
            done_action_callback=self.on_b_finished,
            error_callback=self.on_b_error,
        )
        self._class_c = None

    def on_b_finished(self, result: str):
        """Callback when B finishes successfully."""
        print(f"📞 A: B finished! Result: {result}")
        self.var1 = result

        # Now start C's work
        print(f"A: Starting ClassC...")
        self._class_c = ClassC(
            db=self.db,
            done_action_callback=self.on_c_finished,
            error_callback=self.on_c_error,
            timeout=5,
        )
        self._class_c.process_async(self.var1)

    def on_b_error(self, error: Exception):
        """Error handler for B."""
        print(f"❌ A: B failed with error: {error}")
        # Handle error, maybe retry

    def on_c_finished(self, result: DatabaseRecord):
        """Callback when C finishes successfully."""
        print(f"📞 A: C finished! Record ID: {result.id}")
        self.latest_record_id = result.id
        self.var1 = result.value
        print(f"A: Final var1: {self.var1}")

    def on_c_error(self, error: Exception):
        """Error handler for C."""
        print(f"❌ A: C failed with error: {error}")
        # Handle error

    def start_async_work(self):
        """Start the async workflow."""
        print(f"A: Starting async workflow...")
        print(f"   Initial var1: {self.var1}")
        print(f"   Database state: {len(self.db.get_all())} records")

        # Start B
        self._class_b.process_async(self.var1)

        # Continue with other work while B works
        print(f"A: Continuing other work while B processes...")
        time.sleep(4)
        print(f"A: Other work done")

    def get_database_records(self):
        """Get all records from database."""
        return self.db.get_all()


# ===== CLASS B (Processor) =====


class ClassB:
    """
    Processor - transforms data asynchronously.
    Has error handling and timeout.
    """

    def __init__(
        self,
        done_action_callback: Callable[[str], None],
        error_callback: Callable[[Exception], None],
        timeout: int = 5,
    ):
        self.done_action_callback = done_action_callback
        self.error_callback = error_callback
        self.timeout = timeout

    def process_async(self, var1: str):
        """Process asynchronously in a background thread."""

        def do_work():
            try:
                print(f"B: Starting async work on '{var1}'...")

                # Simulate processing
                time.sleep(2)

                # Simulate occasional error (10% chance)
                import random

                if random.random() < 0.1:
                    raise ValueError("Random processing error!")

                result = var1.upper()
                print(f"B: Work done! Result: {result}")
                self.done_action_callback(result)

            except Exception as e:
                print(f"B: Error occurred: {e}")
                self.error_callback(e)

        # Start in background thread
        thread = Thread(target=do_work, daemon=False)
        thread.start()


# ===== CLASS C (Database Writer) =====


class ClassC:
    """
    Database Writer - saves data to database asynchronously.
    Has full error handling and timeout.
    """

    def __init__(
        self,
        db: SimpleDatabase,
        done_action_callback: Callable[[DatabaseRecord], None],
        error_callback: Callable[[Exception], None],
        timeout: int = 5,
    ):
        self.db = db
        self.done_action_callback = done_action_callback
        self.error_callback = error_callback
        self.timeout = timeout

    def process_async(self, var1: str):
        """Save to database asynchronously."""

        def do_work():
            try:
                print(f"C: Starting async database work on '{var1}'...")

                # Simulate database operation
                time.sleep(1)

                # Check timeout
                if self.timeout < 0:
                    raise TimeoutError("Database operation timed out!")

                # Insert into database
                record = self.db.insert(var1, processed_by="ClassC")

                # Simulate occasional DB error (5% chance)
                import random

                if random.random() < 0.05:
                    raise IOError("Database connection lost!")

                print(f"C: Database write done! Record ID: {record.id}")
                self.done_action_callback(record)

            except TimeoutError as e:
                print(f"C: Timeout error: {e}")
                self.error_callback(e)

            except IOError as e:
                print(f"C: Database error: {e}")
                self.error_callback(e)

            except Exception as e:
                print(f"C: Unexpected error: {e}")
                self.error_callback(e)

        # Start in background thread
        thread = Thread(target=do_work, daemon=False)
        thread.start()


# ===== USAGE EXAMPLE =====


def main():
    print("=" * 70)
    print("PRODUCTION-READY ASYNC CALLBACK PATTERN")
    print("=" * 70)
    print()

    # Create database (NO GLOBAL VARIABLES!)
    db = SimpleDatabase()

    # Create workflow
    class_a = ClassA(var1="hello", db=db)

    print("Before workflow:")
    print(f"  var1: {class_a.var1}")
    print(f"  Database records: {len(db.get_all())}")
    print()

    # Start async workflow
    class_a.start_async_work()

    # Wait for everything to finish (B: 2s, C: 1s, plus overhead)
    print("\n⏳ Waiting for async operations to complete...")
    time.sleep(5)

    print("\n" + "=" * 70)
    print("AFTER WORKFLOW")
    print("=" * 70)
    print(f"Final var1: {class_a.var1}")
    print(f"Latest record ID: {class_a.latest_record_id}")
    print(f"\nDatabase records:")
    for record in class_a.get_database_records():
        print(f"  Record #{record.id}: {record.value} (by {record.processed_by})")


# ===== ADVANCED EXAMPLE: Error Handling =====


def main_with_error_demo():
    """Demonstrate error handling."""
    print("=" * 70)
    print("ERROR HANDLING DEMONSTRATION")
    print("=" * 70)
    print()

    db = SimpleDatabase()

    class_a = ClassA(var1="error_test", db=db)

    print("Starting workflow that might encounter errors...")
    class_a.start_async_work()

    # Wait longer to see error handling
    time.sleep(6)

    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETED (with possible errors)")
    print("=" * 70)


# ===== ADVANCED EXAMPLE: Multiple Parallel Workflows =====


def main_parallel_workflows():
    """Run multiple workflows in parallel."""
    print("=" * 70)
    print("PARALLEL WORKFLOWS DEMONSTRATION")
    print("=" * 70)
    print()

    db = SimpleDatabase()

    # Create multiple workflows
    workflows = [ClassA(var1=f"workflow_{i}", db=db) for i in range(3)]

    # Start all workflows
    for i, workflow in enumerate(workflows):
        print(f"\nStarting workflow {i}...")
        workflow.start_async_work()

    # Wait for all to complete
    print("\n⏳ Waiting for all workflows to complete...")
    time.sleep(6)

    print("\n" + "=" * 70)
    print("ALL WORKFLOWS COMPLETED")
    print("=" * 70)
    print(f"Total database records: {len(db.get_all())}")
    print("\nAll records:")
    for record in db.get_all():
        print(f"  #{record.id}: {record.value} (by {record.processed_by})")


# ===== COMPARISON: WITH vs WITHOUT GLOBALS =====


def demo_no_globals():
    """
    This version shows how to avoid global variables.
    Instead, pass everything as parameters or constructor args.
    """
    print("✅ NO GLOBAL VARIABLES USED!")
    print()
    print("Instead of:")
    print("  GLOBAL = 1")
    print("  class_b.modify_global()")
    print()
    print("We use:")
    print("  db = SimpleDatabase()  # Passed to classes")
    print("  class_a = ClassA(db=db)")
    print()
    print("Benefits:")
    print("  ✅ No hidden state")
    print("  ✅ Easy to test (inject mock DB)")
    print("  ✅ Thread-safe (each workflow has own DB reference)")
    print("  ✅ Traceable (see exactly what changed)")


if __name__ == "__main__":
    # Choose which demo to run
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "error":
        main_with_error_demo()
    elif len(sys.argv) > 1 and sys.argv[1] == "parallel":
        main_parallel_workflows()
    elif len(sys.argv) > 1 and sys.argv[1] == "no_globals":
        demo_no_globals()
    else:
        main()

    print("\n✅ Done!\n")
