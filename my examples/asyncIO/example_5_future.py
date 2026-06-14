# Future is the promise of future result

import asyncio


async def set_future_result(future, value):
    await asyncio.sleep(2)
    # Set the result of the future
    future.set_result(value)
    print(f"Set the futures result to: {value}")


async def main():
    # create a future object
    loop = asyncio.get_running_loop()
    future = loop.create_future()

    # Schedule setting the guture result:

    asyncio.create_task(set_future_result(future, "Future result is ready"))

    # wait for the future result
    result = await future
    print(f"Received the future result {result}")


asyncio.run(main())
