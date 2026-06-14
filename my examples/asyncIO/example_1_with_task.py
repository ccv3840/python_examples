import asyncio
import time

# ---------------------------------------------------

# TASK allows us to schedule and manage the execution of coroutines,
# enabling concurrent execution and efficient resource utilization in asynchronous programming.

# ---------------------------------------------------


async def fetch_data(param):
    print(f"Do something with {param}...")
    await asyncio.sleep(param)
    print(f"Done with {param}")
    return f"Result of {param}"


async def main():
    task1 = asyncio.create_task(
        fetch_data(1)
    )  # Create and Schedule and make them Ready for the execution the coroutine functions to run concurrently
    task2 = asyncio.create_task(
        fetch_data(2)
    )  # Create and Schedule make them Ready for the execution the coroutine functions to run concurrently
    result1 = await task1
    print("Task 1 fully completed")
    result2 = await task2
    print("Task 2 fully completed")
    return [result1, result2]


t1 = time.perf_counter()

results = asyncio.run(main())
print(results)

t2 = time.perf_counter()
print(f"Finished in {t2 - t1:.2f} seconds")
