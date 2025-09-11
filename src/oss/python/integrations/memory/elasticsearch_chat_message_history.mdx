---
title: Elasticsearch
---

>[Elasticsearch](https://www.elastic.co/elasticsearch/) is a distributed, RESTful search and analytics engine, capable of performing both vector and lexical search. It is built on top of the Apache Lucene library.

This notebook shows how to use chat message history functionality with `Elasticsearch`.

## Set up Elasticsearch

There are two main ways to set up an Elasticsearch instance:

1. **Elastic Cloud.** Elastic Cloud is a managed Elasticsearch service. Sign up for a [free trial](https://cloud.elastic.co/registration?storm=langchain-notebook).

2. **Local Elasticsearch installation.** Get started with Elasticsearch by running it locally. The easiest way is to use the official Elasticsearch Docker image. See the [Elasticsearch Docker documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html) for more information.

## Install dependencies

```python
%pip install -qU  elasticsearch langchain langchain-community
```

## Authentication

### How to obtain a password for the default "elastic" user

To obtain your Elastic Cloud password for the default "elastic" user:

1. Log in to the [Elastic Cloud console](https://cloud.elastic.co)
2. Go to "Security" > "Users"
3. Locate the "elastic" user and click "Edit"
4. Click "Reset password"
5. Follow the prompts to reset the password

### Use the Username/password

```python
es_username = os.environ.get("ES_USERNAME", "elastic")
es_password = os.environ.get("ES_PASSWORD", "change me...")

history = ElasticsearchChatMessageHistory(
    es_url=es_url,
    es_user=es_username,
    es_password=es_password,
    index="test-history",
    session_id="test-session"
)
```

### How to obtain an API key

To obtain an API key:

1. Log in to the [Elastic Cloud console](https://cloud.elastic.co)
2. Open `Kibana` and go to Stack Management > API Keys
3. Click "Create API key"
4. Enter a name for the API key and click "Create"

### Use the API key

```python
es_api_key = os.environ.get("ES_API_KEY")

history = ElasticsearchChatMessageHistory(
    es_api_key=es_api_key,
    index="test-history",
    session_id="test-session"
)
```

## Initialize Elasticsearch client and chat message history

```python
import os

from langchain_community.chat_message_histories import (
    ElasticsearchChatMessageHistory,
)

es_url = os.environ.get("ES_URL", "http://localhost:9200")

# If using Elastic Cloud:
# es_cloud_id = os.environ.get("ES_CLOUD_ID")

# Note: see Authentication section for various authentication methods

history = ElasticsearchChatMessageHistory(
    es_url=es_url, index="test-history", session_id="test-session"
)
```

## Use the chat message history

```python
history.add_user_message("hi!")
history.add_ai_message("whats up?")
```

```output
indexing message content='hi!' additional_kwargs={} example=False
indexing message content='whats up?' additional_kwargs={} example=False
```
