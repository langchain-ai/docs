---
title: Galaxia
---

Galaxia is GraphRAG solution, which automates document processing, knowledge base (Graph Language Model) creation and retrieval:
[galaxia-rag](https://smabbler.gitbook.io/smabbler/api-rag/smabblers-api-rag)

To use Galaxia first upload your texts and create a Graph Language Model here: [smabbler-cloud](https://beta.cloud.smabbler.com)

After the model is built and activated, you will be able to use this integration to retrieve what you need.

The module repository is located here: [github](https://github.com/rrozanski-smabbler/galaxia-langchain)

### Integration details

| Retriever | Self-host | Cloud offering | Package |
| :--- | :--- | :---: | :---: |
[Galaxia Retriever](https://github.com/rrozanski-smabbler/galaxia-langchain) | ❌ | ✅ | __langchain-galaxia-retriever__ |

## Setup

Before you can retrieve anything you need to create your Graph Language Model here: [smabbler-cloud](https://beta.cloud.smabbler.com)

following these 3 simple steps: [rag-instruction](https://smabbler.gitbook.io/smabbler/api-rag/build-rag-model-in-3-steps)

Don't forget to activate the model after building it!

### Installation

The retriever is implemented in the following package: [pypi](https://pypi.org/project/langchain-galaxia-retriever/)

```python
%pip install -qU langchain-galaxia-retriever
```

## Instantiation

```python
from langchain_galaxia_retriever.retriever import GalaxiaRetriever

gr = GalaxiaRetriever(
    api_url="beta.api.smabbler.com",
    api_key="<key>",  # you can find it here: https://beta.cloud.smabbler.com/user/account
    knowledge_base_id="<knowledge_base_id>",  # you can find it in https://beta.cloud.smabbler.com , in the model table
    n_retries=10,
    wait_time=5,
)
```

## Usage

```python
result = gr.invoke("<test question>")
print(result)
```

## Use within a chain

```python
# | output: false
# | echo: false

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
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
    {"context": gr | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

```python
chain.invoke("<test question>")
```

## API reference

For more information about Galaxia Retriever check its implementation on github [github](https://github.com/rrozanski-smabbler/galaxia-langchain)
