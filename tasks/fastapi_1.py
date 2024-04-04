from contextlib import asynccontextmanager
from fastapi import FastAPI

def startup(app: FastAPI):
    app.state.startup = True

def shutdown(app: FastAPI):
    app.state.shutdown = True

def create_fastapi_app() -> FastAPI:
    """Create a new FastAPI app which calls the lifespan functions startup and shutdown.

    Returns:
        FastAPI: New FastAPI instance
    """    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        startup(app)
        yield
        shutdown(app)
    return FastAPI(lifespan=lifespan)