from fastapi import FastAPI

from apis.routes.manual import ManualRoute


app = FastAPI()
app.include_router(ManualRoute().router)


