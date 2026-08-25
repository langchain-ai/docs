# :remove-start:
from langchain_openai import ChatOpenAI

# Breakpoints only apply to GPT-5.6+; OpenAI requires a prefix of at least
# 1024 tokens before cache reads/writes appear in usage metadata.
stable_prefix = "Stable, cacheable instructions and reference material. " * 400
# KEEP MODEL
llm = ChatOpenAI(
    model="gpt-5.6-sol",
    prompt_cache_options={"mode": "explicit"},
)
messages = [
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
# :remove-end:

# :snippet-start: openai-prompt-cache-write-tokens-py
response = llm.invoke(messages)

cache_read = response.usage_metadata["input_token_details"].get("cache_read")
cache_creation = response.usage_metadata["input_token_details"].get("cache_creation")
print(f"Cache read tokens:     {cache_read}")
print(f"Cache creation tokens: {cache_creation}")
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    assert response is not None
    assert response.usage_metadata is not None
    # Exercise the documented accessors; a second call should show a cache read.
    cache_key = "docs-prompt-cache-write-tokens-v1"
    first = llm.invoke(messages, prompt_cache_key=cache_key)
    second = llm.invoke(messages, prompt_cache_key=cache_key)
    assert first.usage_metadata is not None
    assert second.usage_metadata is not None
    first_details = first.usage_metadata["input_token_details"]
    second_details = second.usage_metadata["input_token_details"]
    print(f"first invoke input_token_details:  {first_details}")
    print(f"second invoke input_token_details: {second_details}")
    cache_read_second = second_details.get("cache_read") or 0
    assert cache_read_second > 0, (
        f"expected cache_read > 0 on second invoke, got {second_details}"
    )
    print("✓ cache write/read token reporting sample completed")
# :remove-end:
