import asyncio


async def fetch_data(id, sleep_time):
    print(f"Coroutine {id} doing something...")
    await asyncio.sleep(sleep_time)
    print(f"Coroutine {id} done.")
    return {"id": id, "data": f"Sample data from coroutine {id}"}


async def _main_1():
    # Create tasks for running coroutines concuretnly
    task1 = asyncio.create_task(fetch_data(1, 2))
    task2 = asyncio.create_task(fetch_data(2, 3))
    task3 = asyncio.create_task(fetch_data(3, 1))

    result1 = await task1
    result2 = await task2
    result3 = await task3

    print(result1, result2, result3)


## Same as above, instead of running manually, we can do it we gather


async def _main_2():
    # Run coroutines concurrently and gather their return values
    results: tuple = await asyncio.gather(
        fetch_data(1, 2), fetch_data(2, 3), fetch_data(3, 1)
    ) #not great in error_handling, if 1 error occurs in 1 of the functions, wont handle
    

    for result in results:
        print(f"Received result: {result}")


# Difference between gather and task.group, taskgroup will fail if 1 function fail
async def main():
    tasks = []
    
    async with asyncio.TaskGroup() as tg:
        for i, sleep_time in enumerate([2,1,3], start=1):
            task = tg.create_task(fetch_data(i,sleep_time))
            tasks.append(task)
            
    # after the Task Group block, all task have complete. 
    results = [task.result() for task in tasks]
    
    for result in results:
        print(f"Received result: {result}")

    

asyncio.run(main())
