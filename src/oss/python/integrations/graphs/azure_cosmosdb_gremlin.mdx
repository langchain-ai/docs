---
title: Azure Cosmos DB for Apache Gremlin
---

>[Azure Cosmos DB for Apache Gremlin](https://learn.microsoft.com/en-us/azure/cosmos-db/gremlin/introduction) is a graph database service that can be used to store massive graphs with billions of vertices and edges. You can query the graphs with millisecond latency and evolve the graph structure easily.
>
>[Gremlin](https://en.wikipedia.org/wiki/Gremlin_(query_language)) is a graph traversal language and virtual machine developed by `Apache TinkerPop` of the `Apache Software Foundation`.

This notebook shows how to use LLMs to provide a natural language interface to a graph database you can query with the `Gremlin` query language.

## Setting up

Install a library:

```python
!pip3 install gremlinpython
```

You will need an Azure CosmosDB Graph database instance. One option is to create a [free CosmosDB Graph database instance in Azure](https://learn.microsoft.com/en-us/azure/cosmos-db/free-tier).

When you create your Cosmos DB account and Graph, use `/type` as a partition key.

```python
cosmosdb_name = "mycosmosdb"
cosmosdb_db_id = "graphtesting"
cosmosdb_db_graph_id = "mygraph"
cosmosdb_access_Key = "longstring=="
```

```python
import nest_asyncio
from langchain_community.chains.graph_qa.gremlin import GremlinQAChain
from langchain_community.graphs import GremlinGraph
from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from langchain_core.documents import Document
from langchain_openai import AzureChatOpenAI
```

```python
graph = GremlinGraph(
    url=f"wss://{cosmosdb_name}.gremlin.cosmos.azure.com:443/",
    username=f"/dbs/{cosmosdb_db_id}/colls/{cosmosdb_db_graph_id}",
    password=cosmosdb_access_Key,
)
```

## Seeding the database

Assuming your database is empty, you can populate it using the GraphDocuments

For Gremlin, always add property called 'label' for each Node.
If no label is set, Node.type is used as a label.
For cosmos using natural id's make sense, as they are visible in the graph explorer.

```python
source_doc = Document(
    page_content="Matrix is a movie where Keanu Reeves, Laurence Fishburne and Carrie-Anne Moss acted."
)
movie = Node(id="The Matrix", properties={"label": "movie", "title": "The Matrix"})
actor1 = Node(id="Keanu Reeves", properties={"label": "actor", "name": "Keanu Reeves"})
actor2 = Node(
    id="Laurence Fishburne", properties={"label": "actor", "name": "Laurence Fishburne"}
)
actor3 = Node(
    id="Carrie-Anne Moss", properties={"label": "actor", "name": "Carrie-Anne Moss"}
)
rel1 = Relationship(
    id=5, type="ActedIn", source=actor1, target=movie, properties={"label": "ActedIn"}
)
rel2 = Relationship(
    id=6, type="ActedIn", source=actor2, target=movie, properties={"label": "ActedIn"}
)
rel3 = Relationship(
    id=7, type="ActedIn", source=actor3, target=movie, properties={"label": "ActedIn"}
)
rel4 = Relationship(
    id=8,
    type="Starring",
    source=movie,
    target=actor1,
    properties={"label": "Strarring"},
)
rel5 = Relationship(
    id=9,
    type="Starring",
    source=movie,
    target=actor2,
    properties={"label": "Strarring"},
)
rel6 = Relationship(
    id=10,
    type="Straring",
    source=movie,
    target=actor3,
    properties={"label": "Strarring"},
)
graph_doc = GraphDocument(
    nodes=[movie, actor1, actor2, actor3],
    relationships=[rel1, rel2, rel3, rel4, rel5, rel6],
    source=source_doc,
)
```

```python
# The underlying python-gremlin has a problem when running in notebook
# The following line is a workaround to fix the problem
nest_asyncio.apply()

# Add the document to the CosmosDB graph.
graph.add_graph_documents([graph_doc])
```

## Refresh graph schema information

If the schema of database changes (after updates), you can refresh the schema information.

```python
graph.refresh_schema()
```

```python
print(graph.schema)
```

## Querying the graph

We can now use the gremlin QA chain to ask question of the graph

```python
chain = GremlinQAChain.from_llm(
    AzureChatOpenAI(
        temperature=0,
        azure_deployment="gpt-4-turbo",
    ),
    graph=graph,
    verbose=True,
)
```

```python
chain.invoke("Who played in The Matrix?")
```

```python
chain.run("How many people played in The Matrix?")
```
