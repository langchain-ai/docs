# :snippet-start: middleware-dynamic-prompt-decorator-py
from collections.abc import Callable

from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call
from langchain.messages import SystemMessage


@wrap_model_call
def add_context(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    new_content = list(request.system_message.content_blocks) + [
        {"type": "text", "text": "Additional context."}
    ]
    new_system_message = SystemMessage(content=new_content)
    return handler(request.override(system_message=new_system_message))


# :snippet-end:

# :snippet-start: middleware-dynamic-prompt-class-py
from collections.abc import Callable

from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse


class ContextMiddleware(AgentMiddleware):
    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        new_content = list(request.system_message.content_blocks) + [
            {"type": "text", "text": "Additional context."}
        ]
        new_system_message = SystemMessage(content=new_content)
        return handler(request.override(system_message=new_system_message))


# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    from langchain.agents import create_agent
    from langchain.messages import AIMessage
    from langchain_core.language_models.fake_chat_models import GenericFakeChatModel

    captured_messages: list = []

    class RecordingFakeChatModel(GenericFakeChatModel):
        def _generate(self, messages, stop=None, run_manager=None, **kwargs):
            captured_messages.clear()
            captured_messages.extend(messages)
            return super()._generate(
                messages, stop=stop, run_manager=run_manager, **kwargs
            )

    def assert_middleware_adds_context_to_system_prompt(middleware) -> None:
        model = RecordingFakeChatModel(messages=iter([AIMessage(content="ok")]))
        agent = create_agent(
            model,
            tools=[],
            system_prompt="You are a helpful assistant.",
            middleware=[middleware],
        )
        captured_messages.clear()
        agent.invoke({"messages": [{"role": "user", "content": "Hello"}]})

        assert captured_messages, "expected the model to be called once"
        system_msg = captured_messages[0]
        text_chunks = [
            b["text"] for b in system_msg.content_blocks if b["type"] == "text"
        ]
        assert "You are a helpful assistant." in text_chunks, text_chunks
        assert "Additional context." in text_chunks, text_chunks

    assert_middleware_adds_context_to_system_prompt(add_context)
    print("✓ wrap_model_call decorator adds context to the model request")

    assert_middleware_adds_context_to_system_prompt(ContextMiddleware())
    print("✓ ContextMiddleware adds context to the model request")

# :remove-end:
