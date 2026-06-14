# Similar to lock,
# but allow multiple coroutines to access the shared resource concurrently, up to a specified limit.
# at the same time


import asyncio


async def access_resource(semaphore, id):
    async with semaphore:
        print(f"Coroutine {id} is accessing the resource...")
        await asyncio.sleep(1)  # Simulate some work
        print(f"Coroutine {id} is done accessing the resource.")


async def main():
    # Create a semaphore with a limit of 2 concurrent accesses
    semaphore = asyncio.Semaphore(2)

    # Create multiple tasks that will access the resource
    tasks = [asyncio.create_task(access_resource(semaphore, i)) for i in range(5)]

    # Wait for all tasks to complete
    await asyncio.gather(*tasks)


asyncio.run(main())
