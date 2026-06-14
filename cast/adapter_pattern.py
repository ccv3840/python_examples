
# 1. The Adapter Pattern (Critical)

# Define interface
import asyncio


class HardwareAdapter(ABC):
    @abstractmethod
    async def force_signal(self, name, value): pass
    
    @abstractmethod
    async def observe_signal(self, name, timeout): pass

# Real implementation
class RealOBCAdapter(HardwareAdapter):
    async def force_signal(self, name, value):
        # OPC call
        opc_client.write(name, value)

# Simulated implementation
class SimulatedOBCAdapter(HardwareAdapter):
    async def force_signal(self, name, value):
        # In-memory state
        self.state[name] = value


""" 

    config = load_config()
    if config["environment"] == "REAL":
        adapter = RealOBCAdapter()
    else:
        adapter = SimulatedOBCAdapter()

    # Same code works for both
    await adapter.force_signal("OBC_STATUS", "IDLE")
"""

# 2. Execution Context / Isolation (Critical)
## Your problem: 1000 concurrent test cases need independent state
# Why: Test A's forced signal doesn't pollute Test B's expected result.
# Time to learn: 2 hours (just think through the isolation model)

class ExecutionContext:
    """One test case's isolated world"""
    def __init__(self, test_case, adapter):
        self.variables = {}        # Fresh per test
        self.signal_overrides = {} # Local only
        self.adapter = adapter     # Shared hardware interface
    
    async def run(self):
        # This test can't see other tests' state
        await self.adapter.force_signal(...)
        result = await self.adapter.observe_signal(...)
        return result


# 3. Producer-Consumer Queue Pattern (Nice-to-have)
## Your problem: 1000 test cases, 20 workers
# Why: Automatic load balancing. If one test takes 10s and another takes 0.1s, workers don't starve.
# Time to learn: 2 hours (mostly just understanding asyncio.Queue)

job_queue = asyncio.Queue()

# Producer: add all tests
for test in test_cases:
    await job_queue.put(test)

# Consumers: workers pull from queue
async def worker():
    while not job_queue.empty():
        test = job_queue.get_nowait()
        result = await execute(test)
        job_queue.task_done()

# Run 20 workers in parallel
workers = [asyncio.create_task(worker()) for _ in range(20)]
await asyncio.gather(*workers)

