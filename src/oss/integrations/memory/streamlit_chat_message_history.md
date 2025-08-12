# Streamlit

>[Streamlit](https://docs.streamlit.io/) is an open-source Python library that makes it easy to create and share beautiful, 
custom web apps for machine learning and data science.

This notebook goes over how to store and use chat message history in a `Streamlit` app. `StreamlitChatMessageHistory` will store messages in
[Streamlit session state](https://docs.streamlit.io/library/api-reference/session-state)
at the specified `key=`. The default key is `"langchain_messages"`.

- Note, `StreamlitChatMessageHistory` only works when run in a Streamlit app.
- You may also be interested in [StreamlitCallbackHandler](/oss/integrations/callbacks/streamlit) for LangChain.
- For more on Streamlit check out their
[getting started documentation](https://docs.streamlit.io/library/get-started).

The integration lives in the `langchain-community` package, so we need to install that. We also need to install `streamlit`.

```
pip install -U langchain-community streamlit
```

You can see the [full app example running here](https://langchain-st-memory.streamlit.app/), and more examples in
[github.com/langchain-ai/streamlit-agent](https://github.com/langchain-ai/streamlit-agent).


```python
from langchain_community.chat_message_histories import (
    StreamlitChatMessageHistory,
)

history = StreamlitChatMessageHistory(key="chat_messages")

history.add_user_message("hi!")
history.add_ai_message("whats up?")
```


```python
history.messages
```

We can easily combine this message history class with [LCEL Runnables](/oss/how-to/message_history).

The history will be persisted across re-runs of the Streamlit app within a given user session. A given `StreamlitChatMessageHistory` will NOT be persisted or shared across user sessions.


```python
# Optionally, specify your own session_state key for storing messages
msgs = StreamlitChatMessageHistory(key="special_app_key")

if len(msgs.messages) == 0:
    msgs.add_ai_message("How can I help you?")
```


```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an AI chatbot having a conversation with a human."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

chain = prompt | ChatOpenAI()
```


```python
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: msgs,  # Always return the instance created earlier
    input_messages_key="question",
    history_messages_key="history",
)
```

Conversational Streamlit apps will often re-draw each previous chat message on every re-run. This is easy to do by iterating through `StreamlitChatMessageHistory.messages`:


```python
import streamlit as st

for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

if prompt := st.chat_input():
    st.chat_message("human").write(prompt)

    # As usual, new messages are added to StreamlitChatMessageHistory when the Chain is called.
    config = {"configurable": {"session_id": "any"}}
    response = chain_with_history.invoke({"question": prompt}, config)
    st.chat_message("ai").write(response.content)
```

**[View the final app](https://langchain-st-memory.streamlit.app/).**
