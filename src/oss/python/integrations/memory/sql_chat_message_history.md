---
title: SQL (SQLAlchemy)
---

>[Structured Query Language (SQL)](https://en.wikipedia.org/wiki/SQL) is a domain-specific language used in programming and designed for managing data held in a relational database management system (RDBMS), or for stream processing in a relational data stream management system (RDSMS). It is particularly useful in handling structured data, i.e., data incorporating relations among entities and variables.

>[SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) is an open-source `SQL` toolkit and object-relational mapper (ORM) for the Python programming language released under the MIT License.

This notebook goes over a `SQLChatMessageHistory` class that allows to store chat history in any database supported by `SQLAlchemy`.

Please note that to use it with databases other than `SQLite`, you will need to install the corresponding database driver.

## Setup

The integration lives in the `langchain-community` package, so we need to install that. We also need to install the `SQLAlchemy` package.

```bash
pip install -U langchain-community SQLAlchemy langchain-openai
```

It's also helpful (but not needed) to set up [LangSmith](https://smith.langchain.com/) for best-in-class observability


```python
# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass()
```

## Usage

To use the storage you need to provide only 2 things:

1. Session Id - a unique identifier of the session, like user name, email, chat id etc.
2. Connection string - a string that specifies the database connection. It will be passed to SQLAlchemy create_engine function.


```python
from langchain_community.chat_message_histories import SQLChatMessageHistory

chat_message_history = SQLChatMessageHistory(
    session_id="test_session", connection_string="sqlite:///sqlite.db"
)

chat_message_history.add_user_message("Hello")
chat_message_history.add_ai_message("Hi")
```


```python
chat_message_history.messages
```



```output
[HumanMessage(content='Hello'), AIMessage(content='Hi')]
```


## Chaining

We can easily combine this message history class with [LCEL Runnables](/oss/how-to/message_history)

To do this we will want to use OpenAI, so we need to install that



```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
```


```python
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

chain = prompt | ChatOpenAI()
```


```python
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: SQLChatMessageHistory(
        session_id=session_id, connection_string="sqlite:///sqlite.db"
    ),
    input_messages_key="question",
    history_messages_key="history",
)
```


```python
# This is where we configure the session id
config = {"configurable": {"session_id": "<SESSION_ID>"}}
```


```python
chain_with_history.invoke({"question": "Hi! I'm bob"}, config=config)
```



```output
AIMessage(content='Hello Bob! How can I assist you today?')
```



```python
chain_with_history.invoke({"question": "Whats my name"}, config=config)
```



```output
AIMessage(content='Your name is Bob! Is there anything specific you would like assistance with, Bob?')
```
