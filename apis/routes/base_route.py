import asyncio
from fastapi import APIRouter
from concurrent.futures import ThreadPoolExecutor

from services.base_service import BaseSingleton


class WorkerManager(BaseSingleton):
    def __init__(self):
        super(WorkerManager, self).__init__()
        self.executor = ThreadPoolExecutor(max_workers=100)

    async def wait(self, job, *args):
        loop = asyncio.get_event_loop()
        output = await loop.run_in_executor(self.executor, job, *args)
        return output


class BaseRoute(BaseSingleton):
    def __init__(self, prefix="/"):
        self.router = APIRouter(
            prefix=prefix,
            responses={404: {"description": "Not found"}},
        )
        self.worker_manager = WorkerManager()
        self.create_routes()

    async def wait(self, job, *args):
        output = await self.worker_manager.wait(job, *args)
        return output

    def create_routes(self):
        raise NotImplementedError(f"{__name__} need Implementation")
