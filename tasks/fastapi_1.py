from contextlib import asynccontextmanager
from fastapi import FastAPI

def startup(app: FastAPI):
    print("Starting the FastAPI server")

def shutdown(app: FastAPI):
    print("Stopping the FastAPI server")

def create_fastapi_app() -> FastAPI:
    """Create an instance of FastAPI which calls `startup` when starting and `shutdown` when stopping"""
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        startup(app)
        yield
        shutdown(app)
    return FastAPI(lifespan=lifespan)