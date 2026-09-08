# :snippet-start: openai-prompt-cache-options-py
from langchain_openai import ChatOpenAI

# KEEP MODEL
llm = ChatOpenAI(
    model="gpt-5.6-sol",
    prompt_cache_options={"mode": "explicit", "ttl": "30m"},
)

messages = [{"role": "user", "content": "Hello"}]

# Override per request
response = llm.invoke(
    messages,
    prompt_cache_options={"mode": "implicit"},
)
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    assert response is not None
    assert response.usage_metadata is not None

    # Confirm model-level options remain available on a follow-up call, and that
    # a per-request override is accepted without error.
    default_response = llm.invoke(messages)
    assert default_response is not None

    # KEEP MODEL
    responses_llm = ChatOpenAI(
        model="gpt-5.6-sol",
        use_responses_api=True,
        prompt_cache_options={"mode": "explicit", "ttl": "30m"},
    )
    responses_result = responses_llm.invoke(
        messages,
        prompt_cache_options={"mode": "implicit"},
    )
    assert responses_result is not None
    print("✓ prompt_cache_options model-level and per-request override completed")
# :remove-end:
