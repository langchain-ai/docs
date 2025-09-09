---
title: Astra DB
---

> [DataStax Astra DB](https://docs.datastax.com/en/astra-db-serverless/index.html) is a serverless
> AI-ready database built on `Apache Cassandra®` and made conveniently availablev
> through an easy-to-use JSON API.

This notebook goes over how to use Astra DB to store chat message history.

## Setup

To run this notebook you need a running Astra DB. Get the connection secrets on your Astra dashboard:

- the API Endpoint looks like `https://01234567-89ab-cdef-0123-456789abcdef-us-east1.apps.astra.datastax.com`;
- the Database Token looks like `AstraCS:aBcD0123...`.

```python
!pip install "langchain-astradb>=0.6,<0.7"
```

### Set up the database connection parameters and secrets

```python
import getpass

ASTRA_DB_API_ENDPOINT = input("ASTRA_DB_API_ENDPOINT = ")
ASTRA_DB_APPLICATION_TOKEN = getpass.getpass("ASTRA_DB_APPLICATION_TOKEN = ")
```

```output
ASTRA_DB_API_ENDPOINT =  https://01234567-89ab-cdef-0123-456789abcdef-us-east1.apps.astra.datastax.com
ASTRA_DB_APPLICATION_TOKEN =  ········
```

## Example

```python
from langchain_astradb import AstraDBChatMessageHistory

message_history = AstraDBChatMessageHistory(
    session_id="test-session",
    api_endpoint=ASTRA_DB_API_ENDPOINT,
    token=ASTRA_DB_APPLICATION_TOKEN,
)

message_history.add_user_message("hi!")

message_history.add_ai_message("hello, how are you?")
```

[**API Reference:** `AstraDBChatMessageHistory`](https://python.langchain.com/api_reference/astradb/chat_message_histories/langchain_astradb.chat_message_histories.AstraDBChatMessageHistory.html#langchain_astradb.chat_message_histories.AstraDBChatMessageHistory)

```python
message_history.messages
```

```output
[HumanMessage(content='hi!', additional_kwargs={}, response_metadata={}),
 AIMessage(content='hello, how are you?', additional_kwargs={}, response_metadata={})]
```
