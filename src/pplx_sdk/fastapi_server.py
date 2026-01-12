"""FastAPI server exposing Perplexity AI as OpenAI-compatible endpoint.

Example:
    uvicorn pplx_sdk.fastapi_server:app --reload
"""

import logging
from typing import Optional

try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import StreamingResponse
except ImportError:
    raise ImportError("FastAPI is required. Install with: pip install fastapi uvicorn")

from pydantic import BaseModel

from pplx_sdk.client import AsyncPplxClient
from pplx_sdk.models import ChatCompletionMessage, ChatCompletionRole
from pplx_sdk.openai_compat import AsyncOpenAICompatibleLayer

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Perplexity AI OpenAI-Compatible Server",
    description="Expose Perplexity AI as OpenAI-compatible API",
    version="0.1.0",
)

# Initialize clients at startup
pplx_client: Optional[AsyncPplxClient] = None
openai_layer: Optional[AsyncOpenAICompatibleLayer] = None


@app.on_event("startup")
async def startup():
    """Initialize clients on startup."""
    global pplx_client, openai_layer
    pplx_client = AsyncPplxClient()
    openai_layer = AsyncOpenAICompatibleLayer(pplx_client)
    logger.info("Clients initialized")


@app.on_event("shutdown")
async def shutdown():
    """Close clients on shutdown."""
    global pplx_client
    if pplx_client:
        await pplx_client.close()
    logger.info("Clients closed")


class ChatCompletionRequest(BaseModel):
    """Chat completion request body."""

    model: str
    messages: list[dict]
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    stream: bool = False


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint."""
    if not openai_layer:
        raise HTTPException(status_code=500, detail="Server not initialized")

    try:
        result = await openai_layer.create_completion(
            model=request.model,
            messages=request.messages,
            stream=request.stream,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
        )

        if request.stream:
            return StreamingResponse(result, media_type="text/event-stream")
        return result
    except Exception as e:
        logger.exception("Error in chat completions")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
