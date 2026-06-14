# How to Use These Async Materials
## Complete Learning & Implementation Guide

---

## The Three Files You Have

### 1. **async_patterns_complete.py** (Runnable Examples)
**What it is:** Working code you can run right now.
```bash
python async_patterns_complete.py
```

**What it shows:**
- ✅ PATTERN 1: `asyncio.gather()` - Parallel execution (3s → 1s)
- ✅ PATTERN 2: `asyncio.Lock()` - Shared resource protection
- ✅ PATTERN 3: `asyncio.Queue()` - Job queue with workers
- ✅ PATTERN 4: `asyncio.wait_for()` - Timeout handling
- ✅ PATTERN 5: `ThreadPoolExecutor` - Blocking calls
- ✅ PATTERN 6: All together - Real CATT v2 preview

**How to use it:**
1. Run it to see output
2. Read the comments to understand each pattern
3. Modify it - try changing worker count, test count, timeouts
4. See how changes affect execution time

**Key outputs to watch:**
```
Sequential: 3s
Concurrent: 1s (← This is what you get!)

Workers acquiring locks in order
Test cases being executed in parallel
Timeouts handling gracefully
Blocking calls in thread pool
```

---

### 2. **ASYNC_PATTERNS_EXPLAINED.md** (Reference Guide)
**What it is:** Written explanations of each pattern.

**How to use it:**
1. Read when you're confused about a pattern
2. Use as reference while coding
3. Show to your team to explain concepts
4. Copy code snippets into your CATT v2

**Structure:**
- Each pattern has: What it does + When to use + Key insight
- Common mistakes section
- All patterns together explanation
- Links to avoid learning unnecessary things

---

### 3. **CATT_v2_skeleton.py** (Architecture Blueprint)
**What it is:** The actual structure of CATT v2.

**How to use it:**
1. Read the comments to understand the flow
2. This is 80% of what your real CATT v2 will look like
3. Shows where each async pattern is used
4. Shows how adapters, contexts, queues fit together

**Don't copy-paste blindly:**
- This is a skeleton, not complete code
- Real hardware calls are stubbed out
- You'll need to integrate your actual OPC/Ethernet code
- Real testscript loading will be slightly different

---

## Learning Path (1-2 Weeks)

### Day 1-2: Run and Read Examples
```
Time: 4 hours

1. Run async_patterns_complete.py
   python async_patterns_complete.py

2. Read output, understand what happened

3. For each pattern:
   - Look at the code
   - Read ASYNC_PATTERNS_EXPLAINED.md
   - Understand why it matters

4. Question to answer:
   "Why does gather() make things 3× faster?"
   Answer: Runs all tasks in parallel instead of one-by-one
```

### Day 3-4: Modify Examples
```
Time: 4 hours

Try these experiments:

1. Experiment 1 - More workers
   In example_3_queue():
   Change: num_workers = 3
   To:     num_workers = 10
   Result: Should still complete in ~3s (load balancing)

2. Experiment 2 - More test cases
   Change: for i in range(10)
   To:     for i in range(100)
   Result: Watch it scale

3. Experiment 3 - Timeout behavior
   In example_4_timeout():
   Change timeout values
   See what happens

4. Experiment 4 - Lock behavior
   In example_2_lock():
   Add print statements to track lock acquisition order
```

### Day 5-6: Understand CATT v2 Structure
```
Time: 4 hours

Read CATT_v2_skeleton.py in order:

1. HardwareAdapter (abstract base class)
   Question: "Why make it abstract?"
   Answer: Same interface, different implementations

2. RealHardwareAdapter
   Question: "Why use ThreadPoolExecutor?"
   Answer: Real OPC is blocking

3. SimulatedHardwareAdapter
   Question: "Why use Lock?"
   Answer: Multiple tests write to shared state

4. ExecutionContext
   Question: "How is isolation achieved?"
   Answer: Each test gets own variables dict

5. TestExecutor
   Question: "How do 20 workers run concurrently?"
   Answer: asyncio.Queue + asyncio.gather()

6. main()
   Question: "What's the entry point?"
   Answer: This is what gets called from GUI/CLI
```

