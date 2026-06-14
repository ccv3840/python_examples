# Async Patterns for SilworX CATT v2
## Quick Reference Guide

---

## PATTERN 1: `asyncio.gather()` - Run multiple tasks at the same time

**What it does:**
```python
# Sequential (BAD): One after another
result1 = await fetch_signal("OBC")      # Wait 1s
result2 = await fetch_signal("WSC")      # Wait 1s
result3 = await fetch_signal("ATS")      # Wait 1s
# Total: 3 seconds ❌

# Concurrent (GOOD): All at the same time
tasks = [
    fetch_signal("OBC"),
    fetch_signal("WSC"),
    fetch_signal("ATS"),
]
results = await asyncio.gather(*tasks)   # Wait 1s (all parallel)
# Total: 1 second ✓
```

**When to use:**
- Run multiple signal reads/writes at same time
- Run multiple test cases concurrently
- **This is 80% of your speedup**

**Key insight:**
```
gather() says: "Run all these tasks, wait for ALL of them, then give me results"
If one task takes 5s and another takes 1s, gather() waits 5s total.
```

---

## PATTERN 2: `asyncio.Lock()` - Protect shared resources

**What it does:**
```python
# Problem: 3 tests try to write at the same time
Test1: force OBC_STATUS = BUSY
Test2: force OBC_STATUS = IDLE      ← Collision! Both writing same signal
Test3: force OBC_STATUS = ERROR

# Hardware gets confused which value is correct

# Solution: Use lock to serialize writes
class Hardware:
    def __init__(self):
        self.lock = asyncio.Lock()
    
    async def force_signal(self, name, value):
        async with self.lock:           # ← WAIT for lock
            write_to_hardware(name, value)
        # ← RELEASE lock automatically
```

**When to use:**
- Real hardware that can only handle one write at a time
- Simulated state that needs consistent updates
- **This prevents test interference**

**Key insight:**
```
Lock ensures only ONE coroutine can execute the "with" block at a time.
Others wait in line. Think of it as a bathroom with one toilet.
```

---

## PATTERN 3: `asyncio.Queue()` - Job queue with workers

**What it does:**
```python
# Create queue
job_queue = asyncio.Queue()

# Add 1000 test cases
for test in 1000_tests:
    await job_queue.put(test)

# Create 20 workers (coroutines)
async def worker():
    while not job_queue.empty():
        test = job_queue.get_nowait()
        result = await execute_test(test)
        job_queue.task_done()

# Run all workers in parallel
workers = [asyncio.create_task(worker()) for _ in range(20)]
await asyncio.gather(*workers)
```

**When to use:**
- You have N test cases and M workers
- Workers pull from queue, execute, get next job
- **This is the main CATT v2 pattern**

**Key insight:**
```
Queue acts like a to-do list. Workers grab items and work.
If one worker finishes early, it grabs the next item.
Automatic load balancing!

1000 tests, 20 workers:
- If each test takes 0.1s: 1000 * 0.1 / 20 = 0.5s total
- vs sequential: 1000 * 0.1 = 100s
```

---

## PATTERN 4: `asyncio.wait_for()` - Graceful timeouts

**What it does:**
```python
# Without timeout: Waits FOREVER if signal never comes
signal = await observe_signal("OBC_STATUS")  # Could hang forever

# With timeout: Give up after N seconds
try:
    signal = await asyncio.wait_for(
        observe_signal("OBC_STATUS"),
        timeout=5  # Wait max 5 seconds
    )
    print(f"Got signal: {signal}")
except asyncio.TimeoutError:
    print("Signal never came, test fails gracefully")
```

**When to use:**
- Waiting for hardware signals that might not come
- Don't want tests to hang forever
- **This prevents test suites from freezing**

**Key insight:**
```
wait_for() says: "Try this task, but give up after N seconds"

If task finishes in 2s: returns result
If task takes 10s but timeout is 5s: raises TimeoutError (doesn't wait)
```

---

## PATTERN 5: `ThreadPoolExecutor` - Handle blocking calls

**What it does:**
```python
# Problem: OPC library is blocking
def blocking_opc_write(signal, value):
    opc_client.write(signal, value)  # BLOCKS for 1 second
    # During this 1 second, ENTIRE event loop is frozen!
    # All other coroutines pause!

# Bad: Freezes everything
result = blocking_opc_write("OBC", "BUSY")  # Everything pauses for 1s

# Good: Run in thread pool
executor = ThreadPoolExecutor(max_workers=4)
loop = asyncio.get_event_loop()

result = await loop.run_in_executor(
    executor,
    blocking_opc_write,
    "OBC", "BUSY"
)
# Other coroutines keep running while this blocks in thread!
```

