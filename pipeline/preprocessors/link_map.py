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
            "UsageMetadata": "langchain/messages/#langchain.messages.UsageMetadata",
            "InputTokenDetails": "langchain/messages/#langchain.messages.InputTokenDetails",
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
            # Document loaders
            "BaseLoader": "langchain_core/document_loaders/#langchain_core.document_loaders.BaseLoader",
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
            "StateGraph": "langgraph/graphs/#langgraph.graph.state.StateGraph",
            "StateGraph.compile": "langgraph/graphs/#langgraph.graph.state.StateGraph.compile",
            "add_edge": "langgraph/graphs/#langgraph.graph.state.StateGraph.add_edge",
            "add_conditional_edges": "langgraph/graphs/#langgraph.graph.state.StateGraph.add_conditional_edges",
            "add_node": "langgraph/graphs/#langgraph.graph.state.StateGraph.add_node",
            "add_messages": "langgraph/graphs/#langgraph.graph.message.add_messages",
            "CompiledStateGraph": "langgraph/graphs/#langgraph.graph.state.CompiledStateGraph",
            "CompiledStateGraph.astream": "langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.astream",
            "CompiledStateGraph.invoke": "langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.invoke",
            "CompiledStateGraph.stream": "langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.stream",
            "get_state_history": "langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.get_state_history",
            "update_state": "langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.update_state",
            "InjectedState": "langgraph/agents/#langgraph.prebuilt.tool_node.InjectedState",
            "InjectedStore": "langgraph/agents/#langgraph.prebuilt.tool_node.InjectedStore",
            "InjectedToolCallId": "langchain/tools/#langchain.tools.InjectedToolCallId",
            "get_runtime": "langgraph/runtime/#langgraph.runtime.get_runtime",
            "Command": "langgraph/types/#langgraph.types.Command",
            "CachePolicy": "langgraph/types/#langgraph.types.CachePolicy",
            "interrupt": "langgraph/types/#langgraph.types.interrupt",
            "ToolNode": "langgraph/agents/#langgraph.prebuilt.tool_node.ToolNode",
            "AsyncPostgresSaver": "langgraph/checkpoints/#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver",
            "AsyncSqliteSaver": "langgraph/checkpoints/#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver",
            "BaseCheckpointSaver": "langgraph/checkpoints/#langgraph.checkpoint.base.BaseCheckpointSaver",
            "BinaryOperatorAggregate": "langgraph/pregel/#langgraph.pregel.Pregel--advanced-channels-context-and-binaryoperatoraggregate",
            "CipherProtocol": "langgraph/checkpoints/#langgraph.checkpoint.serde.base.CipherProtocol",
            "EncryptedSerializer": "langgraph/checkpoints/#langgraph.checkpoint.serde.encrypted.EncryptedSerializer",
            "from_pycryptodome_aes": "langgraph/checkpoints/#langgraph.checkpoint.serde.encrypted.EncryptedSerializer.from_pycryptodome_aes",
            "InMemorySaver": "langgraph/checkpoints/#langgraph.checkpoint.memory.InMemorySaver",
            "SerializerProtocol": "langgraph/checkpoints/#langgraph.checkpoint.serde.base.SerializerProtocol",
            "SqliteSaver": "langgraph/checkpoints/#langgraph.checkpoint.sqlite.SqliteSaver",
            "JsonPlusSerializer": "langgraph/checkpoints/#langgraph.checkpoint.serde.jsonplus.JsonPlusSerializer",
            "PostgresSaver": "langgraph/checkpoints/#langgraph.checkpoint.postgres.PostgresSaver",
            "create_react_agent": "langgraph/prebuilt/#langgraph.prebuilt.chat_agent_executor.create_react_agent",
            "LastValue": "langgraph/channels/#langgraph.channels.LastValue",
            "START": "langgraph/constants/#langgraph.constants.START",
            "Pregel": "langgraph/pregel/",
            "Pregel.astream": "langgraph/pregel/#langgraph.pregel.Pregel.astream",
            "Pregel.stream": "langgraph/pregel/#langgraph.pregel.Pregel.stream",
            "Runtime": "langgraph/runtime/#langgraph.runtime.Runtime",
            "Send": "langgraph/types/#langgraph.types.Send",
            "Topic": "langgraph/channels/#langgraph.channels.Topic",
            # SDK
            "client.runs.stream": "langsmith/deployment/sdk/#langgraph_sdk.client.RunsClient.stream",
            "client.runs.wait": "langsmith/deployment/sdk/#langgraph_sdk.client.RunsClient.wait",
            "client.threads.get_history": "langsmith/deployment/sdk/#langgraph_sdk.client.ThreadsClient.get_history",
            "client.threads.update_state": "langsmith/deployment/sdk/#langgraph_sdk.client.ThreadsClient.update_state",
            # Functional API
            "@task": "langgraph/func/#langgraph.func.task",
            "@entrypoint": "langgraph/func/#langgraph.func.entrypoint",
            "entrypoint.final": "langgraph/func/#langgraph.func.entrypoint.final",
        },
    },
    {
        "host": "https://reference.langchain.com/javascript/",
        "scope": "js",
        "links": {
            # @langchain/core references
            "AIMessage": "classes/_langchain_core.messages.AIMessage.html",
            "AIMessageChunk": "classes/_langchain_core.messages.AIMessageChunk.html",
            "BaseChatModel.invoke": "classes/_langchain_core.language_models_chat_models.BaseChatModel.html#invoke",
            "BaseChatModel.stream": "classes/_langchain_core.language_models_chat_models.BaseChatModel.html#stream",
            "BaseChatModel.streamEvents": "classes/_langchain_core.language_models_chat_models.BaseChatModel.html#streamEvents",
            "BaseChatModel.batch": "classes/_langchain_core.language_models_chat_models.BaseChatModel.html#batch",
            "BaseChatModel.bindTools": "classes/_langchain_core.language_models_chat_models.BaseChatModel.html#bindTools",
            "Document": "classes/_langchain_core.documents.Document.html",
            "Embeddings": "classes/_langchain_core.embeddings.Embeddings.html",
            "initChatModel": "functions/langchain.chat_models_universal.initChatModel.html",
            "RunnableConfig": "interfaces/_langchain_core.runnables.RunnableConfig.html",
            "tool": "functions/_langchain_core.tools.tool.html",
            "UsageMetadata": "types/_langchain_core.messages.UsageMetadata.html",
            "BaseLoader": "classes/_langchain_core.document_loaders_base.BaseDocumentLoader.html",
            "getContextVariable": "functions/_langchain_core.context.getContextVariable.html",
            "astream_events": "classes/_langchain_core.runnables.Runnable.html#streamEvents",
            # LangGraph SDK references
            "Auth": "classes/_langchain_langgraph-sdk.auth.Auth.html",
            "client.runs.stream": "classes/_langchain_langgraph-sdk.client.RunsClient.html#stream",
            "client.runs.wait": "classes/_langchain_langgraph-sdk.client.RunsClient.html#wait",
            "client.threads.get_history": "classes/_langchain_langgraph-sdk.client.ThreadsClient.html#getHistory",
            "client.threads.update_state": "classes/_langchain_langgraph-sdk.client.ThreadsClient.html#updateState",
            # LangGraph checkpoint references
            "BaseCheckpointSaver": "classes/_langchain_langgraph-checkpoint.BaseCheckpointSaver.html",
            "BaseStore": "classes/_langchain_langgraph-checkpoint.BaseStore.html",
            "BaseStore.put": "classes/_langchain_langgraph-checkpoint.BaseStore.html#put",
            "MemorySaver": "classes/_langchain_langgraph-checkpoint.MemorySaver.html",
            "PostgresSaver": "classes/_langchain_langgraph-checkpoint-postgres.index.PostgresSaver.html",
            "protocol": "interfaces/_langchain_langgraph-checkpoint.SerializerProtocol.html",
            "SerializerProtocol": "interfaces/_langchain_langgraph-checkpoint.SerializerProtocol.html",
            "SqliteSaver": "classes/_langchain_langgraph-checkpoint-sqlite.SqliteSaver.html",
            # LangGraph core references
            "StateGraph": "classes/_langchain_langgraph.index.StateGraph.html",
            "add_conditional_edges": "classes/_langchain_langgraph.index.StateGraph.html#addConditionalEdges",
            "add_edge": "classes/_langchain_langgraph.index.StateGraph.html#addEdge",
            "add_node": "classes/_langchain_langgraph.index.StateGraph.html#addNode",
            "add_messages": "functions/_langchain_langgraph.index.messagesStateReducer.html",
            "BinaryOperatorAggregate": "classes/_langchain_langgraph.index.BinaryOperatorAggregate.html",
            "Command": "classes/_langchain_langgraph.index.Command.html",
            "CompiledStateGraph": "classes/_langchain_langgraph.index.CompiledStateGraph.html",
            "create_react_agent": "functions/_langchain_langgraph.prebuilt.createReactAgent.html",
            "create_supervisor": "functions/_langchain_langgraph-supervisor.createSupervisor.html",
            "entrypoint": "functions/_langchain_langgraph.index.entrypoint.html",
            "entrypoint.final": "functions/_langchain_langgraph.index.entrypoint.html#final",
            "get_state_history": "classes/_langchain_langgraph.pregel.Pregel.html#getStateHistory",
            "HumanInterrupt": "interfaces/_langchain_langgraph.prebuilt.HumanInterrupt.html",
            "interrupt": "functions/_langchain_langgraph.index.interrupt.html",
            "CompiledStateGraph.invoke": "classes/_langchain_langgraph.index.CompiledStateGraph.html#invoke",
            "langgraph.json": "cloud/reference/cli/#configuration-file",
            "messagesStateReducer": "functions/_langchain_langgraph.index.messagesStateReducer.html",
            "Pregel": "classes/_langchain_langgraph.pregel.Pregel.html",
            "Pregel.stream": "classes/_langchain_langgraph.pregel.Pregel.html#stream",
            "Send": "classes/_langchain_langgraph.index.Send.html",
            "START": "variables/_langchain_langgraph.index.START.html",
            "CompiledStateGraph.stream": "classes/_langchain_langgraph.index.CompiledStateGraph.html#stream",
            "task": "functions/_langchain_langgraph.index.task.html",
            "update_state": "classes/_langchain_langgraph.pregel.Pregel.html#updateState",
            "Runtime": "interfaces/_langchain_langgraph.index.Runtime.html",
            "ToolNode": "classes/_langchain_langgraph.prebuilt.ToolNode.html",
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