### Day 7: Plan Your CATT v2
```
Time: 4 hours

Create a checklist:

From async_patterns_complete.py, I need:
- [ ] Pattern 1: gather() to run all workers
- [ ] Pattern 2: Lock to protect hardware writes
- [ ] Pattern 3: Queue for job distribution
- [ ] Pattern 4: wait_for() for signal timeouts
- [ ] Pattern 5: ThreadPoolExecutor for blocking OPC

From CATT_v2_skeleton.py, I need:
- [ ] HardwareAdapter (abstract interface)
- [ ] RealHardwareAdapter (with real OPC calls)
- [ ] SimulatedHardwareAdapter (in-memory state)
- [ ] ExecutionContext (test isolation)
- [ ] TestExecutor (orchestration)
- [ ] main() (entry point)

From my current CATT:
- [ ] Loading testscript_{id}.py
- [ ] Parsing TEST_CASES
- [ ] Running assertions
- [ ] Generating reports
```

---

## Applying to Your CATT

### What Stays the Same
✅ CLI interface: `CATT -is /path/to/testscript`  
✅ testscript_{id}.py structure (format from CAPT)  
✅ Report generation  
✅ RQM integration (if you have it)  

### What Changes
❌ Sequential execution → Parallel (PATTERN 3)  
❌ No timeout handling → Graceful timeouts (PATTERN 4)  
❌ Shared state (all tests see same signals) → Isolated contexts  
❌ Blocking hardware calls → ThreadPoolExecutor (PATTERN 5)  

### Integration Steps

**Step 1: Make adapters (Week 1)**
```python
# In your project:
adapters/
├── hardware_adapter.py      (abstract base)
├── real_adapter.py          (your real OBC/WSC code)
└── simulated_adapter.py     (in-memory state)

# Your real adapter calls your actual OPC code
# Everything else is the same
```

**Step 2: Make ExecutionContext (Week 1)**
```python
# In your project:
execution/
└── context.py

# Copy structure from CATT_v2_skeleton.py
# Replace signal handling with your real testscript execution
```

**Step 3: Make TestExecutor (Week 2)**
```python
# In your project:
execution/
└── executor.py

# This orchestrates everything
# Copy the queue + worker pattern from skeleton
# Replace testscript loading with your actual code
```

**Step 4: Integration with existing CATT (Week 2)**
```python
# Keep your existing CATT structure
# Just replace the execution loop with TestExecutor

# Old CATT:
def run_tests(testscript_folder):
    testscript = load(testscript_folder)
    for test in testscript.TEST_CASES:      # Sequential
        result = execute(test)

# New CATT:
async def run_tests(testscript_folder):
    testscript = load(testscript_folder)
    executor = TestExecutor(num_workers=20)
    results = await executor.run_tests(testscript.TEST_CASES)
    # Done in 10s instead of 100s!
```

---

## Testing Your Implementation

### Test 1: Verify Speedup
```python
# Measure:
# - 10 sequential tests
# - 10 parallel tests with 2 workers
# - 10 parallel tests with 20 workers

# Expected:
# Sequential:    ~1 second
# 2 workers:     ~0.5 seconds
# 20 workers:    ~0.1 seconds
```

### Test 2: Verify Isolation
```python
# Verify each test:
# - Gets own variable namespace
# - Can't see other tests' signal forces
# - Fails independently (one test failure doesn't affect others)

# Run 100 tests where some fail
# Check: failures are independent
```

### Test 3: Verify Lock Protection
```python
# Run 100 tests that all write same signal
# Check: writes happen one-by-one (not simultaneously)
# Watch lock output: test_001 waits, test_002 waits, test_001 done, etc.
```

### Test 4: Verify Timeouts
```python
# Run tests with signals that never come
# Check: timeout after N seconds (doesn't hang forever)
# Test fails gracefully with timeout error
```

---