**When to use:**
- OPC library calls (they're blocking)
- Other I/O that's not async-native
- **Only if real hardware is blocking**

**Key insight:**
```
Executor runs blocking call in separate thread (not event loop).
Event loop keeps going, other coroutines keep running.
When blocking call finishes, result comes back to async code.
```

---

## PATTERN 6: All Together - Real CATT v2

**How they fit together:**

```
CATT loads testscript with 1000 test cases
         ↓
Creates job queue (PATTERN 3: Queue)
         ↓
Spawns 20 worker coroutines (PATTERN 1: gather to run all workers)
         ↓
Each worker:
  1. Gets test from queue
  2. Locks hardware before writing (PATTERN 2: Lock)
  3. Waits for signal with timeout (PATTERN 4: wait_for)
  4. Calls OPC in thread pool (PATTERN 5: ThreadPoolExecutor)
  5. Gets next test
         ↓
All workers wait for all tests done (PATTERN 1: gather)
         ↓
Generate report
```

**Real execution (from the example output):**
```
Worker1: Start test_001 (lock acquired, OBC write)
Worker2: Start test_002 (waiting for lock...)
Worker1: Finish test_001 (lock released)
Worker2: Get lock, write
Worker1: Start test_003 (while Worker2 is writing)
...
All done in ~5 seconds instead of 100+ seconds
```

---

## What Each Pattern Solves

| Problem | Pattern | Solution |
|---------|---------|----------|
| "Signal reads take 1s each" | `gather()` | Read all signals in parallel |
| "2 tests write same signal" | `Lock` | Serialize writes with lock |
| "1000 tests, needs to run fast" | `Queue` | Workers pull from queue |
| "Test hangs waiting for signal" | `wait_for()` | Timeout after N seconds |
| "OPC write freezes everything" | `ThreadPoolExecutor` | Run blocking in thread |

---

## Key Concepts to Remember

### `async def` vs regular `def`
```python
# Regular function - BLOCKS
def blocking_function():
    time.sleep(5)  # Everything stops

# Async function - Can be awaited
async def async_function():
    await asyncio.sleep(5)  # Other code runs
```

### `await` - "Pause here, let others run"
```python
result = await fetch_signal("OBC")
# Pauses THIS coroutine
# But OTHER coroutines keep running
# When signal arrives, resumes THIS coroutine
```

### `asyncio.create_task()` - "Start running"
```python
# These are NOT started
async def work(): await asyncio.sleep(1)
task1 = work()      # ← Not running yet
task2 = work()      # ← Not running yet

# These start running (in background)
task1 = asyncio.create_task(work())  # ← Running now
task2 = asyncio.create_task(work())  # ← Running now

# Wait for all
await asyncio.gather(task1, task2)
```

### `async with lock` - Automatic lock release
```python
async with self.lock:      # ACQUIRE lock
    do_something()
    if error:
        return             # Lock released automatically!
    do_more()
# Lock released here automatically
```

---

## Common Mistakes

### ❌ Forgetting `await`
```python
# Wrong: You get a coroutine object, not the result
result = fetch_signal("OBC")  # Doesn't actually run!

# Right:
result = await fetch_signal("OBC")  # Actually runs and waits
```

### ❌ Mixing blocking with async
```python
# Wrong: Blocks everything
async def bad():
    time.sleep(5)  # BLOCKS THE ENTIRE EVENT LOOP
    await something_else()

# Right: Use asyncio.sleep or executor
async def good():
    await asyncio.sleep(5)  # Just pauses this coroutine
    await something_else()
```

### ❌ Forgetting `gather()`
```python
# Wrong: Sequential (slow)
task1 = asyncio.create_task(execute_test(t1))
task2 = asyncio.create_task(execute_test(t2))
await task1
await task2

# Right: Parallel (fast)
await asyncio.gather(task1, task2)
```

### ❌ Sharing state without lock
```python
# Wrong: Race condition
async def test_a():
    shared_state["OBC"] = "BUSY"   # Did this write finish?

async def test_b():
    value = shared_state["OBC"]    # Is this new or old value?

# Right: Use lock
async with hardware.lock:
    shared_state["OBC"] = "BUSY"
```

---

## Test It Yourself

The code file `async_patterns_complete.py` has ALL these patterns with:
- ✅ Working examples
- ✅ Explanations in comments
- ✅ Output you can see
- ✅ Pattern 6 shows how they work together

Just run:
```bash
python async_patterns_complete.py
```

You'll see:
1. Sequential vs concurrent (3s vs 1s)
2. Lock preventing race conditions
3. Queue with workers handling 10 jobs
4. Timeout gracefully handling slow signals
5. ThreadPoolExecutor handling blocking calls
6. All together in simulated CATT v2

---

## Next Step: Build CATT v2

Once you understand these patterns, building CATT v2 is:
1. Load testscript_{id}.py with TEST_CASES
2. Create queue
3. Spawn workers
4. Workers use patterns above
5. Wait for all done
6. Generate report

You now have all the pieces. Just assemble them!
