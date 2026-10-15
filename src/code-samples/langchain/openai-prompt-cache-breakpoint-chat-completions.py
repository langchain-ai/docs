# :snippet-start: openai-prompt-cache-breakpoint-chat-completions-py
from langchain_openai import ChatOpenAI

# KEEP MODEL
llm = ChatOpenAI(
    model="gpt-5.6-sol",
    prompt_cache_options={"mode": "explicit"},
)

messages = [
    {
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": (
                    "You are a helpful assistant with access to a large knowledge base."
                ),
                "prompt_cache_breakpoint": {"mode": "explicit"},  # [!code highlight]
            }
        ],
    },
    {"role": "user", "content": "Summarize the key points."},
]

response = llm.invoke(messages, prompt_cache_key="docs-breakpoint-v1")
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    # Breakpoints only apply to GPT-5.6+; OpenAI requires a prefix of at least
    # 1024 tokens before cache reads/writes appear in usage metadata.
    stable_prefix = "Stable, cacheable instructions and reference material. " * 400
    cache_messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": stable_prefix,
                    "prompt_cache_breakpoint": {"mode": "explicit"},
                },
                {"type": "text", "text": "Say hello."},
            ],
        }
    ]
    cache_key = "docs-breakpoint-cache-test-chat-completions-v1"

    first = llm.invoke(cache_messages, prompt_cache_key=cache_key)
    second = llm.invoke(cache_messages, prompt_cache_key=cache_key)

    assert first.usage_metadata is not None
    assert second.usage_metadata is not None
    first_details = first.usage_metadata["input_token_details"]
    second_details = second.usage_metadata["input_token_details"]
    cache_read = second_details.get("cache_read") or 0

    print(f"first invoke input_token_details:  {first_details}")
    print(f"second invoke input_token_details: {second_details}")
    assert cache_read > 0, (
        "expected cache_read > 0 on second invoke with identical "
        f"breakpoint prefix, got {second_details}"
    )
    print("✓ prompt cache breakpoint (Chat Completions) sample completed")
# :remove-end:
