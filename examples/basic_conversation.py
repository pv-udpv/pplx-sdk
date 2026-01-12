"""Basic conversation example using Perplexity SDK.

Demonstrates the high-level Conversation API for asking questions.
"""

import os
import sys

from pplx_sdk import PerplexityClient


def main() -> None:
    """Run basic conversation example."""
    # Get auth token from environment
    auth_token = os.getenv("PPLX_AUTH_TOKEN")
    if not auth_token:
        print("Error: PPLX_AUTH_TOKEN environment variable not set")
        print("\nTo get your token:")
        print("1. Open perplexity.ai in browser")
        print("2. Open DevTools (F12)")
        print("3. Go to Application → Cookies")
        print("4. Find 'pplx.session-id' or 'pplx_session'")
        print("5. Set: export PPLX_AUTH_TOKEN='your-token'")
        sys.exit(1)

    # Create client
    print("Initializing Perplexity client...")
    client = PerplexityClient(auth_token=auth_token)

    # Create conversation
    print("Creating new conversation...")
    conv = client.new_conversation(title="SDK Example")

    # Ask a question with streaming
    print("\n=== Streaming Response ===")
    query = "What is quantum computing in simple terms?"
    print(f"Query: {query}\n")

    full_text = []
    for chunk in conv.ask_stream(query, mode="concise"):
        if chunk.text:
            print(chunk.text, end="", flush=True)
            full_text.append(chunk.text)

    print("\n")

    # Ask follow-up question
    print("\n=== Follow-up Question ===")
    followup = "What are its main applications?"
    print(f"Query: {followup}\n")

    entry = conv.ask(followup, mode="concise")
    print(f"Status: {entry.status}")
    print(f"Completed: {entry.text_completed}")
    print(f"Model: {entry.display_model}")
    print(f"Sources: {len(entry.sources)}")

    # Print some source information
    if entry.sources:
        print("\nSources:")
        for i, source in enumerate(entry.sources[:3], 1):
            print(f"  {i}. {source.title or source.url}")

    # Show conversation stats
    print(f"\n=== Conversation Stats ===")
    print(f"Context UUID: {conv.context_uuid}")
    print(f"Total entries: {len(conv.entries)}")
    print(f"Thread title: {conv.thread.title}")

    # Close client
    client.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
