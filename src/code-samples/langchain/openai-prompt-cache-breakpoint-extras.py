# :snippet-start: openai-prompt-cache-breakpoint-extras-py
content_block = {
    "type": "text",
    "text": "Long system prompt...",
    "extras": {"prompt_cache_breakpoint": {"mode": "explicit"}},
}
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    from langchain_openai import ChatOpenAI

    assert content_block["extras"]["prompt_cache_breakpoint"] == {"mode": "explicit"}

    # Breakpoints only apply to GPT-5.6+; OpenAI requires a prefix of at least
    # 1024 tokens before cache reads/writes appear in usage metadata.
    stable_prefix = "Stable, cacheable instructions and reference material. " * 400
    # KEEP MODEL
    llm = ChatOpenAI(
        model="gpt-5.6-sol",
        prompt_cache_options={"mode": "explicit"},
    )
    cache_messages = [
        {
            "role": "user",
            "content": [
                {
                    **content_block,
                    "text": stable_prefix,
                },
                {"type": "text", "text": "Say hello."},
            ],
        }
    ]
    cache_key = "docs-breakpoint-extras-v1"
    first = llm.invoke(cache_messages, prompt_cache_key=cache_key)
    second = llm.invoke(cache_messages, prompt_cache_key=cache_key)

    assert first.usage_metadata is not None
    assert second.usage_metadata is not None
    cache_read = second.usage_metadata["input_token_details"].get("cache_read") or 0
    assert cache_read > 0, (
        "expected cache_read > 0 when breakpoint is nested in extras, "
        f"got {second.usage_metadata['input_token_details']}"
    )
    print("✓ extras prompt_cache_breakpoint sample completed")
# :remove-end:
