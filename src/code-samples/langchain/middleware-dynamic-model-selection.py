# :snippet-start: middleware-dynamic-model-selection-decorator-py
from collections.abc import Callable

from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call
from langchain.chat_models import init_chat_model

complex_model = init_chat_model("claude-sonnet-4-6")
simple_model = init_chat_model("claude-haiku-4-5-20251001")


@wrap_model_call
def dynamic_model(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    if len(request.messages) > 10:
        model = complex_model
    else:
        model = simple_model
    return handler(request.override(model=model))


# :snippet-end:

# :snippet-start: middleware-dynamic-model-selection-class-py
from collections.abc import Callable

from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain.chat_models import init_chat_model

complex_model = init_chat_model("claude-sonnet-4-6")
simple_model = init_chat_model("claude-haiku-4-5-20251001")


class DynamicModelMiddleware(AgentMiddleware):
    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        if len(request.messages) > 10:
            model = complex_model
        else:
            model = simple_model
        return handler(request.override(model=model))


# :snippet-end:

# :remove-start:
from itertools import cycle

from langchain.agents import create_agent
from langchain.messages import AIMessage
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel

assert dynamic_model is not None, "Decorator middleware should be defined"
assert issubclass(DynamicModelMiddleware, AgentMiddleware), (
    "Class middleware should subclass AgentMiddleware"
)

_simple_calls: list = []
_complex_calls: list = []


class _SimpleRouteFake(GenericFakeChatModel):
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        _simple_calls.append(messages)
        return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)


class _ComplexRouteFake(GenericFakeChatModel):
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        _complex_calls.append(messages)
        return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)


def _assert_model_routing(middleware) -> None:
    """Middleware picks simple vs complex model based on request message count."""
    global complex_model, simple_model

    _simple_calls.clear()
    _complex_calls.clear()
    simple_model = _SimpleRouteFake(messages=cycle([AIMessage(content="ok")]))
    complex_model = _ComplexRouteFake(messages=cycle([AIMessage(content="ok")]))
    placeholder = GenericFakeChatModel(messages=cycle([AIMessage(content="ok")]))

    agent = create_agent(placeholder, tools=[], middleware=[middleware])

    agent.invoke({"messages": [{"role": "user", "content": "Short thread."}]})
    assert len(_simple_calls) == 1 and len(_complex_calls) == 0, (
        "expected simple model when the request has at most 10 messages"
    )

    _simple_calls.clear()
    _complex_calls.clear()
    long_thread = [{"role": "user", "content": f"msg-{i}"} for i in range(11)]
    agent.invoke({"messages": long_thread})
    assert len(_complex_calls) == 1 and len(_simple_calls) == 0, (
        "expected complex model when the request has more than 10 messages"
    )


_assert_model_routing(dynamic_model)
print("✓ wrap_model_call decorator routes to the expected model by message count")

_assert_model_routing(DynamicModelMiddleware())
print("✓ DynamicModelMiddleware routes to the expected model by message count")
# :remove-end:
