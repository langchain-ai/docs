---
title: Couchbase
---

> Couchbase is an award-winning distributed NoSQL cloud database that delivers unmatched versatility, performance, scalability, and financial value for all of your cloud, mobile, AI, and edge computing applications. Couchbase embraces AI with coding assistance for developers and vector search for their applications.

This notebook goes over how to use the `CouchbaseChatMessageHistory` class to store the chat message history in a Couchbase cluster

## Set Up Couchbase Cluster

To run this demo, you need a Couchbase Cluster.

You can work with both [Couchbase Capella](https://www.couchbase.com/products/capella/) and your self-managed Couchbase Server.

## Install Dependencies

`CouchbaseChatMessageHistory` lives inside the `langchain-couchbase` package.

```python
%pip install -qU langchain-couchbase
```

```output
Note: you may need to restart the kernel to use updated packages.
```

## Create Couchbase Connection Object

We create a connection to the Couchbase cluster initially and then pass the cluster object to the Vector Store.

Here, we are connecting using the username and password. You can also connect using any other supported way to your cluster.

For more information on connecting to the Couchbase cluster, please check the [Python SDK documentation](https://docs.couchbase.com/python-sdk/current/hello-world/start-using-sdk.html#connect).

```python
COUCHBASE_CONNECTION_STRING = (
    "couchbase://localhost"  # or "couchbases://localhost" if using TLS
)
DB_USERNAME = "Administrator"
DB_PASSWORD = "Password"
```

```python
from datetime import timedelta

from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions

auth = PasswordAuthenticator(DB_USERNAME, DB_PASSWORD)
options = ClusterOptions(auth)
cluster = Cluster(COUCHBASE_CONNECTION_STRING, options)

# Wait until the cluster is ready for use.
cluster.wait_until_ready(timedelta(seconds=5))
```

We will now set the bucket, scope, and collection names in the Couchbase cluster that we want to use for storing the message history.

Note that the bucket, scope, and collection need to exist before using them to store the message history.

```python
BUCKET_NAME = "langchain-testing"
SCOPE_NAME = "_default"
COLLECTION_NAME = "conversational_cache"
```

## Usage

In order to store the messages, you need the following:

- Couchbase Cluster object: Valid connection to the Couchbase cluster
- bucket_name: Bucket in cluster to store the chat message history
- scope_name: Scope in bucket to store the message history
- collection_name: Collection in scope to store the message history
- session_id: Unique identifier for the session

Optionally you can configure the following:

- session_id_key: Field in the chat message documents to store the `session_id`
- message_key: Field in the chat message documents to store the message content
- create_index: Used to specify if the index needs to be created on the collection. By default, an index is created on the `message_key` and the `session_id_key` of the documents
- ttl: Used to specify a time in `timedelta` to live for the documents after which they will get deleted automatically from the storage.

```python
from langchain_couchbase.chat_message_histories import CouchbaseChatMessageHistory

message_history = CouchbaseChatMessageHistory(
    cluster=cluster,
    bucket_name=BUCKET_NAME,
    scope_name=SCOPE_NAME,
    collection_name=COLLECTION_NAME,
    session_id="test-session",
)

message_history.add_user_message("hi!")

message_history.add_ai_message("how are you doing?")
```

```python
message_history.messages
```

```output
[HumanMessage(content='hi!'), AIMessage(content='how are you doing?')]
```

## Specifying a Time to Live (TTL) for the Chat Messages

The stored messages can be deleted after a specified time automatically by specifying a `ttl` parameter along with the initialization of the chat message history store.

```python
from langchain_couchbase.chat_message_histories import CouchbaseChatMessageHistory

message_history = CouchbaseChatMessageHistory(
    cluster=cluster,
    bucket_name=BUCKET_NAME,
    scope_name=SCOPE_NAME,
    collection_name=COLLECTION_NAME,
    session_id="test-session",
    ttl=timedelta(hours=24),
)
```

## Chaining

The chat message history class can be used with [LCEL Runnables](https://python.langchain.com/docs/how_to/message_history/)

```python
import getpass
import os

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = getpass.getpass()
```

```python
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

# Create the LCEL runnable
chain = prompt | ChatOpenAI()
```

```python
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: CouchbaseChatMessageHistory(
        cluster=cluster,
        bucket_name=BUCKET_NAME,
        scope_name=SCOPE_NAME,
        collection_name=COLLECTION_NAME,
        session_id=session_id,
    ),
    input_messages_key="question",
    history_messages_key="history",
)
```

```python
# This is where we configure the session id
config = {"configurable": {"session_id": "testing"}}
```

```python
chain_with_history.invoke({"question": "Hi! I'm bob"}, config=config)
```

```output
AIMessage(content='Hello, Bob! How can I assist you today?', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 11, 'prompt_tokens': 22, 'total_tokens': 33}, 'model_name': 'gpt-3.5-turbo-0125', 'system_fingerprint': None, 'finish_reason': 'stop', 'logprobs': None}, id='run-62e54e3d-db70-429d-9ee0-e5e8eb2489a1-0', usage_metadata={'input_tokens': 22, 'output_tokens': 11, 'total_tokens': 33})
```

```python
chain_with_history.invoke({"question": "Whats my name"}, config=config)
```

```output
AIMessage(content='Your name is Bob.', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 5, 'prompt_tokens': 44, 'total_tokens': 49}, 'model_name': 'gpt-3.5-turbo-0125', 'system_fingerprint': None, 'finish_reason': 'stop', 'logprobs': None}, id='run-d84a570a-45f3-4931-814a-078761170bca-0', usage_metadata={'input_tokens': 44, 'output_tokens': 5, 'total_tokens': 49})
```
