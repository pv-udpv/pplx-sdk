"""OpenAI-compatible API client example.

Demonstrates using the OpenAI client with the pplx-sdk adapter server.
"""

import os
import sys

# Note: This example requires the openai package
# Install with: pip install openai

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed")
    print("Install with: pip install openai")
    sys.exit(1)


def main() -> None:
    """Run OpenAI-compatible example."""
    # Note: The adapter server uses PPLX_AUTH_TOKEN from environment
    # Start the server first with:
    #   export PPLX_AUTH_TOKEN="your-token"
    #   uvicorn pplx_sdk.api.oai_server:app --port 8000

    # Create OpenAI client pointing to local server
    client = OpenAI(
        api_key="unused",  # pplx uses session auth
        base_url="http://localhost:8000/v1",
    )

    # List available models
    print("=== Available Models ===")
    models = client.models.list()
    for model in models.data:
        print(f"  - {model.id}")
    print()

    # Non-streaming completion
    print("=== Non-Streaming Completion ===")
    response = client.chat.completions.create(
        model="pplx-70b-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is quantum computing?"},
        ],
        temperature=0.7,
        max_tokens=500,
    )

    print(f"Response: {response.choices[0].message.content}\n")

    # Streaming completion
    print("=== Streaming Completion ===")
    stream = client.chat.completions.create(
        model="pplx-70b-chat",
        messages=[
            {"role": "user", "content": "Explain machine learning in simple terms"},
        ],
        stream=True,
    )

    print("Response: ", end="", flush=True)
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print("\n")

    # Using GPT model mapping
    print("=== Using GPT Model Mapping ===")
    stream = client.chat.completions.create(
        model="gpt-4-turbo",  # Maps to pplx-70b-deep with research mode
        messages=[
            {"role": "user", "content": "What are the latest developments in AI?"},
        ],
        stream=True,
    )

    print("Response: ", end="", flush=True)
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print("\n")

    print("Done!")


if __name__ == "__main__":
    main()
