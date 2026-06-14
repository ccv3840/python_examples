# catt.py (the new executor)
import asyncio
from pathlib import Path


async def main():
    # 1. Load testscript folder
    testscript_path = Path(args.testscript_path)
    spec = importlib.util.spec_from_file_location(
        "testscript", testscript_path / "testscript.py"
    )
    testscript = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(testscript)

    # 2. Initialize adapter (real or simulated)
    environment = config["environment"]  # From config.yaml
    if environment == "SIMULATED":
        adapter = SimulatedAdapter()
    else:
        adapter = RealAdapter()

    # 3. Create worker coroutines
    job_queue = asyncio.Queue()
    for test_case in testscript.TEST_CASES:
        await job_queue.put(test_case)

    # 4. Spawn workers
    num_workers = min(20, len(testscript.TEST_CASES))  # Max 20 concurrent
    workers = [
        asyncio.create_task(worker(job_queue, adapter, results))
        for _ in range(num_workers)
    ]

    # 5. Wait for all to finish
    await job_queue.join()

    # 6. Generate report
    report = generate_report(results)
    report.save(testscript_path / "report.html")

    print(f"✓ {len(results)} tests completed")
    print(f"  PASSED: {sum(1 for r in results if r['status'] == 'PASS')}")
    print(f"  FAILED: {sum(1 for r in results if r['status'] == 'FAIL')}")


async def worker(job_queue, adapter, results):
    while True:
        try:
            test_case = job_queue.get_nowait()
        except asyncio.QueueEmpty:
            break

        context = ExecutionContext(test_case, adapter)
        try:
            result = await context.execute()
            results.append(result)
            print(f"✓ {test_case['id']}")  # Real-time feedback
        except Exception as e:
            results.append({"id": test_case["id"], "error": str(e)})
            print(f"✗ {test_case['id']}: {e}")
        finally:
            job_queue.task_done()


if __name__ == "__main__":
    asyncio.run(main())


# GUI code calling CATT
def run_test(cast_file):
    # Step 1: CAPT (generate)
    capt_process = subprocess.Popen(
        ["python", "CAPT.py", "-cf", cast_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = capt_process.communicate()
    testscript_folder = extract_path(stdout)  # Get generated folder
    
    # Step 2: CATT (execute) — NOW ASYNC!
    catt_process = subprocess.Popen(
        ["python", "CATT.py", "-is", testscript_folder],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Stream results in real-time to GUI
    while True:
        line = catt_process.stdout.readline()
        if not line:
            break
        self.results_table.addRow(parse_result(line))  # Update GUI live
        self.progress_bar.setValue(self.results_table.rowCount())
    
    catt_process.wait()
    self.show_report(testscript_folder / "report.html")