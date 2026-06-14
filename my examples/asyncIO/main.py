import asyncio
import time


# concurrently running tasks


def synch_function(test_param: str) -> str:
    print(
        "This is a synchronous function, it will block the execution until it finishes"
    )
    time.sleep(0.1)
    return f"synch_function: {test_param}"


async def async_function(test_param: str) -> str:
    print("This is an asynchronous function, it will not block the execution")
    await asyncio.sleep(0.1)
    return f"async_function: {test_param}"


async def main():
    # --------------------------------------------------------------------------------------

    # run synchronously
    # print(synch_function("test1"))
    # print(synch_function("test2"))

    # --------------------------------------------------------------------------------------
    # # run asynchronously
    # loop = asyncio.get_event_loop()
    # future = loop.create_task(
    #     coro=async_function("test1")
    # )  # A promise-like object that represents the execution of the asynchronous function
    # print(f"Empty Future: {future}")

    # future.set_result("Future Result: Test")  # Manually set the result of the future
    # future_result = await future  # Await the result of the future
    # print(f"Future with Result: {future_result}")

    # --------------------------------------------------------------------------------------
    # coroutine_obj = async_function("test1")  # Create a coroutine object
    # print(
    #     f"Coroutine Object: {coroutine_obj}"
    # )  #  <coroutine object async_function at 0x000001F26A2A8E10>
    # couroutine_result = await coroutine_obj  # Await the result of the coroutine
    # print(f"Coroutine Result: {couroutine_result}")  # test1

    # --------------------------------------------------------------------------------------

    task = asyncio.create_task(async_function("test2"))  # Create a task from the coroutine
    print(f"Task Object: {task}")  # <Task pending name='Task-1' coro=<async_function() running at main.py:11>>
    task_result = await task  # Await the result of the task
    print(f"Task Result: {task_result}")  # test2 | Task keep track of the execution of the coroutine and its result

if __name__ == "__main__":
    # Start the Event Loop and run the main function
    asyncio.run(main())


# Coroutines are special functions that can be paused and resumed, allowing for asynchronous programming.
# They are defined using the async keyword and can use the await keyword to pause execution until a certain condition is met or a result is available.

# Tasks are a way to schedule and manage the execution of coroutines.
# They are created using the asyncio.create_task() function and can be awaited to get their result.
# Tasks allow for concurrent execution of multiple coroutines, enabling efficient use of resources and improved performance in I/O-bound operations.

# Future is an object that represents the result of an asynchronous operation.
# It is a low-level construct that can be used to manage the state of an asynchronous operation, such as whether it is pending, completed,
# or has resulted in an error. Futures can be awaited to get their result once the asynchronous operation is complete.
