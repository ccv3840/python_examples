"""
Complete Async Patterns for SilworX CATT v2
All patterns explained with runnable examples
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List


# ============================================================================
# PATTERN 1: asyncio.gather() - Run tasks concurrently
# ============================================================================

print("\n" + "="*70)
print("PATTERN 1: asyncio.gather() - Run multiple tasks at the same time")
print("="*70)

async def fetch_signal(name: str, delay: float = 1) -> str:
    """
    Simulates fetching a signal from hardware (takes time).
    
    In real CATT:
    - This would call: await hardware_adapter.get_signal("OBC_STATUS")
    - It would block waiting for the hardware to respond
    
    Args:
        name: Signal name (e.g., "OBC_STATUS")
        delay: Simulated hardware response time in seconds
    
    Returns:
        Signal value
    """
    print(f"  [SIGNAL] Fetching {name}...")
    await asyncio.sleep(delay)  # Simulate hardware response time
    print(f"  [SIGNAL] {name} = OK")
    return f"{name}=OK"


async def example_1_gather():
    """
    Example: Run 5 signal fetches concurrently.
    
    Sequential (bad):  5 fetches × 1 second = 5 seconds
    Concurrent (good): All 5 in parallel = 1 second
    """
    print("\n[SEQUENTIAL] - Slow (for comparison)")
    start = time.time()
    
    # Sequential: one after another
    result1 = await fetch_signal("OBC_STATUS", delay=1)
    result2 = await fetch_signal("WSC_MODE", delay=1)
    result3 = await fetch_signal("ATS_REQUEST", delay=1)
    
    elapsed = time.time() - start
    print(f"Sequential took {elapsed:.2f}s\n")
    
    # --------
    
    print("[CONCURRENT] - Fast (using gather)")
    start = time.time()
    
    # Concurrent: all at the same time
    tasks = [
        fetch_signal("OBC_STATUS", delay=1),
        fetch_signal("WSC_MODE", delay=1),
        fetch_signal("ATS_REQUEST", delay=1),
        fetch_signal("DMI_STATE", delay=1),
        fetch_signal("CUT_STATUS", delay=1),
    ]
    
    # asyncio.gather() waits for ALL tasks to complete
    results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start
    print(f"Concurrent took {elapsed:.2f}s")
    print(f"Results: {results}")


# ============================================================================
# PATTERN 2: asyncio.Lock - Serialize writes to shared resource
# ============================================================================

print("\n" + "="*70)
print("PATTERN 2: asyncio.Lock - Protect shared resources")
print("="*70)

class SharedHardwareState:
    """
    Simulates shared hardware that only one test can write to at a time.
    
    Problem: If 20 tests try to force signals simultaneously:
    - Test 1 sets OBC_STATUS = BUSY
    - Test 2 sets OBC_STATUS = IDLE
    - Hardware gets confused (write collision)
    
    Solution: Use asyncio.Lock to serialize writes
    """
    
    def __init__(self):
        self.state = {"OBC_STATUS": "IDLE"}
        self.lock = asyncio.Lock()  # ← LOCK - Only one coroutine at a time
    
    async def force_signal(self, signal_name: str, value: str, test_id: str):
        """
        Force a signal value. Must be serialized (one at a time).
        """
        print(f"  [{test_id}] Waiting for lock to force {signal_name}={value}...")
        
        async with self.lock:  # ← ACQUIRE LOCK (wait if locked)
            print(f"  [{test_id}] Got lock! Writing {signal_name}={value}")
            await asyncio.sleep(0.2)  # Simulate OPC write time
            self.state[signal_name] = value
            print(f"  [{test_id}] Done writing. Releasing lock.")
        # ← LOCK AUTOMATICALLY RELEASED here
    
    async def read_signal(self, signal_name: str, test_id: str):
        """
        Read a signal. CAN be done in parallel (reads don't conflict).
        """
        # NO lock needed for reads
        await asyncio.sleep(0.1)  # Simulate OPC read time
        value = self.state.get(signal_name, "UNKNOWN")
        print(f"  [{test_id}] Read {signal_name}={value}")
        return value


async def example_2_lock():
    """
    Example: 3 tests try to force signals simultaneously.
    The lock ensures they do it one-by-one.
    """
    hardware = SharedHardwareState()
    
    # All 3 tests try to force at the same time
    tasks = [
        hardware.force_signal("OBC_STATUS", "BUSY", "test_001"),
        hardware.force_signal("OBC_STATUS", "IDLE", "test_002"),
        hardware.force_signal("OBC_STATUS", "ERROR", "test_003"),
    ]
    
    # They'll execute, but the lock serializes the actual hardware writes
    await asyncio.gather(*tasks)
    
    print(f"Final hardware state: {hardware.state}")


# ============================================================================
# PATTERN 3: asyncio.Queue - Job queue with multiple workers
# ============================================================================

print("\n" + "="*70)
print("PATTERN 3: asyncio.Queue - Producer-Consumer (Job Queue)")
print("="*70)

async def execute_test(test_case: dict, worker_id: int) -> dict:
    """
    Execute ONE test case.
    
    In real CATT:
    - This would be: ExecutionContext(test_case).run()
    - It would force signals, run function, observe results
    
    Args:
        test_case: {"id": "test_001", "function": "obc_check", ...}
        worker_id: Which worker is running this (for display)
    
    Returns:
        Test result
    """
    test_id = test_case["id"]
    print(f"    [Worker {worker_id}] Starting {test_id}")
    
    # Simulate test execution
    await asyncio.sleep(test_case.get("duration", 0.5))
    
    # Simulate pass/fail
    passed = test_case.get("passed", True)
    result = {
        "id": test_id,
        "status": "PASS" if passed else "FAIL",
        "worker": worker_id,
    }
    print(f"    [Worker {worker_id}] Completed {test_id}: {result['status']}")
    return result


async def job_queue_worker(job_queue: asyncio.Queue, worker_id: int, results: list):
    """
    Worker coroutine: continuously pulls jobs from queue and executes them.
    
    This is ONE worker. You'd have 20 of these running in parallel.
    """
    while True:
        try:
            # Try to get a job (non-blocking, raises if empty)
            test_case = job_queue.get_nowait()
        except asyncio.QueueEmpty:
            # No more jobs
            break
        
        # Execute the test
        result = await execute_test(test_case, worker_id)
        results.append(result)
        
        # Tell the queue we finished this job
        job_queue.task_done()


async def example_3_queue():
    """
    Example: 10 test cases, 3 workers.
    
    Workers pull from queue and execute in parallel.
    This is the main pattern for CATT v2!
    """
    
    # Create 10 test cases
    test_cases = [
        {"id": f"test_{i:03d}", "duration": 0.3, "passed": i % 10 != 5}
        for i in range(10)
    ]
    
    # Create the job queue
    job_queue = asyncio.Queue()
    
    # Add all tests to queue
    for test in test_cases:
        await job_queue.put(test)
    
    print(f"\n[QUEUE] 10 test cases, 3 workers")
    print(f"Queue size: {job_queue.qsize()}")
    
    # Collect results
    results = []
    
    # Create 3 worker tasks
    num_workers = 3
    workers = [
        asyncio.create_task(job_queue_worker(job_queue, i, results))
        for i in range(num_workers)
    ]
    
    # Wait for all workers to finish
    await asyncio.gather(*workers)
    
    # Results
    print(f"\n[RESULTS]")
    print(f"Total: {len(results)}")
    print(f"Passed: {sum(1 for r in results if r['status'] == 'PASS')}")
    print(f"Failed: {sum(1 for r in results if r['status'] == 'FAIL')}")


# ============================================================================
# PATTERN 4: asyncio.wait_for() - Timeouts
# ============================================================================

print("\n" + "="*70)
print("PATTERN 4: asyncio.wait_for() - Graceful timeout handling")
print("="*70)

async def observe_signal_with_timeout(signal_name: str, timeout: float) -> str:
    """
    Wait for a signal to appear, but give up after timeout.
    
    In real CATT:
    - Test says: "Wait for OBC_STATUS, but only 5 seconds"
    - If signal doesn't come in 5s, fail the test gracefully
    - Don't hang forever
    
    Args:
        signal_name: Which signal to wait for
        timeout: How long to wait (seconds)
    
    Returns:
        Signal value if it comes
    
    Raises:
        asyncio.TimeoutError if timeout exceeded
    """
    
    # Simulate waiting for a signal that takes time to arrive
    print(f"    Waiting for {signal_name} (timeout: {timeout}s)...")
    await asyncio.sleep(signal_name == "FAST_SIGNAL" and 1 or 6)  # 1s or 6s
    return f"{signal_name}=OK"


async def example_4_timeout():
    """
    Example: Wait for signals with timeout.
    - Some signals arrive in time ✓
    - Some signals timeout ✗
    """
    
    print("\n[TIMEOUT] Handling slow/missing signals\n")
    
    # Signal that arrives BEFORE timeout
    try:
        result = await asyncio.wait_for(
            observe_signal_with_timeout("FAST_SIGNAL", timeout=2),
            timeout=2  # Give 2 seconds
        )
        print(f"  ✓ Got signal: {result}\n")
    except asyncio.TimeoutError:
        print(f"  ✗ Timeout waiting for FAST_SIGNAL\n")
    
    # Signal that does NOT arrive before timeout
    try:
        result = await asyncio.wait_for(
            observe_signal_with_timeout("SLOW_SIGNAL", timeout=2),
            timeout=2  # Give 2 seconds (but signal takes 6s)
        )
        print(f"  ✓ Got signal: {result}\n")
    except asyncio.TimeoutError:
        print(f"  ✗ Timeout waiting for SLOW_SIGNAL (took too long)\n")


# ============================================================================
# PATTERN 5: ThreadPoolExecutor - Handle blocking calls
# ============================================================================

print("\n" + "="*70)
print("PATTERN 5: ThreadPoolExecutor - Handle blocking calls in async code")
print("="*70)

def blocking_opc_write(signal_name: str, value: str) -> bool:
    """
    BLOCKING function - simulates OPC library call.
    
    Real OPC libraries (opcua) use blocking I/O:
    - They lock until the write completes
    - Can't be called directly in async code
    - Would freeze all other coroutines
    
    Args:
        signal_name: Which signal to write
        value: What value to write
    
    Returns:
        True if successful
    """
    print(f"        [BLOCKING] Starting OPC write {signal_name}={value} (thread)")
    time.sleep(1)  # BLOCKING sleep - locks the thread
    print(f"        [BLOCKING] OPC write complete")
    return True


async def example_5_threadpool():
    """
    Example: Call blocking function from async code.
    
    Problem: OPC is blocking. If you call it directly:
      result = blocking_opc_write("OBC", "BUSY")
      - Freezes ENTIRE asyncio event loop
      - All other coroutines pause
      - Takes forever
    
    Solution: Run blocking call in ThreadPoolExecutor
      - Blocking call runs in separate thread
      - Async code doesn't freeze
      - Parallelization still works
    """
    
    print("\n[THREADPOOL] 3 parallel OPC writes\n")
    
    # Create executor with max 2 threads
    executor = ThreadPoolExecutor(max_workers=2)
    
    # Get the event loop
    loop = asyncio.get_event_loop()
    
    # Create 3 blocking tasks (but run them in threads)
    tasks = [
        loop.run_in_executor(
            executor,
            blocking_opc_write,
            f"SIGNAL_{i}",
            "VALUE"
        )
        for i in range(1, 4)
    ]
    
    # Wait for all blocking calls to finish
    # But while waiting, other async code can run
    results = await asyncio.gather(*tasks)
    
    print(f"\nAll OPC writes completed: {results}")
    executor.shutdown()  # Clean up thread pool


# ============================================================================
# PATTERN 6: COMBINED - Everything together (Real CATT v2 preview)
# ============================================================================

print("\n" + "="*70)
print("PATTERN 6: COMBINED - All patterns together")
print("="*70)

class ExecutionContext:
    """
    One test case's isolated execution context.
    Uses: async, lock, timeout, threadpool
    """
    
    def __init__(self, test_case: dict, hardware, executor, test_id: int):
        self.case = test_case
        self.hardware = hardware
        self.executor = executor
        self.id = test_id
        self.result = {}
    
    async def execute(self) -> dict:
        """
        Execute ONE test with all patterns.
        """
        try:
            # 1. Force signals with lock (PATTERN 2)
            for signal, value in self.case.get("signals_force", {}).items():
                await self.hardware.force_signal(signal, value, f"test_{self.id}")
            
            # 2. Observe signal with timeout (PATTERN 4)
            observe_signals = self.case.get("signals_observe", {})
            for signal, expected in observe_signals.items():
                try:
                    actual = await asyncio.wait_for(
                        self.hardware.read_signal(signal, f"test_{self.id}"),
                        timeout=2
                    )
                    self.result[signal] = actual
                except asyncio.TimeoutError:
                    self.result[signal] = "TIMEOUT"
            
            # 3. Call blocking function with threadpool (PATTERN 5)
            loop = asyncio.get_event_loop()
            blocking_result = await loop.run_in_executor(
                self.executor,
                blocking_opc_write,
                "TEST_SIGNAL",
                "TEST"
            )
            
            return {
                "id": f"test_{self.id}",
                "status": "PASS",
                "result": self.result
            }
        
        except Exception as e:
            return {
                "id": f"test_{self.id}",
                "status": "FAIL",
                "error": str(e)
            }


async def example_6_combined():
    """
    Example: Real CATT v2 preview.
    
    5 test cases, 2 workers, using all patterns.
    """
    
    print("\n[COMBINED] Real CATT v2 simulation\n")
    
    # Setup
    hardware = SharedHardwareState()
    executor = ThreadPoolExecutor(max_workers=2)
    
    # Create test cases
    test_cases = [
        {
            "id": 1,
            "signals_force": {"OBC_STATUS": "BUSY"},
            "signals_observe": {"OBC_STATUS": "OK"},
        },
        {
            "id": 2,
            "signals_force": {"WSC_MODE": "IDLE"},
            "signals_observe": {"WSC_MODE": "OK"},
        },
        {
            "id": 3,
            "signals_force": {"ATS_REQUEST": "ACTIVE"},
            "signals_observe": {"ATS_REQUEST": "OK"},
        },
    ]
    
    # Create job queue (PATTERN 3)
    job_queue = asyncio.Queue()
    for test in test_cases:
        await job_queue.put(test)
    
    results = []
    
    # Create 2 workers (PATTERN 3)
    async def worker(worker_id):
        while not job_queue.empty():
            try:
                test = job_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
            
            ctx = ExecutionContext(test, hardware, executor, test["id"])
            result = await ctx.execute()  # Uses all patterns
            results.append(result)
            job_queue.task_done()
    
    # Run workers (PATTERN 1: gather)
    await asyncio.gather(
        worker(1),
        worker(2),
    )
    
    print(f"\nResults: {len(results)} tests completed")
    executor.shutdown()


# ============================================================================
# RUN ALL EXAMPLES
# ============================================================================

async def main():
    """Run all examples"""
    
    await example_1_gather()
    await example_2_lock()
    await example_3_queue()
    await example_4_timeout()
    await example_5_threadpool()
    await example_6_combined()
    
    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70)


if __name__ == "__main__":
    # This is the ONLY way to run async code
    asyncio.run(main())
