from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.state import db_client
from app.routes import router
from app.fixtures import load_crm_fixture


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage database lifecycle - startup and shutdown."""
    # Startup: Connect to ChromaDB and load fixtures
    db_client.connect()
    
    # Load fixtures on startup if needed
    try:
        load_crm_fixture(db_client)
    except Exception as e:
        print(f"Warning: Could not load fixtures: {e}")
    
    yield
    
    # Shutdown: Disconnect from ChromaDB
    db_client.disconnect()


app = FastAPI(
    title="RAG Application API",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routes
app.include_router(router)

# Run with: uvicorn main:app --reload
