"""Low-level SSE streaming example.

Demonstrates direct use of the SSE transport layer.
"""

import os
import sys
import uuid

import httpx

from pplx_sdk.transport.sse import SSETransport


def main() -> None:
    """Run SSE streaming example."""
    # Get auth token from environment
    auth_token = os.getenv("PPLX_AUTH_TOKEN")
    if not auth_token:
        print("Error: PPLX_AUTH_TOKEN environment variable not set")
        sys.exit(1)

    # Create HTTP client
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "User-Agent": "pplx-sdk/0.1.0",
        "X-Client-Name": "web",
    }

    client = httpx.Client(
        base_url="https://www.perplexity.ai",
        headers=headers,
        timeout=30.0,
    )

    # Create SSE transport
    transport = SSETransport(client, "/rest/sse/perplexity.ask")

    # Generate UUIDs
    context_uuid = str(uuid.uuid4())
    frontend_uuid = str(uuid.uuid4())

    # Stream query
    print("=== SSE Streaming ===")
    query = "Explain machine learning in simple terms"
    print(f"Query: {query}")
    print(f"Context UUID: {context_uuid}")
    print(f"Frontend UUID: {frontend_uuid}\n")

    for chunk in transport.stream(
        query=query,
        context_uuid=context_uuid,
        frontend_uuid=frontend_uuid,
        mode="concise",
        model_preference="pplx-70b-chat",
    ):
        print(f"Event: {chunk.type}")

        if chunk.status:
            print(f"  Status: {chunk.status}")

        if chunk.text:
            print(f"  Text: {chunk.text[:50]}...")

        if chunk.backend_uuid:
            print(f"  Backend UUID: {chunk.backend_uuid}")

        if chunk.type == "final_response":
            print(f"  Cursor: {chunk.cursor}")
            print(f"  Reconnectable: {chunk.reconnectable}")

        print()

    # Close client
    client.close()
    print("Done!")


if __name__ == "__main__":
    main()
