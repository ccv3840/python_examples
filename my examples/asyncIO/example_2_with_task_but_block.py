import asyncio
import time

# USING TIME.SLEEP() IN AN ASYNCIO PROGRAM WILL BLOCK THE ENTIRE EVENT LOOP,
# CAUSING ALL OTHER COROUTINES TO BE BLOCKED AND UNABLE TO EXECUTE
# UNTIL THE SLEEP DURATION HAS PASSED. THIS DEFEATS THE PURPOSE OF USING ASYNCIO
# FOR CONCURRENT EXECUTION AND CAN LEAD TO PERFORMANCE ISSUES IN YOUR APPLICATION.


async def fetch_data(param):
    print(f"Do something with {param}...")
    time.sleep(param)
    print(f"Done with {param}")
    return f"Result of {param}"


async def main():
    task1 = asyncio.create_task(fetch_data(1))
    task2 = asyncio.create_task(fetch_data(2))
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


"""
Do something with 1...
Done with 1
Do something with 2...
Done with 2
Task 1 fully completed
Task 2 fully completed
['Result of 1', 'Result of 2']
Finished in 3.00 seconds
"""