## Quick Reference: Where Each Pattern Goes

| Pattern | Where in CATT v2 | Why |
|---------|---|---|
| `gather()` | TestExecutor: wait for all workers | Run all workers at same time |
| `Lock` | HardwareAdapter: protect writes | Only one test writes at a time |
| `Queue` | TestExecutor: distribute jobs | Workers pull tests dynamically |
| `wait_for()` | ExecutionContext: observe signal | Don't wait forever for signals |
| `ThreadPoolExecutor` | RealHardwareAdapter: OPC calls | Don't freeze event loop |

---

## Common Questions

### Q: Do I need to understand ALL async patterns?
**A:** No. You need patterns 1, 2, 3. Patterns 4 and 5 are optional (but make things better).

### Q: Can I use ThreadPoolExecutor without asyncio?
**A:** No, ThreadPoolExecutor only makes sense with async. If using it synchronously, threads are slower than just sequential.

### Q: How many workers should I use?
**A:** Start with 20. If hardware is simulated, go up to 50. If hardware is real and blocking, go down to 4-10 (to avoid overwhelming real hardware).

### Q: What if a test needs real hardware state from previous test?
**A:** Don't do that. Isolation is a feature, not a bug. Each test must be independent. If you need setup, put it in the test case itself.

### Q: Can tests interfere with each other?
**A:** Only if they share state without a lock. Use locks for writes to hardware. Reads don't need locks.

### Q: What if I get a "RuntimeError: no running event loop"?
**A:** You're trying to use async code outside of asyncio.run(). Wrap everything in `async def main()` and call `asyncio.run(main())`.

---

## Implementation Checklist

- [ ] Downloaded async_patterns_complete.py
- [ ] Ran it and saw the output
- [ ] Read ASYNC_PATTERNS_EXPLAINED.md
- [ ] Understood each pattern
- [ ] Read CATT_v2_skeleton.py
- [ ] Understood the architecture
- [ ] Created HardwareAdapter abstract class
- [ ] Created RealHardwareAdapter (with your OPC code)
- [ ] Created SimulatedHardwareAdapter
- [ ] Created ExecutionContext
- [ ] Created TestExecutor
- [ ] Integrated into your CATT
- [ ] Tested with 10 test cases
- [ ] Tested with 100 test cases
- [ ] Measured speedup (should be 10-20×)
- [ ] Verified isolation works
- [ ] Verified timeouts work
- [ ] Deployed to team

---

## Time Estimate

| Task | Time | Difficulty |
|------|------|-----------|
| Run examples | 1 hour | Easy |
| Read explanations | 2 hours | Easy |
| Understand patterns | 4 hours | Medium |
| Build HardwareAdapter | 4 hours | Medium |
| Build ExecutionContext | 4 hours | Medium |
| Build TestExecutor | 4 hours | Medium |
| Integration testing | 4 hours | Medium |
| **Total** | **~23 hours** | **1-2 weeks** |

**Reality:** Probably 3 weeks with debugging, learning, integration.

---

## Help Resources

If you get stuck:

1. **"What does `async with` do?"**
   → ASYNC_PATTERNS_EXPLAINED.md → Look up "async with lock"

2. **"How do I add timeout?"**
   → ASYNC_PATTERNS_COMPLETE.py → Look at example_4_timeout()

3. **"Why is my hardware adapter blocking?"**
   → CATT_v2_skeleton.py → RealHardwareAdapter → ThreadPoolExecutor

4. **"How do test cases get isolation?"**
   → CATT_v2_skeleton.py → ExecutionContext → owns self.variables

---

## Next Step

**Start here:**
```bash
# 1. Run the examples
python async_patterns_complete.py

# 2. Read the explanations
# (Open ASYNC_PATTERNS_EXPLAINED.md in your editor)

# 3. Study the skeleton
# (Open CATT_v2_skeleton.py, read all comments)

# 4. Plan your implementation
# (Create checklist above)

# 5. Start coding
# (Build HardwareAdapter first)
```

Good luck! You've got this.
