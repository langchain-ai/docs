---
title: DingoDB
---

>[DingoDB](https://dingodb.readthedocs.io/en/latest/) is a distributed multi-mode vector database, which combines the characteristics of data lakes and vector databases, and can store data of any type and size (Key-Value, PDF, audio, video, etc.). It has real-time low-latency processing capabilities to achieve rapid insight and response, and can efficiently conduct instant analysis and process multi-modal data.

In the walkthrough, we'll demo the `SelfQueryRetriever` with a `DingoDB` vector store.

## Creating a DingoDB index

First we'll want to create a `DingoDB` vector store and seed it with some data. We've created a small demo set of documents that contain summaries of movies.

To use DingoDB, you should have a [DingoDB instance up and running](https://github.com/dingodb/dingo-deploy/blob/main/README.md).

**Note:** The self-query retriever requires you to have `lark` package installed.

```python
%pip install -qU  dingodb
# or install latest:
%pip install -qU  git+https://git@github.com/dingodb/pydingo.git
```

We want to use `OpenAIEmbeddings` so we have to get the OpenAI API Key.

```python
import os

OPENAI_API_KEY = ""

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
```

```python
from langchain_community.vectorstores import Dingo
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
# create new index
from dingodb import DingoDB

index_name = "langchain_demo"

dingo_client = DingoDB(user="", password="", host=["172.30.14.221:13000"])
# First, check if our index already exists. If it doesn't, we create it
if (
    index_name not in dingo_client.get_index()
    and index_name.upper() not in dingo_client.get_index()
):
    # we create a new index, modify to your own
    dingo_client.create_index(
        index_name=index_name, dimension=1536, metric_type="cosine", auto_id=False
    )
```

```python
docs = [
    Document(
        page_content="A bunch of scientists bring back dinosaurs and mayhem breaks loose",
        metadata={"year": 1993, "rating": 7.7, "genre": '"action", "science fiction"'},
    ),
    Document(
        page_content="Leo DiCaprio gets lost in a dream within a dream within a dream within a ...",
        metadata={"year": 2010, "director": "Christopher Nolan", "rating": 8.2},
    ),
    Document(
        page_content="A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea",
        metadata={"year": 2006, "director": "Satoshi Kon", "rating": 8.6},
    ),
    Document(
        page_content="A bunch of normal-sized women are supremely wholesome and some men pine after them",
        metadata={"year": 2019, "director": "Greta Gerwig", "rating": 8.3},
    ),
    Document(
        page_content="Toys come alive and have a blast doing so",
        metadata={"year": 1995, "genre": "animated"},
    ),
    Document(
        page_content="Three men walk into the Zone, three men walk out of the Zone",
        metadata={
            "year": 1979,
            "director": "Andrei Tarkovsky",
            "genre": '"science fiction", "thriller"',
            "rating": 9.9,
        },
    ),
]
vectorstore = Dingo.from_documents(
    docs, embeddings, index_name=index_name, client=dingo_client
)
```

```python
dingo_client.get_index()
dingo_client.delete_index("langchain_demo")
```

```output
True
```

```python
dingo_client.vector_count("langchain_demo")
```

```output
9
```

## Creating our self-querying retriever

Now we can instantiate our retriever. To do this we'll need to provide some information upfront about the metadata fields that our documents support and a short description of the document contents.

```python
from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_openai import OpenAI

metadata_field_info = [
    AttributeInfo(
        name="genre",
        description="The genre of the movie",
        type="string or list[string]",
    ),
    AttributeInfo(
        name="year",
        description="The year the movie was released",
        type="integer",
    ),
    AttributeInfo(
        name="director",
        description="The name of the movie director",
        type="string",
    ),
    AttributeInfo(
        name="rating", description="A 1-10 rating for the movie", type="float"
    ),
]
document_content_description = "Brief summary of a movie"
llm = OpenAI(temperature=0)
retriever = SelfQueryRetriever.from_llm(
    llm, vectorstore, document_content_description, metadata_field_info, verbose=True
)
```

## Testing it out

And now we can try actually using our retriever!

```python
# This example only specifies a relevant query
retriever.invoke("What are some movies about dinosaurs")
```

```output
query='dinosaurs' filter=None limit=None
```

```output
[Document(page_content='A bunch of scientists bring back dinosaurs and mayhem breaks loose', metadata={'id': 1183188982475, 'text': 'A bunch of scientists bring back dinosaurs and mayhem breaks loose', 'score': 0.13397777, 'year': {'value': 1993}, 'rating': {'value': 7.7}, 'genre': '"action", "science fiction"'}),
 Document(page_content='Toys come alive and have a blast doing so', metadata={'id': 1183189196391, 'text': 'Toys come alive and have a blast doing so', 'score': 0.18994397, 'year': {'value': 1995}, 'genre': 'animated'}),
 Document(page_content='Three men walk into the Zone, three men walk out of the Zone', metadata={'id': 1183189220159, 'text': 'Three men walk into the Zone, three men walk out of the Zone', 'score': 0.23288351, 'year': {'value': 1979}, 'director': 'Andrei Tarkovsky', 'rating': {'value': 9.9}, 'genre': '"science fiction", "thriller"'}),
 Document(page_content='A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea', metadata={'id': 1183189148854, 'text': 'A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea', 'score': 0.24421334, 'year': {'value': 2006}, 'director': 'Satoshi Kon', 'rating': {'value': 8.6}})]
```

```python
# This example only specifies a filter
retriever.invoke("I want to watch a movie rated higher than 8.5")
```

```output
query=' ' filter=Comparison(comparator=<Comparator.GT: 'gt'>, attribute='rating', value=8.5) limit=None
comparator=<Comparator.GT: 'gt'> attribute='rating' value=8.5
```

```output
[Document(page_content='Three men walk into the Zone, three men walk out of the Zone', metadata={'id': 1183189220159, 'text': 'Three men walk into the Zone, three men walk out of the Zone', 'score': 0.25033575, 'year': {'value': 1979}, 'director': 'Andrei Tarkovsky', 'genre': '"science fiction", "thriller"', 'rating': {'value': 9.9}}),
 Document(page_content='A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea', metadata={'id': 1183189148854, 'text': 'A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea', 'score': 0.26431882, 'year': {'value': 2006}, 'director': 'Satoshi Kon', 'rating': {'value': 8.6}})]
```

```python
# This example specifies a query and a filter
retriever.invoke("Has Greta Gerwig directed any movies about women")
```

```output
query='women' filter=Comparison(comparator=<Comparator.EQ: 'eq'>, attribute='director', value='Greta Gerwig') limit=None
comparator=<Comparator.EQ: 'eq'> attribute='director' value='Greta Gerwig'
```

```output
[Document(page_content='A bunch of normal-sized women are supremely wholesome and some men pine after them', metadata={'id': 1183189172623, 'text': 'A bunch of normal-sized women are supremely wholesome and some men pine after them', 'score': 0.19482517, 'year': {'value': 2019}, 'director': 'Greta Gerwig', 'rating': {'value': 8.3}})]
```

```python
# This example specifies a composite filter
retriever.invoke("What's a highly rated (above 8.5) science fiction film?")
```

```output
query='science fiction' filter=Comparison(comparator=<Comparator.GT: 'gt'>, attribute='rating', value=8.5) limit=None
comparator=<Comparator.GT: 'gt'> attribute='rating' value=8.5
```

```output
[Document(page_content='A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea', metadata={'id': 1183189148854, 'text': 'A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea', 'score': 0.19805312, 'year': {'value': 2006}, 'director': 'Satoshi Kon', 'rating': {'value': 8.6}}),
 Document(page_content='Three men walk into the Zone, three men walk out of the Zone', metadata={'id': 1183189220159, 'text': 'Three men walk into the Zone, three men walk out of the Zone', 'score': 0.225586, 'year': {'value': 1979}, 'director': 'Andrei Tarkovsky', 'rating': {'value': 9.9}, 'genre': '"science fiction", "thriller"'})]
```

```python
# This example specifies a query and composite filter
retriever.invoke(
    "What's a movie after 1990 but before 2005 that's all about toys, and preferably is animated"
)
```

```output
query='toys' filter=Operation(operator=<Operator.AND: 'and'>, arguments=[Operation(operator=<Operator.AND: 'and'>, arguments=[Comparison(comparator=<Comparator.GT: 'gt'>, attribute='year', value=1990), Comparison(comparator=<Comparator.LT: 'lt'>, attribute='year', value=2005)]), Comparison(comparator=<Comparator.EQ: 'eq'>, attribute='genre', value='animated')]) limit=None
operator=<Operator.AND: 'and'> arguments=[Operation(operator=<Operator.AND: 'and'>, arguments=[Comparison(comparator=<Comparator.GT: 'gt'>, attribute='year', value=1990), Comparison(comparator=<Comparator.LT: 'lt'>, attribute='year', value=2005)]), Comparison(comparator=<Comparator.EQ: 'eq'>, attribute='genre', value='animated')]
```

```output
[Document(page_content='Toys come alive and have a blast doing so', metadata={'id': 1183189196391, 'text': 'Toys come alive and have a blast doing so', 'score': 0.133829, 'year': {'value': 1995}, 'genre': 'animated'})]
```

## Filter k

We can also use the self query retriever to specify `k`: the number of documents to fetch.

We can do this by passing `enable_limit=True` to the constructor.

```python
retriever = SelfQueryRetriever.from_llm(
    llm,
    vectorstore,
    document_content_description,
    metadata_field_info,
    enable_limit=True,
    verbose=True,
)
```

```python
# This example only specifies a relevant query
retriever.invoke("What are two movies about dinosaurs")
```

```output
query='dinosaurs' filter=None limit=2
```

```output
[Document(page_content='A bunch of scientists bring back dinosaurs and mayhem breaks loose', metadata={'id': 1183188982475, 'text': 'A bunch of scientists bring back dinosaurs and mayhem breaks loose', 'score': 0.13394928, 'year': {'value': 1993}, 'rating': {'value': 7.7}, 'genre': '"action", "science fiction"'}),
 Document(page_content='Toys come alive and have a blast doing so', metadata={'id': 1183189196391, 'text': 'Toys come alive and have a blast doing so', 'score': 0.1899159, 'year': {'value': 1995}, 'genre': 'animated'})]
```
