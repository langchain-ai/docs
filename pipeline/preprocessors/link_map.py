"""Link mapping for cross-reference resolution across different scopes.

This module provides link mappings for different language/framework scopes
to resolve @[link_name] references to actual URLs.
"""

from collections.abc import Mapping
from typing import TypedDict


class LinkMap(TypedDict):
    """Typed mapping describing each link map entry."""

    host: str
    scope: str
    links: Mapping[str, str]


LINK_MAPS: list[LinkMap] = [
    {
        # Python LangGraph reference
        "host": "https://langchain-ai.github.io/langgraph/",
        "scope": "python",
        "links": {
            # Need to finish porting these
            "client.runs.stream": "cloud/reference/sdk/python_sdk_ref/#langgraph_sdk.client.RunsClient.stream",
            "client.runs.wait": "cloud/reference/sdk/python_sdk_ref/#langgraph_sdk.client.RunsClient.wait",
            "client.threads.get_history": "cloud/reference/sdk/python_sdk_ref/#langgraph_sdk.client.ThreadsClient.get_history",
            "client.threads.update_state": "cloud/reference/sdk/python_sdk_ref/#langgraph_sdk.client.ThreadsClient.update_state",
            "BaseLoader": "https://python.langchain.com/api_reference/core/document_loaders/langchain_core.document_loaders.base.BaseLoader.html",
        },
    },
    {
        # JS LangGraph reference
        "host": "https://langchain-ai.github.io/langgraphjs/",
        "scope": "js",
        "links": {
            "Auth": "reference/classes/sdk_auth.Auth.html",
            "StateGraph": "reference/classes/langgraph.StateGraph.html",
            "add_conditional_edges": "/reference/classes/langgraph.StateGraph.html#addConditionalEdges",
            "add_edge": "reference/classes/langgraph.StateGraph.html#addEdge",
            "add_node": "reference/classes/langgraph.StateGraph.html#addNode",
            "add_messages": "reference/modules/langgraph.html#addMessages",
            "astream_events": "https://v03.api.js.langchain.com/types/_langchain_core.tracers_log_stream.StreamEvent.html",
            "BaseCheckpointSaver": "reference/classes/checkpoint.BaseCheckpointSaver.html",
            "BaseLoader": "https://v03.api.js.langchain.com/classes/_langchain_core.document_loaders_base.BaseDocumentLoader.html",
            "BaseStore": "reference/classes/checkpoint.BaseStore.html",
            "BaseStore.put": "reference/classes/checkpoint.BaseStore.html#put",
            "BinaryOperatorAggregate": "reference/classes/langgraph.BinaryOperatorAggregate.html",
            "client.runs.stream": "reference/classes/sdk_client.RunsClient.html#stream",
            "client.runs.wait": "reference/classes/sdk_client.RunsClient.html#wait",
            "client.threads.get_history": "reference/classes/sdk_client.ThreadsClient.html#getHistory",
            "client.threads.update_state": "reference/classes/sdk_client.ThreadsClient.html#updateState",
            "Command": "reference/classes/langgraph.Command.html",
            "CompiledStateGraph": "reference/classes/langgraph.CompiledStateGraph.html",
            "create_react_agent": "reference/functions/langgraph_prebuilt.createReactAgent.html",
            "create_supervisor": "reference/functions/langgraph_supervisor.createSupervisor.html",
            "entrypoint.final": "reference/functions/langgraph.entrypoint.html#final",
            "entrypoint": "reference/functions/langgraph.entrypoint.html",
            "getContextVariable": "https://v03.api.js.langchain.com/functions/_langchain_core.context.getContextVariable.html",
            "get_state_history": "reference/classes/langgraph.CompiledStateGraph.html#getStateHistory",
            "HumanInterrupt": "reference/interfaces/langgraph_prebuilt.HumanInterrupt.html",
            "init_chat_model": "https://v03.api.js.langchain.com/functions/langchain.chat_models_universal.initChatModel.html",
            "interrupt": "reference/functions/langgraph.interrupt-2.html",
            "CompiledStateGraph.invoke": "reference/classes/langgraph.CompiledStateGraph.html#invoke",
            "langgraph.json": "cloud/reference/cli/#configuration-file",
            "MemorySaver": "reference/classes/checkpoint.MemorySaver.html",
            "messagesStateReducer": "reference/functions/langgraph.messagesStateReducer.html",
            "PostgresSaver": "reference/classes/checkpoint_postgres.PostgresSaver.html",
            "Pregel": "reference/classes/langgraph.Pregel.html",
            "Pregel.stream": "reference/classes/langgraph.Pregel.html#stream",
            "pre_model_hook": "reference/functions/langgraph_prebuilt.createReactAgent.html",
            "protocol": "reference/interfaces/checkpoint.SerializerProtocol.html",
            "Send": "reference/classes/langgraph.Send.html",
            "SerializerProtocol": "reference/interfaces/checkpoint.SerializerProtocol.html",
            "SqliteSaver": "reference/classes/checkpoint_sqlite.SqliteSaver.html",
            "START": "reference/variables/langgraph.START.html",
            "CompiledStateGraph.stream": "reference/classes/langgraph.CompiledStateGraph.html#stream",
            "task": "reference/functions/langgraph.task.html",
            "update_state": "reference/classes/langgraph.CompiledStateGraph.html#updateState",
        },
    },
    {
        "host": "https://v03.api.js.langchain.com/",
        "scope": "js",
        "links": {
            "AIMessage": "classes/_langchain_core.messages_ai_message.AIMessage.html",
            "AIMessageChunk": "classes/_langchain_core.messages_ai_message.AIMessageChunk.html",
            "BaseChatModel.invoke": "classes/_langchain_core.language_models_chat_models.BaseChatModel.html#invoke",
            "BaseChatModel.stream": "classes/_langchain_core.language_models_chat_models.BaseChatModel.html#stream",
            "BaseChatModel.streamEvents": "classes/_langchain_core.language_models_chat_models.BaseChatModel.html#streamEvents",
            "BaseChatModel.batch": "classes/_langchain_core.language_models_chat_models.BaseChatModel.html#batch",
            "BaseChatModel.bindTools": "classes/langchain.chat_models_universal.ConfigurableModel.html#bindTools",
            "Document": "classes/_langchain_core.documents.Document.html",
            "initChatModel": "functions/langchain.chat_models_universal.initChatModel.html",
            "RunnableConfig": "interfaces/_langchain_core.runnables.RunnableConfig.html",
            "Reference": "index.html",
            "Embeddings": "classes/_langchain_core.embeddings.Embeddings.html",
        },
    },
    {
        "host": "https://reference.langchain.com/python/",
        "scope": "python",
        "links": {
            # Module pages
            "langchain": "langchain/langchain",
            "langchain.agents": "langchain/agents",
            "langchain.messages": "langchain/messages",
            "langchain.tools": "langchain/tools",
            "langchain.chat_models": "langchain/models",
            "langchain.embeddings": "langchain/embeddings",
            "langchain_core": "langchain_core/",
            # Agents
            "create_agent": "langchain/agents/#langchain.agents.create_agent",
            "create_agent(tools)": "langchain/agents/#langchain.agents.create_agent(tools)",
            "create_agent(response_format)": "langchain/agents/#langchain.agents.create_agent(response_format)",
            "system_prompt": "langchain/agents/#langchain.agents.create_agent(system_prompt)",
            "AgentState": "langchain/agents/#langchain.agents.AgentState",
            "ModelRequest": "langchain/middleware/#langchain.agents.middleware.ModelRequest",
            "ModelRequest(response_format)": "langchain/middleware/#langchain.agents.middleware.ModelRequest(response_format)",
            "@dynamic_prompt": "langchain/middleware/#langchain.agents.middleware.dynamic_prompt",
            "@before_model": "langchain/middleware/#langchain.agents.middleware.before_model",
            "@after_model": "langchain/middleware/#langchain.agents.middleware.after_model",
            "@wrap_tool_call": "langchain/middleware/#langchain.agents.middleware.wrap_tool_call",
            "@wrap_model_call": "langchain/middleware/#langchain.agents.middleware.wrap_model_call",
            # Middleware
            "AgentMiddleware": "langchain/middleware/#langchain.agents.middleware.AgentMiddleware",
            "state_schema": "langchain/middleware/#langchain.agents.middleware.AgentMiddleware.state_schema",
            "PIIMiddleware": "langchain/middleware/#langchain.agents.middleware.PIIMiddleware",
            "SummarizationMiddleware": "langchain/middleware/#langchain.agents.middleware.SummarizationMiddleware",
            "HumanInTheLoopMiddleware": "langchain/middleware/#langchain.agents.middleware.HumanInTheLoopMiddleware",
            "ClearToolUsesEdit": "langchain/middleware/#langchain.agents.middleware.ClearToolUsesEdit",
            # Messages
            "AIMessage": "langchain/messages/#langchain.messages.AIMessage",
            "AIMessageChunk": "langchain/messages/#langchain.messages.AIMessageChunk",
            "ToolMessage": "langchain/messages/#langchain.messages.ToolMessage",
            "SystemMessage": "langchain/messages/#langchain.messages.SystemMessage",
            "HumanMessage": "langchain/messages/#langchain.messages.HumanMessage",
            "trim_messages": "langchain/messages/#langchain.messages.trim_messages",
            # Content blocks
            "BaseMessage": "langchain_core/language_models/#langchain_core.messages.BaseMessage",
            "BaseMessage(content)": "langchain_core/language_models/#langchain_core.messages.BaseMessage.content",
            "BaseMessage(content_blocks)": "langchain_core/language_models/#langchain_core.messages.BaseMessage.content_blocks",
            "ContentBlock": "langchain/messages/#langchain.messages.ContentBlock",
            "TextContentBlock": "langchain/messages/#langchain.messages.TextContentBlock",
            "ReasoningContentBlock": "langchain/messages/#langchain.messages.ReasoningContentBlock",
            "NonStandardContentBlock": "langchain/messages/#langchain.messages.NonStandardContentBlock",
            "ImageContentBlock": "langchain/messages/#langchain.messages.ImageContentBlock",
            "VideoContentBlock": "langchain/messages/#langchain.messages.VideoContentBlock",
            "AudioContentBlock": "langchain/messages/#langchain.messages.AudioContentBlock",
            "PlainTextContentBlock": "langchain/messages/#langchain.messages.PlainTextContentBlock",
            "FileContentBlock": "langchain/messages/#langchain.messages.FileContentBlock",
            "ToolCall": "langchain/messages/#langchain.messages.ToolCall",
            "ToolCallChunk": "langchain/messages/#langchain.messages.ToolCallChunk",
            "ServerToolCall": "langchain/messages/#langchain.messages.ServerToolCall",
            "ServerToolCallChunk": "langchain/messages/#langchain.messages.ServerToolCallChunk",
            "ServerToolResult": "langchain/messages/#langchain.messages.ServerToolResult",
            # Integrations
            # langchain-openai
            "langchain-openai": "integrations/langchain_openai",
            "BaseChatOpenAI": "integrations/langchain_openai/BaseChatOpenAI/",
            "ChatOpenAI": "integrations/langchain_openai/ChatOpenAI/",
            "AzureChatOpenAI": "integrations/langchain_openai/AzureChatOpenAI/",
            "OpenAI": "integrations/langchain_openai/OpenAI/",
            "AzureOpenAI": "integrations/langchain_openai/AzureOpenAI/",
            "OpenAIEmbeddings": "integrations/langchain_openai/OpenAIEmbeddings/",
            "AzureOpenAIEmbeddings": "integrations/langchain_openai/AzureOpenAIEmbeddings/",
            # langchain-anthropic
            "langchain-anthropic": "integrations/langchain_anthropic",
            "ChatAnthropic": "integrations/langchain_anthropic/ChatAnthropic/",
            "AnthropicLLM": "integrations/langchain_anthropic/AnthropicLLM/",
            # Models
            "init_chat_model": "langchain/models/#langchain.chat_models.init_chat_model",
            "init_chat_model(model_provider)": "langchain/models/#langchain.chat_models.init_chat_model(model_provider)",
            "BaseChatModel": "langchain_core/language_models/#langchain_core.language_models.chat_models.BaseChatModel",
            "BaseChatModel.invoke": "langchain_core/language_models/#langchain_core.language_models.chat_models.BaseChatModel.invoke",
            "BaseChatModel.stream": "langchain_core/language_models/#langchain_core.language_models.chat_models.BaseChatModel.stream",
            "BaseChatModel.astream_events": "langchain_core/language_models/#langchain_core.language_models.chat_models.BaseChatModel.astream_events",
            "BaseChatModel.batch": "langchain_core/language_models/#langchain_core.language_models.chat_models.BaseChatModel.batch",
            "BaseChatModel.batch_as_completed": "langchain_core/language_models/#langchain_core.language_models.chat_models.BaseChatModel.batch_as_completed",
            "BaseChatModel.bind_tools": "langchain_core/language_models/#langchain_core.language_models.chat_models.BaseChatModel.bind_tools",
            "BaseChatModel.configurable_fields": "langchain_core/language_models/#langchain_core.language_models.chat_models.BaseChatModel.configurable_fields",
            "BaseChatModel.with_structured_output": "langchain_core/language_models/#langchain_core.language_models.chat_models.BaseChatModel.with_structured_output",
            "BaseChatModel.with_structured_output(include_raw)": "langchain_core/language_models/#langchain_core.language_models.chat_models.BaseChatModel.with_structured_output(include_raw)",
            # Tools
            "@tool": "langchain/tools/#langchain.tools.tool",
            "BaseTool": "langchain/tools/#langchain.tools.BaseTool",
            # Embeddings
            "init_embeddings": "langchain_core/embeddings/#langchain_core.embeddings.embeddings.Embeddings",
            "Embeddings": "langchain_core/embeddings/#langchain_core.embeddings.embeddings.Embeddings",
            # Documents
            "Document": "langchain_core/documents/#langchain_core.documents.base.Document",
            # Runnables
            "RunnableConfig": "langchain_core/runnables/#langchain_core.runnables.RunnableConfig",
            "RunnableConfig(max_concurrency)": "langchain_core/runnables/#langchain_core.runnables.RunnableConfig.max_concurrency",
            # VectorStores
            "VectorStore": "langchain_core/vectorstores/?h=#langchain_core.vectorstores.base.VectorStore",
            # Key-value stores
            "BaseStore": "langgraph/store/#langgraph.store.base.BaseStore",
            "BaseStore.put": "langgraph/store/#langgraph.store.base.BaseStore.put",
            # Callbacks
            "on_llm_new_token": "langchain_core/callbacks/#langchain_core.callbacks.base.AsyncCallbackHandler.on_llm_new_token",
            # Rate limiters
            "InMemoryRateLimiter": "langchain_core/rate_limiters/#langchain_core.rate_limiters.InMemoryRateLimiter",
            # LangGraph
            "get_stream_writer": "langgraph/config/#langgraph.config.get_stream_writer",
            # The following are all new/ported from old LangGraph site, shold do double checks for existing usage/duplication
            "StateGraph": "langgraph/graphs/#langgraph.graph.StateGraph",
            "add_conditional_edges": "langgraph/graphs/#langgraph.graph.state.StateGraph.add_conditional_edges",
            "add_edge": "langgraph/graphs/#langgraph.graph.state.StateGraph.add_edge",
            "add_node": "langgraph/graphs/#langgraph.graph.state.StateGraph.add_node",
            "add_messages": "langgraph/graphs/#langgraph.graph.message.add_messages",
            "ToolNode": "langgraph/agents/#langgraph.prebuilt.tool_node.ToolNode",
            "CompiledStateGraph": "langgraph/graphs/#langgraph.graph.state.CompiledStateGraph",
            "CompiledStateGraph.astream": "langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.astream",
            "CompiledStateGraph.invoke": "langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.invoke",
            "AsyncPostgresSaver": "langgraph/checkpoints/#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver",
            "AsyncSqliteSaver": "langgraph/checkpoints/#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver",
            "BaseCheckpointSaver": "langgraph/checkpoints/#langgraph.checkpoint.base.BaseCheckpointSaver",
            "BinaryOperatorAggregate": "langgraph/pregel/#langgraph.pregel.Pregel--advanced-channels-context-and-binaryoperatoraggregate",
            "CipherProtocol": "langgraph/checkpoints/#langgraph.checkpoint.serde.base.CipherProtocol",
            "Command": "langgraph/types/#langgraph.types.Command",
            "create_react_agent": "langgraph/prebuilt/#langgraph.prebuilt.chat_agent_executor.create_react_agent",
            "get_runtime": "langgraph/runtime/#langgraph.runtime.get_runtime",
            "create_supervisor": "langgraph/supervisor/#langgraph_supervisor.supervisor.create_supervisor",
            "EncryptedSerializer": "langgraph/checkpoints/#langgraph.checkpoint.serde.encrypted.EncryptedSerializer",
            "entrypoint": "langgraph/func/#langgraph.func.entrypoint",
            "entrypoint.final": "langgraph/func/#langgraph.func.entrypoint.final",
            "from_pycryptodome_aes": "langgraph/checkpoints/#langgraph.checkpoint.serde.encrypted.EncryptedSerializer.from_pycryptodome_aes",
            "get_state_history": "langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.get_state_history",
            "HumanInterrupt": "langgraph/prebuilt/#langgraph.prebuilt.interrupt.HumanInterrupt",
            "InjectedState": "langgraph/agents/#langgraph.prebuilt.tool_node.InjectedState",
            "InMemorySaver": "langgraph/checkpoints/#langgraph.checkpoint.memory.InMemorySaver",
            "interrupt": "langgraph/types/#langgraph.types.interrupt",
            "JsonPlusSerializer": "langgraph/checkpoints/#langgraph.checkpoint.serde.jsonplus.JsonPlusSerializer",
            "LastValue": "langgraph/channels/#langgraph.channels.LastValue",
            "PostgresSaver": "langgraph/checkpoints/#langgraph.checkpoint.postgres.PostgresSaver",
            "Pregel": "langgraph/pregel/",
            "Pregel.astream": "langgraph/pregel/#langgraph.pregel.Pregel.astream",
            "Pregel.stream": "langgraph/pregel/#langgraph.pregel.Pregel.stream",
            "pre_model_hook": "langgraph/prebuilt/#langgraph.prebuilt.chat_agent_executor.create_react_agent",
            "protocol": "langgraph/checkpoints/#langgraph.checkpoint.serde.base.SerializerProtocol",
            "Runtime": "langgraph/runtime/#langgraph.runtime.Runtime",
            "Send": "langgraph/types/#langgraph.types.Send",
            "SerializerProtocol": "langgraph/checkpoints/#langgraph.checkpoint.serde.base.SerializerProtocol",
            "SqliteSaver": "langgraph/checkpoints/#langgraph.checkpoint.sqlite.SqliteSaver",
            "START": "langgraph/constants/#langgraph.constants.START",
            "CompiledStateGraph.stream": "langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.stream",
            "task": "langgraph/func/#langgraph.func.task",
            "Topic": "langgraph/channels/#langgraph.channels.Topic",
            "update_state": "langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.update_state",
        },
    },
    {
        "host": "https://reference.langchain.com/javascript/",
        "scope": "js",
        "links": {
            "Runtime": "interfaces/_langchain_langgraph.index.Runtime.html",
            "tool": "functions/_langchain_core.tools.tool.html",
            "ToolNode": "classes/langchain.index.ToolNode.html",
            "UsageMetadata": "types/_langchain_core.messages.UsageMetadata.html",
        },
    },
]


def _enumerate_links(scope: str) -> dict[str, str]:
    result = {}
    for link_map in LINK_MAPS:
        if link_map["scope"] == scope:
            links = link_map["links"]
            for key, value in links.items():
                if not value.startswith("http"):
                    result[key] = f"{link_map['host']}{value}"
                else:
                    result[key] = value
    return result


# Global scope is assembled from the Python and JS mappings
# Combined mapping by scope
SCOPE_LINK_MAPS = {
    "python": _enumerate_links("python"),
    "js": _enumerate_links("js"),
}
