---
title: Google Spanner
---

> [Google Cloud Spanner](https://cloud.google.com/spanner) is a highly scalable database that combines unlimited scalability with relational semantics, such as secondary indexes, strong consistency, schemas, and SQL providing 99.999% availability in one easy solution.

This notebook goes over how to use `Spanner` to store chat message history with the `SpannerChatMessageHistory` class.
Learn more about the package on [GitHub](https://github.com/googleapis/langchain-google-spanner-python/).

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/googleapis/langchain-google-spanner-python/blob/main/samples/chat_message_history.ipynb)

## Before You Begin

To run this notebook, you will need to do the following:

* [Create a Google Cloud Project](https://developers.google.com/workspace/guides/create-project)
* [Enable the Cloud Spanner API](https://console.cloud.google.com/flows/enableapi?apiid=spanner.googleapis.com)
* [Create a Spanner instance](https://cloud.google.com/spanner/docs/create-manage-instances)
* [Create a Spanner database](https://cloud.google.com/spanner/docs/create-manage-databases)

### 🦜🔗 Library Installation

The integration lives in its own `langchain-google-spanner` package, so we need to install it.

```python
%pip install -qU langchain-google-spanner
```

**Colab only:** Uncomment the following cell to restart the kernel or use the button to restart the kernel. For Vertex AI Workbench you can restart the terminal using the button on top.

```python
# # Automatically restart kernel after installs so that your environment can access the new packages
# import IPython

# app = IPython.Application.instance()
# app.kernel.do_shutdown(True)
```

### 🔐 Authentication

Authenticate to Google Cloud as the IAM user logged into this notebook in order to access your Google Cloud Project.

* If you are using Colab to run this notebook, use the cell below and continue.
* If you are using Vertex AI Workbench, check out the setup instructions [here](https://github.com/GoogleCloudPlatform/generative-ai/tree/main/setup-env).

```python
from google.colab import auth

auth.authenticate_user()
```

### ☁ Set Your Google Cloud Project

Set your Google Cloud project so that you can leverage Google Cloud resources within this notebook.

If you don't know your project ID, try the following:

* Run `gcloud config list`.
* Run `gcloud projects list`.
* See the support page: [Locate the project ID](https://support.google.com/googleapi/answer/7014113).

```python
# @markdown Please fill in the value below with your Google Cloud project ID and then run the cell.

PROJECT_ID = "my-project-id"  # @param {type:"string"}

# Set the project id
!gcloud config set project {PROJECT_ID}
```

### 💡 API Enablement

The `langchain-google-spanner` package requires that you [enable the Spanner API](https://console.cloud.google.com/flows/enableapi?apiid=spanner.googleapis.com) in your Google Cloud Project.

```python
# enable Spanner API
!gcloud services enable spanner.googleapis.com
```

## Basic Usage

### Set Spanner database values

Find your database values, in the [Spanner Instances page](https://console.cloud.google.com/spanner).

```python
# @title Set Your Values Here { display-mode: "form" }
INSTANCE = "my-instance"  # @param {type: "string"}
DATABASE = "my-database"  # @param {type: "string"}
TABLE_NAME = "message_store"  # @param {type: "string"}
```

### Initialize a table

The `SpannerChatMessageHistory` class requires a database table with a specific schema in order to store the chat message history.

The helper method `init_chat_history_table()` that can be used to create a table with the proper schema for you.

```python
from langchain_google_spanner import (
    SpannerChatMessageHistory,
)

SpannerChatMessageHistory.init_chat_history_table(table_name=TABLE_NAME)
```

### SpannerChatMessageHistory

To initialize the `SpannerChatMessageHistory` class you need to provide only 3 things:

1. `instance_id` - The name of the Spanner instance
1. `database_id` - The name of the Spanner database
1. `session_id` - A unique identifier string that specifies an id for the session.
1. `table_name` - The name of the table within the database to store the chat message history.

```python
message_history = SpannerChatMessageHistory(
    instance_id=INSTANCE,
    database_id=DATABASE,
    table_name=TABLE_NAME,
    session_id="user-session-id",
)

message_history.add_user_message("hi!")
message_history.add_ai_message("whats up?")
```

```python
message_history.messages
```

## Custom client

The client created by default is the default client. To use a non-default, a [custom client](https://cloud.google.com/spanner/docs/samples/spanner-create-client-with-query-options#spanner_create_client_with_query_options-python) can be passed to the constructor.

```python
from google.cloud import spanner

custom_client_message_history = SpannerChatMessageHistory(
    instance_id="my-instance",
    database_id="my-database",
    client=spanner.Client(...),
)
```

## Cleaning up

When the history of a specific session is obsolete and can be deleted, it can be done the following way.
Note: Once deleted, the data is no longer stored in Cloud Spanner and is gone forever.

```python
message_history = SpannerChatMessageHistory(
    instance_id=INSTANCE,
    database_id=DATABASE,
    table_name=TABLE_NAME,
    session_id="user-session-id",
)

message_history.clear()
```
