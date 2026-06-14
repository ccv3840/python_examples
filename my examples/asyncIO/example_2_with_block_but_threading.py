import asyncio
import time
from concurrent.futures import ProcessPoolExecutor

# USING TIME.SLEEP() IN AN ASYNCIO PROGRAM WILL BLOCK THE ENTIRE EVENT LOOP,
# HOWEVER, WE USE THREADS


def fetch_data(param):
    print(f"Do something with {param}...", flush=True)
    time.sleep(param)
    print(f"Done with {param}", flush=True)
    return f"Result of {param}"


# When we dont have a option to change the blocking function to a non-blocking one,
# we can use threads or process pool to run the blocking function in a separate thread or process,
# so that it does not block the event loop and other coroutines can continue to run concurrently.


async def main():
    # Run in Threads
    task1 = asyncio.create_task(
        asyncio.to_thread(fetch_data, 1)
    )  # create and schedule a task
    task2 = asyncio.create_task(
        asyncio.to_thread(fetch_data, 2)
    )  # create and schedule a task
    result1 = await task1  # Run the thread
    print("Thread 1 fully completed")
    result2 = await task2  # Run the thread
    print("Thread 2 fully completed")

    print("-------------------------- \nRun in Process Pool")
    loop = asyncio.get_running_loop()

    with ProcessPoolExecutor() as executor:
        task1 = loop.run_in_executor(
            executor, fetch_data, 1
        )  # create and schedule a task
        task2 = loop.run_in_executor(
            executor, fetch_data, 2
        )  # create and schedule a task

        result1 = await task1
        print("Process 1 fully completed")
        result2 = await task2
        print("Process 2 fully completed")

    return [result1, result2]


if __name__ == "__main__":
    t1 = time.perf_counter()

    results = asyncio.run(main())
    print(results)

    t2 = time.perf_counter()
    print(f"Finished in {t2 - t1:.2f} seconds")
