import asyncio
import time


async def fetch_data(param):
    await asyncio.sleep(param)
    return f"Result of {param}"


# The key difference between (3) (4) is how TaskGroup handle errors 
# if in gather with return_exception with True, it still runs other tasks
# the result will either success or the exception of the failure 

# in the TaskGroup if one of the tasks fails, 
# it will cancel all other tasks in the group and raise the exception immediately, 
# which can be useful for ensuring that all tasks in the group either succeed or fail together, 
# but it may not be desirable in all cases, especially if you want to allow other tasks to continue running even if one fails.

async def main():
    print("---------------------------------------------------")
    print("(1) Running Tasks and Coroutines concurrently")
    # Create Tasks Manually
    task1 = asyncio.create_task(fetch_data(1))
    task2 = asyncio.create_task(fetch_data(2))
    result1 = await task1
    result2 = await task2
    print(f"Task 1 and 2 awaited results: {[result1, result2]}")

    print("---------------------------------------------------")
    print("(2) Gathering Tasks and Coroutines")
    # Gather list of Coroutines
    coroutines = [fetch_data(i) for i in range(1, 3)]
    results = await asyncio.gather(*coroutines, return_exceptions=True)
    print(f"Coroutine Results: {results}")

    print("---------------------------------------------------")
    print("(3) Gathering Tasks")
    # (2) & (3) are the same, but (3) is more efficient as it creates tasks from the coroutine functions,
    # which allows them to run concurrently, while (2) runs the coroutine functions sequentially
    # as well (3) tasks allow for better error handling and cancellation support, as you can manage individual tasks more effectively.
    # if you want just only results then (2) is fine.
    # Tasks handle errors, cancellation and other features

    # Gather list of Tasks
    tasks = [asyncio.create_task(fetch_data(i)) for i in range(1, 3)] # get schedule 
    results = await asyncio.gather(*tasks, return_exceptions=True) # start execution and await results
    print(f"Task Results: {results}")

    print("---------------------------------------------------")
    print("(4) Using Task Group")

    # Task Group
    async with asyncio.TaskGroup() as tg:
        results = [tg.create_task(fetch_data(i)) for i in range(1, 3)]
        # All tasks are awaited when the context manager exits.
    print(f"Task Group Results: {[result.result() for result in results]}")
    print("---------------------------------------------------")
    return "Main Coroutine Done"


t1 = time.perf_counter()

results = asyncio.run(main())
print(results)

t2 = time.perf_counter()
print(f"Finished in {t2 - t1:.2f} seconds")
