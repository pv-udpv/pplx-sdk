"""FastAPI server providing OpenAI-compatible API.

Wraps Perplexity API with OpenAI's /v1/chat/completions format.
"""

import json
import os
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse

from pplx_sdk.api.oai_models import (
    MODEL_MAPPING,
    ChatCompletionChoice,
    ChatCompletionChunk,
    ChatCompletionChunkChoice,
    ChatCompletionChunkDelta,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    Model,
    ModelList,
)
from pplx_sdk.client import PerplexityClient

# Global client instance (initialized on startup)
_client: PerplexityClient | None = None


def get_client() -> PerplexityClient:
    """Get or create Perplexity client.

    Returns:
        PerplexityClient instance

    Raises:
        HTTPException: If client not initialized
    """
    global _client
    if _client is None:
        # Get auth token from environment
        auth_token = os.getenv("PPLX_AUTH_TOKEN")
        api_base = os.getenv("PPLX_API_BASE", "https://www.perplexity.ai")

        if not auth_token:
            raise HTTPException(
                status_code=500,
                detail="PPLX_AUTH_TOKEN environment variable not set",
            )

        _client = PerplexityClient(api_base=api_base, auth_token=auth_token)

    return _client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifespan.

    Initialize client on startup and cleanup on shutdown.
    """
    # Startup
    global _client
    try:
        get_client()
    except Exception:
        # Allow startup even if client fails (will error on first request)
        pass

    yield

    # Shutdown
    if _client:
        _client.close()
        _client = None


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Perplexity OpenAI-Compatible API",
    description="OpenAI-compatible wrapper for Perplexity AI",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/v1/health")
async def health_check() -> dict:
    """Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy", "service": "pplx-sdk-oai-adapter"}


@app.get("/v1/models")
async def list_models() -> ModelList:
    """List available models.

    Returns:
        ModelList with available models
    """
    models = []
    timestamp = int(time.time())

    for model_id, _config in MODEL_MAPPING.items():
        models.append(
            Model(
                id=model_id,
                created=timestamp,
                owned_by="perplexity-ai",
            )
        )

    return ModelList(data=models)


@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    req: Request,
) -> StreamingResponse:
    """OpenAI-compatible chat completions endpoint.

    Args:
        request: Chat completion request
        req: FastAPI request object

    Returns:
        StreamingResponse with SSE or JSON response

    Raises:
        HTTPException: On errors
    """
    try:
        client = get_client()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Get model configuration
    model_config = MODEL_MAPPING.get(request.model)
    if not model_config:
        # Default to base model
        model_config = {
            "pplx_model": request.model,
            "mode": "concise",
        }

    # Extract query from messages (use last user message)
    query = ""
    for msg in reversed(request.messages):
        if msg.role == "user":
            query = msg.content
            break

    if not query:
        raise HTTPException(status_code=400, detail="No user message found in request")

    # Create conversation
    conv = client.new_conversation(title="OpenAI API Request")

    # Generate completion ID
    completion_id = f"chatcmpl-{int(time.time())}"
    timestamp = int(time.time())

    if request.stream:
        # Streaming response

        async def generate_stream() -> AsyncGenerator[str, None]:
            """Generate SSE stream."""
            try:
                # Send initial chunk with role
                initial_chunk = ChatCompletionChunk(
                    id=completion_id,
                    created=timestamp,
                    model=request.model,
                    choices=[
                        ChatCompletionChunkChoice(
                            index=0,
                            delta=ChatCompletionChunkDelta(role="assistant"),
                            finish_reason=None,
                        )
                    ],
                )
                yield f"data: {initial_chunk.model_dump_json()}\n\n"

                # Stream content
                for chunk in conv.ask_stream(
                    query=query,
                    mode=model_config["mode"],
                    model_preference=model_config["pplx_model"],
                ):
                    if chunk.text:
                        content_chunk = ChatCompletionChunk(
                            id=completion_id,
                            created=timestamp,
                            model=request.model,
                            choices=[
                                ChatCompletionChunkChoice(
                                    index=0,
                                    delta=ChatCompletionChunkDelta(content=chunk.text),
                                    finish_reason=None,
                                )
                            ],
                        )
                        yield f"data: {content_chunk.model_dump_json()}\n\n"

                # Send final chunk
                final_chunk = ChatCompletionChunk(
                    id=completion_id,
                    created=timestamp,
                    model=request.model,
                    choices=[
                        ChatCompletionChunkChoice(
                            index=0,
                            delta=ChatCompletionChunkDelta(),
                            finish_reason="stop",
                        )
                    ],
                )
                yield f"data: {final_chunk.model_dump_json()}\n\n"
                yield "data: [DONE]\n\n"

            except Exception as e:
                error_data = {"error": {"message": str(e), "type": "server_error"}}
                yield f"data: {json.dumps(error_data)}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    else:
        # Non-streaming response
        try:
            entry = conv.ask(
                query=query,
                mode=model_config["mode"],
                model_preference=model_config["pplx_model"],
            )

            # Build text from entry blocks
            text_parts = []
            for block in entry.blocks:
                text_parts.append(block.content)
            full_text = "\n".join(text_parts) if text_parts else ""

            response = ChatCompletionResponse(
                id=completion_id,
                created=timestamp,
                model=request.model,
                choices=[
                    ChatCompletionChoice(
                        index=0,
                        message=ChatMessage(role="assistant", content=full_text),
                        finish_reason="stop",
                    )
                ],
            )

            return response.model_dump()

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
