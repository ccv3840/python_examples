import asyncio

async def waiter(event):
    print("Waiting for the event to be set...")
    await event.wait()  # Wait until the event is set
    print("Event is set! Proceeding with the task...")
    
async def setter(event):
    print("Setting the event in 3 seconds...")
    await asyncio.sleep(3)  # Simulate some work before setting the event
    event.set()  # Set the event to allow the waiter to proceed
    print("Event has been set.")
    
    
async def main():
    event = asyncio.Event()  # Create an Event object
    
    await asyncio.gather(waiter(event), setter(event))

asyncio.run(main())