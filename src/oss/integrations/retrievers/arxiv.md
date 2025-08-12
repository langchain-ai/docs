---
sidebar_label: Arxiv
---

# ArxivRetriever

>[arXiv](https://arxiv.org/) is an open-access archive for 2 million scholarly articles in the fields of physics, mathematics, computer science, quantitative biology, quantitative finance, statistics, electrical engineering and systems science, and economics.

This notebook shows how to retrieve scientific articles from Arxiv.org into the [Document](https://python.langchain.com/api_reference/core/documents/langchain_core.documents.base.Document.html) format that is used downstream.

For detailed documentation of all `ArxivRetriever` features and configurations head to the [API reference](https://python.langchain.com/api_reference/community/retrievers/langchain_community.retrievers.arxiv.ArxivRetriever.html).

### Integration details

<ItemTable category="external_retrievers" item="ArxivRetriever" />

## Setup

If you want to get automated tracing from individual queries, you can also set your [LangSmith](https://docs.smith.langchain.com/) API key by uncommenting below:


```python
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
# os.environ["LANGSMITH_TRACING"] = "true"
```

### Installation

This retriever lives in the `langchain-community` package. We will also need the [arxiv](https://pypi.org/project/arxiv/) dependency:


```python
%pip install -qU langchain-community arxiv
```

## Instantiation

`ArxivRetriever` parameters include:
- optional `load_max_docs`: default=100. Use it to limit number of downloaded documents. It takes time to download all 100 documents, so use a small number for experiments. There is a hard limit of 300 for now.
- optional `load_all_available_meta`: default=False. By default only the most important fields downloaded: `Published` (date when document was published/last updated), `Title`, `Authors`, `Summary`. If True, other fields also downloaded.
- `get_full_documents`: boolean, default False. Determines whether to fetch full text of documents.

See [API reference](https://python.langchain.com/api_reference/community/retrievers/langchain_community.retrievers.arxiv.ArxivRetriever.html) for more detail.


```python
from langchain_community.retrievers import ArxivRetriever

retriever = ArxivRetriever(
    load_max_docs=2,
    get_ful_documents=True,
)
```

## Usage

`ArxivRetriever` supports retrieval by article identifier:


```python
docs = retriever.invoke("1605.08386")
```


```python
docs[0].metadata  # meta-information of the Document
```



```output
{'Entry ID': 'http://arxiv.org/abs/1605.08386v1',
 'Published': datetime.date(2016, 5, 26),
 'Title': 'Heat-bath random walks with Markov bases',
 'Authors': 'Caprice Stanley, Tobias Windisch'}
```



```python
docs[0].page_content[:400]  # a content of the Document
```



```output
'Graphs on lattice points are studied whose edges come from a finite set of\nallowed moves of arbitrary length. We show that the diameter of these graphs on\nfibers of a fixed integer matrix can be bounded from above by a constant. We\nthen study the mixing behaviour of heat-bath random walks on these graphs. We\nalso state explicit conditions on the set of moves so that the heat-bath random\nwalk, a ge'
```


`ArxivRetriever` also supports retrieval based on natural language text:


```python
docs = retriever.invoke("What is the ImageBind model?")
```


```python
docs[0].metadata
```



```output
{'Entry ID': 'http://arxiv.org/abs/2305.05665v2',
 'Published': datetime.date(2023, 5, 31),
 'Title': 'ImageBind: One Embedding Space To Bind Them All',
 'Authors': 'Rohit Girdhar, Alaaeldin El-Nouby, Zhuang Liu, Mannat Singh, Kalyan Vasudev Alwala, Armand Joulin, Ishan Misra'}
```


## Use within a chain

Like other retrievers, `ArxivRetriever` can be incorporated into LLM applications via [chains](/oss/how-to/sequence/).

We will need a LLM or chat model:

<ChatModelTabs customVarName="llm" />



```python
# | output: false
# | echo: false

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(temperature=0)
```


```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

prompt = ChatPromptTemplate.from_template(
    """Answer the question based only on the context provided.

Context: {context}

Question: {question}"""
)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```


```python
chain.invoke("What is the ImageBind model?")
```



```output
'The ImageBind model is an approach to learn a joint embedding across six different modalities - images, text, audio, depth, thermal, and IMU data. It shows that only image-paired data is sufficient to bind the modalities together and can leverage large scale vision-language models for zero-shot capabilities and emergent applications such as cross-modal retrieval, composing modalities with arithmetic, cross-modal detection and generation.'
```


## API reference

For detailed documentation of all `ArxivRetriever` features and configurations head to the [API reference](https://python.langchain.com/api_reference/community/retrievers/langchain_community.retrievers.arxiv.ArxivRetriever.html).
