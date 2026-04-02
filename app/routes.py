from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.embeddings import EmbeddingManager

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    embedding_manager = EmbeddingManager()
    model_info = {
        "name": embedding_manager.model_name,
        "mode": embedding_manager.embedding_mode,
        "embedding_dim": embedding_manager.get_dimension()
    }
    return templates.TemplateResponse(
        name="index.html",
        request=request,
        context={"model_info": model_info}
    )


@router.get("/embeddings")
async def create_embeddings():
    embedding_manager = EmbeddingManager()
    embedding_manager.add_embeddings_to_collection("opportunities")
    return {"message": "Embeddings created successfully"}


@router.post("/search")
async def search(user_query: str, top_k: int = 3):

    embedding_manager = EmbeddingManager()
    query_embedding = embedding_manager.create_embedding(user_query)

    results = embedding_manager.fetch_embeddings(top_k, query_embedding)
    # Natural language response
    if results:
        response_text = (
            f"Based on your query '{user_query}', here are the most relevant opportunities:\n\n"
            + "\n\n".join(results)
        )
    else:
        response_text = f"No relevant results found for '{user_query}'."

    return {"query": user_query, "results": results, "response": response_text}