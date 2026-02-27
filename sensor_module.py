import asyncio

class SensorModule:
    def __init__(self):
        self.data_queue = asyncio.Queue()
    
    async def process_data(self, data):
        # Асинхронная обработка данных
        await asyncio.sleep(0.1)
        print(f"Processed data: {data}")
    
    async def stream_handler(self):
        while True:
            data = await self.data_queue.get()
            if data is None:
                break
            await self.process_data(data)
            self.data_queue.task_done()
    
    async def start(self):
        self.consumer_task = asyncio.create_task(self.stream_handler())
    
    async def stop(self):
        await self.data_queue.put(None)
        await self.consumer_task

async def main():
    module = SensorModule()
    await module.start()
    
    # Симуляция потока данных
    for i in range(5):
        await module.data_queue.put(f"data_{i}")
    
    await asyncio.sleep(1)
    await module.stop()

if __name__ == "__main__":
    asyncio.run(main())