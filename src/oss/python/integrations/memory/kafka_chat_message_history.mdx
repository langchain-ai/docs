---
title: Kafka
---

[Kafka](https://github.com/apache/kafka) is a distributed messaging system that is used to publish and subscribe to streams of records.
This demo shows how to use `KafkaChatMessageHistory` to store and retrieve chat messages from a Kafka cluster.

A running Kafka cluster is required to run the demo. You can follow this [instruction](https://developer.confluent.io/get-started/python) to create a Kafka cluster locally.

```python
from langchain_community.chat_message_histories import KafkaChatMessageHistory

chat_session_id = "chat-message-history-kafka"
bootstrap_servers = "localhost:64797"  # host:port. `localhost:Plaintext Ports` if setup Kafka cluster locally
history = KafkaChatMessageHistory(
    chat_session_id,
    bootstrap_servers,
)
```

Optional parameters to construct `KafkaChatMessageHistory`:

- `ttl_ms`: Time to live in milliseconds for the chat messages.
- `partition`: Number of partition of the topic to store the chat messages.
- `replication_factor`: Replication factor of the topic to store the chat messages.

`KafkaChatMessageHistory` internally uses Kafka consumer to read chat messages, and it has the ability to mark the consumed position persistently. It has following methods to retrieve chat messages:

- `messages`: continue consuming chat messages from last one.
- `messages_from_beginning`: reset the consumer to the beginning of the history and consume messages. Optional parameters:
    1. `max_message_count`: maximum number of messages to read.
    2. `max_time_sec`: maximum time in seconds to read messages.
- `messages_from_latest`: reset the consumer to the end of the chat history and try consuming messages. Optional parameters same as above.
- `messages_from_last_consumed`: return messages continuing from the last consumed message, similar to `messages`, but with optional parameters.

`max_message_count` and `max_time_sec` are used to avoid blocking indefinitely when retrieving messages.
As a result, `messages` and other methods to retrieve messages may not return all messages in the chat history. You will need to specify `max_message_count` and `max_time_sec` to retrieve all chat history in a single batch.

Add messages and retrieve.

```python
history.add_user_message("hi!")
history.add_ai_message("whats up?")

history.messages
```

```output
[HumanMessage(content='hi!'), AIMessage(content='whats up?')]
```

Calling `messages` again returns an empty list because the consumer is at the end of the chat history.

```python
history.messages
```

```output
[]
```

Add new messages and continue consuming.

```python
history.add_user_message("hi again!")
history.add_ai_message("whats up again?")
history.messages
```

```output
[HumanMessage(content='hi again!'), AIMessage(content='whats up again?')]
```

To reset the consumer and read from beginning:

```python
history.messages_from_beginning()
```

```output
[HumanMessage(content='hi again!'),
 AIMessage(content='whats up again?'),
 HumanMessage(content='hi!'),
 AIMessage(content='whats up?')]
```

Set the consumer to the end of the chat history, add a couple of new messages, and consume:

```python
history.messages_from_latest()
history.add_user_message("HI!")
history.add_ai_message("WHATS UP?")
history.messages
```

```output
[HumanMessage(content='HI!'), AIMessage(content='WHATS UP?')]
```
