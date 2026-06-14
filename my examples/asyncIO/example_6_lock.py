# Lock ensure that 2 coroutine wont working on same file at time time
import asyncio

# A share variable
shared_resource = 0

# An asyncio Lock
lock = asyncio.Lock()


async def modify_shared_resource():
    global shared_resource
    async with lock:
        # Critical section starts:
        # Only one coroutine can execute this block at a time
        print(f"Resource before modification: {shared_resource}")
        shared_resource += 1
        await asyncio.sleep(1)  # Simulate some work
        print(f"Resource after modification: {shared_resource}")


async def main():
    await asyncio.gather(*[modify_shared_resource() for _ in range(5)])


asyncio.run(main())
