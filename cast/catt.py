# catt.py - That's the whole tool
# What CATT v2 Actually Looks Like

import asyncio
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor


class HardwareAdapter:
    """Interface to real/simulated hardware"""

    def __init__(self, adapter_type):
        self.type = adapter_type
        if adapter_type == "REAL":
            self.executor = ThreadPoolExecutor(max_workers=4)

    async def force_signal(self, signal, value):
        if self.type == "REAL":
            # Blocking OPC call in thread
            await asyncio.get_event_loop().run_in_executor(
                self.executor, self._blocking_opc_write, signal, value
            )
        else:
            # Simulated: instant
            self.state[signal] = value

    async def observe_signal(self, signal, timeout):
        # Wait for signal with timeout
        start = time.time()
        while True:
            value = self._get_signal(signal)
            if value is not None:
                return value
            if (time.time() - start) > timeout / 1000:
                raise TimeoutError()
            await asyncio.sleep(0.01)  # Check every 10ms


class ExecutionContext:
    """One test case's isolated execution"""

    def __init__(self, test_case, adapter):
        self.case = test_case
        self.adapter = adapter
        self.variables = {}

    async def execute(self):
        """Run one test case"""
        try:
            # Step 1: Force signals
            for sig, val in self.case["signals_force"].items():
                await self.adapter.force_signal(sig, val)

            # Step 2: Run function with inputs
            result = run_function(self.case["function"], self.case["inputs"])

            # Step 3: Observe signals
            for sig in self.case["signals_observe"]:
                obs = await self.adapter.observe_signal(sig, self.case["timeout"])
                result[sig] = obs

            # Step 4: Check assertions
            if result == self.case["expected"]:
                return {"id": self.case["id"], "status": "PASS"}
            else:
                return {
                    "id": self.case["id"],
                    "status": "FAIL",
                    "expected": self.case["expected"],
                    "got": result,
                }
        except Exception as e:
            return {"id": self.case["id"], "status": "ERROR", "error": str(e)}


async def run_all_tests(testscript_folder, num_workers=20):
    """Main executor"""

    # 1. Load test cases
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "testscript", testscript_folder / "testscript.py"
    )
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)

    # 2. Create adapter
    config = load_config(testscript_folder / "config.yaml")
    adapter = HardwareAdapter(config["environment"])

    # 3. Create job queue
    job_queue = asyncio.Queue()
    results = []

    for test_case in script.TEST_CASES:
        await job_queue.put(test_case)

    # 4. Run workers
    async def worker():
        while not job_queue.empty():
            try:
                test_case = job_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

            context = ExecutionContext(test_case, adapter)
            result = await context.execute()
            results.append(result)

            print(f"✓ {result['id']} {result['status']}")
            job_queue.task_done()

    workers = [asyncio.create_task(worker()) for _ in range(num_workers)]
    await asyncio.gather(*workers)

    # 5. Generate report
    print(f"\n{len(results)} tests")
    print(f"PASS: {sum(1 for r in results if r['status'] == 'PASS')}")
    print(f"FAIL: {sum(1 for r in results if r['status'] == 'FAIL')}")

    return results


if __name__ == "__main__":
    testscript_path = Path(sys.argv[1])
    results = asyncio.run(run_all_tests(testscript_path, num_workers=20))
