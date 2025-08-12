# AWS DynamoDB

>[Amazon AWS DynamoDB](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/dynamodb/index.html) is a fully managed `NoSQL` database service that provides fast and predictable performance with seamless scalability.

This notebook goes over how to use `DynamoDB` to store chat message history with `DynamoDBChatMessageHistory` class.

## Setup

First make sure you have correctly configured the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html). Then make sure you have installed the `langchain-community` package, so we need to install that. We also need to install the `boto3` package.

```bash
pip install -U langchain-community boto3
```

It's also helpful (but not needed) to set up [LangSmith](https://smith.langchain.com/) for best-in-class observability


```python
# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass()
```


```python
from langchain_community.chat_message_histories import (
    DynamoDBChatMessageHistory,
)
```

## Create Table

Now, create the `DynamoDB` Table where we will be storing messages:


```python
import boto3

# Get the service resource.
dynamodb = boto3.resource("dynamodb")

# Create the DynamoDB table.
table = dynamodb.create_table(
    TableName="SessionTable",
    KeySchema=[{"AttributeName": "SessionId", "KeyType": "HASH"}],
    AttributeDefinitions=[{"AttributeName": "SessionId", "AttributeType": "S"}],
    BillingMode="PAY_PER_REQUEST",
)

# Wait until the table exists.
table.meta.client.get_waiter("table_exists").wait(TableName="SessionTable")

# Print out some data about the table.
print(table.item_count)
```
```output
0
```
## DynamoDBChatMessageHistory


```python
history = DynamoDBChatMessageHistory(table_name="SessionTable", session_id="0")

history.add_user_message("hi!")

history.add_ai_message("whats up?")
```


```python
history.messages
```



```output
[HumanMessage(content='hi!'), AIMessage(content='whats up?')]
```


## DynamoDBChatMessageHistory with Custom Endpoint URL

Sometimes it is useful to specify the URL to the AWS endpoint to connect to. For instance, when you are running locally against [Localstack](https://localstack.cloud/). For those cases you can specify the URL via the `endpoint_url` parameter in the constructor.


```python
history = DynamoDBChatMessageHistory(
    table_name="SessionTable",
    session_id="0",
    endpoint_url="http://localhost.localstack.cloud:4566",
)
```

## DynamoDBChatMessageHistory With Composite Keys
The default key for DynamoDBChatMessageHistory is ```{"SessionId": self.session_id}```, but you can modify this to match your table design.

### Primary Key Name
You may modify the primary key by passing in a primary_key_name value in the constructor, resulting in the following:
```{self.primary_key_name: self.session_id}```
### Composite Keys
When using an existing DynamoDB table, you may need to modify the key structure from the default of to something including a Sort Key. To do this you may use the ```key``` parameter.

Passing a value for key will override the primary_key parameter, and the resulting key structure will be the passed value.



```python
composite_table = dynamodb.create_table(
    TableName="CompositeTable",
    KeySchema=[
        {"AttributeName": "PK", "KeyType": "HASH"},
        {"AttributeName": "SK", "KeyType": "RANGE"},
    ],
    AttributeDefinitions=[
        {"AttributeName": "PK", "AttributeType": "S"},
        {"AttributeName": "SK", "AttributeType": "S"},
    ],
    BillingMode="PAY_PER_REQUEST",
)

# Wait until the table exists.
composite_table.meta.client.get_waiter("table_exists").wait(TableName="CompositeTable")

# Print out some data about the table.
print(composite_table.item_count)
```
```output
0
```

```python
my_key = {
    "PK": "session_id::0",
    "SK": "langchain_history",
}

composite_key_history = DynamoDBChatMessageHistory(
    table_name="CompositeTable",
    session_id="0",
    endpoint_url="http://localhost.localstack.cloud:4566",
    key=my_key,
)

composite_key_history.add_user_message("hello, composite dynamodb table!")

composite_key_history.messages
```



```output
[HumanMessage(content='hello, composite dynamodb table!')]
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
    lambda session_id: DynamoDBChatMessageHistory(
        table_name="SessionTable", session_id=session_id
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
