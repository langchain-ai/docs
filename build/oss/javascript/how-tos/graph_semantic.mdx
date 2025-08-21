---
sidebar_position: 1
---

# How to add a semantic layer over graph database

You can use database queries to retrieve information from a graph database like Neo4j.
One option is to use LLMs to generate Cypher statements.
While that option provides excellent flexibility, the solution could be brittle and not consistently generating precise Cypher statements.
Instead of generating Cypher statements, we can implement Cypher templates as tools in a semantic layer that an LLM agent can interact with.

![graph_semantic.png](../../static/img/graph_semantic.png)

## Setup

First, get required packages and set environment variables:


```python
%pip install --upgrade --quiet  langchain langchain-neo4j langchain-openai
```

We default to OpenAI models in this guide, but you can swap them out for the model provider of your choice.


```python
import getpass
import os

os.environ["OPENAI_API_KEY"] = getpass.getpass()

# Uncomment the below to use LangSmith. Not required.
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass()
# os.environ["LANGSMITH_TRACING"] = "true"
```
```output
 ········
```
Next, we need to define Neo4j credentials.
Follow [these installation steps](https://neo4j.com/docs/operations-manual/current/installation/) to set up a Neo4j database.


```python
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "password"
```

The below example will create a connection with a Neo4j database and will populate it with example data about movies and their actors.


```python
from langchain_neo4j import Neo4jGraph

graph = Neo4jGraph(refresh_schema=False)

# Import movie information

movies_query = """
LOAD CSV WITH HEADERS FROM 
'https://raw.githubusercontent.com/tomasonjo/blog-datasets/main/movies/movies_small.csv'
AS row
MERGE (m:Movie {id:row.movieId})
SET m.released = date(row.released),
    m.title = row.title,
    m.imdbRating = toFloat(row.imdbRating)
FOREACH (director in split(row.director, '|') | 
    MERGE (p:Person {name:trim(director)})
    MERGE (p)-[:DIRECTED]->(m))
FOREACH (actor in split(row.actors, '|') | 
    MERGE (p:Person {name:trim(actor)})
    MERGE (p)-[:ACTED_IN]->(m))
FOREACH (genre in split(row.genres, '|') | 
    MERGE (g:Genre {name:trim(genre)})
    MERGE (m)-[:IN_GENRE]->(g))
"""

graph.query(movies_query)
```



```output
[]
```


## Custom tools with Cypher templates

A semantic layer consists of various tools exposed to an LLM that it can use to interact with a knowledge graph.
They can be of various complexity. You can think of each tool in a semantic layer as a function.

The function we will implement is to retrieve information about movies or their cast.


```python
description_query = """
MATCH (m:Movie|Person)
WHERE m.title CONTAINS $candidate OR m.name CONTAINS $candidate
MATCH (m)-[r:ACTED_IN|IN_GENRE]-(t)
WITH m, type(r) as type, collect(coalesce(t.name, t.title)) as names
WITH m, type+": "+reduce(s="", n IN names | s + n + ", ") as types
WITH m, collect(types) as contexts
WITH m, "type:" + labels(m)[0] + "\ntitle: "+ coalesce(m.title, m.name) 
       + "\nyear: "+coalesce(m.released,"") +"\n" +
       reduce(s="", c in contexts | s + substring(c, 0, size(c)-2) +"\n") as context
RETURN context LIMIT 1
"""


def get_information(entity: str) -> str:
    try:
        data = graph.query(description_query, params={"candidate": entity})
        return data[0]["context"]
    except IndexError:
        return "No information was found"
```

You can observe that we have defined the Cypher statement used to retrieve information.
Therefore, we can avoid generating Cypher statements and use the LLM agent to only populate the input parameters.
To provide additional information to an LLM agent about when to use the tool and their input parameters, we wrap the function as a tool.


```python
from typing import Optional, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class InformationInput(BaseModel):
    entity: str = Field(description="movie or a person mentioned in the question")


class InformationTool(BaseTool):
    name: str = "Information"
    description: str = (
        "useful for when you need to answer questions about various actors or movies"
    )
    args_schema: Type[BaseModel] = InformationInput

    def _run(
        self,
        entity: str,
    ) -> str:
        """Use the tool."""
        return get_information(entity)

    async def _arun(
        self,
        entity: str,
    ) -> str:
        """Use the tool asynchronously."""
        return get_information(entity)
```

## LangGraph Agent

We will implement a straightforward ReAct agent using LangGraph.

The agent consists of an LLM and tools step. As we interact with the agent, we will first call the LLM to decide if we should use tools. Then we will run a loop:

If the agent said to take an action (i.e. call tool), we’ll run the tools and pass the results back to the agent.
If the agent did not ask to run tools, we will finish (respond to the user).

The code implementation is as straightforward as it gets. First we bind the tools to the LLM and define the assistant step.


```python
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState

llm = ChatOpenAI(model="gpt-4o")

tools = [InformationTool()]
llm_with_tools = llm.bind_tools(tools)

# System message
sys_msg = SystemMessage(
    content="You are a helpful assistant tasked with finding and explaining relevant information about movies."
)


# Node
def assistant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}
```

Next we define the LangGraph flow.


```python
from IPython.display import Image, display
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

# Graph
builder = StateGraph(MessagesState)

# Define nodes: these do the work
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define edges: these determine how the control flow moves
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "assistant")
react_graph = builder.compile()

# Show
display(Image(react_graph.get_graph(xray=True).draw_mermaid_png()))
```

<p>
<img src="data:image/png;base64,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" />
</p>

Let's test the workflow now with an example question.


```python
input_messages = [HumanMessage(content="Who played in the Casino?")]
messages = react_graph.invoke({"messages": input_messages})
for m in messages["messages"]:
    m.pretty_print()
```
```output
================================ Human Message =================================

Who played in the Casino?
================================== Ai Message ==================================
Tool Calls:
  Information (call_j4usgFStGtBM16fuguRaeoGc)
 Call ID: call_j4usgFStGtBM16fuguRaeoGc
  Args:
    entity: Casino
================================= Tool Message =================================
Name: Information

type:Movie
title: Casino
year: 1995-11-22
ACTED_IN: Robert De Niro, Joe Pesci, Sharon Stone, James Woods
IN_GENRE: Drama, Crime

================================== Ai Message ==================================

The movie "Casino," released in 1995, features the following actors:

- Robert De Niro
- Joe Pesci
- Sharon Stone
- James Woods

The film is in the Drama and Crime genres.
```

```python

```
