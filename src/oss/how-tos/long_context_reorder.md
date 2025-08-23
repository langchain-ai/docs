# How to reorder retrieved results to mitigate the "lost in the middle" effect

Substantial performance degradations in [RAG](/oss/tutorials/rag) applications have been [documented](https://arxiv.org/abs/2307.03172) as the number of retrieved documents grows (e.g., beyond ten). In brief: models are liable to miss relevant information in the middle of long contexts.

By contrast, queries against vector stores will typically return documents in descending order of relevance (e.g., as measured by cosine similarity of [embeddings](/oss/concepts/embedding_models)).

To mitigate the ["lost in the middle"](https://arxiv.org/abs/2307.03172) effect, you can re-order documents after retrieval such that the most relevant documents are positioned at extrema (e.g., the first and last pieces of context), and the least relevant documents are positioned in the middle. In some cases this can help surface the most relevant information to LLMs.

The [LongContextReorder](https://python.langchain.com/api_reference/community/document_transformers/langchain_community.document_transformers.long_context_reorder.LongContextReorder.html) document transformer implements this re-ordering procedure. Below we demonstrate an example.


```python
%pip install -qU langchain langchain-community langchain-openai
```

First we embed some artificial documents and index them in a basic in-memory vector store. We will use [OpenAI](/oss/integrations/providers/openai/) embeddings, but any LangChain vector store or embeddings model will suffice.


```python
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

# Get embeddings.
embeddings = OpenAIEmbeddings()

texts = [
    "Basquetball is a great sport.",
    "Fly me to the moon is one of my favourite songs.",
    "The Celtics are my favourite team.",
    "This is a document about the Boston Celtics",
    "I simply love going to the movies",
    "The Boston Celtics won the game by 20 points",
    "This is just a random text.",
    "Elden Ring is one of the best games in the last 15 years.",
    "L. Kornet is one of the best Celtics players.",
    "Larry Bird was an iconic NBA player.",
]

# Create a retriever
retriever = InMemoryVectorStore.from_texts(texts, embedding=embeddings).as_retriever(
    search_kwargs={"k": 10}
)
query = "What can you tell me about the Celtics?"

# Get relevant documents ordered by relevance score
docs = retriever.invoke(query)
for doc in docs:
    print(f"- {doc.page_content}")
```
```output
- The Celtics are my favourite team.
- This is a document about the Boston Celtics
- The Boston Celtics won the game by 20 points
- L. Kornet is one of the best Celtics players.
- Basquetball is a great sport.
- Larry Bird was an iconic NBA player.
- This is just a random text.
- I simply love going to the movies
- Fly me to the moon is one of my favourite songs.
- Elden Ring is one of the best games in the last 15 years.
```
Note that documents are returned in descending order of relevance to the query. The `LongContextReorder` document transformer will implement the re-ordering described above:


```python
from langchain_community.document_transformers import LongContextReorder

# Reorder the documents:
# Less relevant document will be at the middle of the list and more
# relevant elements at beginning / end.
reordering = LongContextReorder()
reordered_docs = reordering.transform_documents(docs)

# Confirm that the 4 relevant documents are at beginning and end.
for doc in reordered_docs:
    print(f"- {doc.page_content}")
```
```output
- This is a document about the Boston Celtics
- L. Kornet is one of the best Celtics players.
- Larry Bird was an iconic NBA player.
- I simply love going to the movies
- Elden Ring is one of the best games in the last 15 years.
- Fly me to the moon is one of my favourite songs.
- This is just a random text.
- Basquetball is a great sport.
- The Boston Celtics won the game by 20 points
- The Celtics are my favourite team.
```
Below, we show how to incorporate the re-ordered documents into a simple question-answering chain:


```python
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

prompt_template = """
Given these texts:
-----
{context}
-----
Please answer the following question:
{query}
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "query"],
)

# Create and invoke the chain:
chain = create_stuff_documents_chain(llm, prompt)
response = chain.invoke({"context": reordered_docs, "query": query})
print(response)
```
```output
The Boston Celtics are a professional basketball team known for their rich history and success in the NBA. L. Kornet is recognized as one of the best players on the team, and the Celtics recently won a game by 20 points. The Celtics are favored by some fans, as indicated by the statement, "The Celtics are my favourite team." Overall, they have a strong following and are considered a significant part of basketball culture.
```
