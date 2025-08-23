# How to load web pages

This guide covers how to [load](/oss/concepts/document_loaders/) web pages into the LangChain [Document](https://python.langchain.com/api_reference/core/documents/langchain_core.documents.base.Document.html) format that we use downstream. Web pages contain text, images, and other multimedia elements, and are typically represented with HTML. They may include links to other pages or resources.

LangChain integrates with a host of parsers that are appropriate for web pages. The right parser will depend on your needs. Below we demonstrate two possibilities:

- [Simple and fast](/oss/how-to/document_loader_web#simple-and-fast-text-extraction) parsing, in which we recover one `Document` per web page with its content represented as a "flattened" string;
- [Advanced](/oss/how-to/document_loader_web#advanced-parsing) parsing, in which we recover multiple `Document` objects per page, allowing one to identify and traverse sections, links, tables, and other structures.

## Setup

For the "simple and fast" parsing, we will need `langchain-community` and the `beautifulsoup4` library:


```python
%pip install -qU langchain-community beautifulsoup4
```

For advanced parsing, we will use `langchain-unstructured`:


```python
%pip install -qU langchain-unstructured
```

## Simple and fast text extraction

If you are looking for a simple string representation of text that is embedded in a web page, the method below is appropriate. It will return a list of `Document` objects -- one per page -- containing a single string of the page's text. Under the hood it uses the `beautifulsoup4` Python library.

LangChain document loaders implement `lazy_load` and its async variant, `alazy_load`, which return iterators of `Document objects`. We will use these below.


```python
import bs4
from langchain_community.document_loaders import WebBaseLoader

page_url = "https://python.langchain.com/docs/how_to/chatbots_memory/"

loader = WebBaseLoader(web_paths=[page_url])
docs = []
async for doc in loader.alazy_load():
    docs.append(doc)

assert len(docs) == 1
doc = docs[0]
```
```output
USER_AGENT environment variable not set, consider setting it to identify your requests.
```

```python
print(f"{doc.metadata}\n")
print(doc.page_content[:500].strip())
```
```output
{'source': 'https://python.langchain.com/docs/how_to/chatbots_memory/', 'title': 'How to add memory to chatbots | \uf8ffü¶úÔ∏è\uf8ffüîó LangChain', 'description': 'A key feature of chatbots is their ability to use content of previous conversation turns as context. This state management can take several forms, including:', 'language': 'en'}

How to add memory to chatbots | ü¶úÔ∏èüîó LangChain







Skip to main contentShare your thoughts on AI agents. Take the 3-min survey.IntegrationsAPI ReferenceMoreContributingPeopleLangSmithLangGraphLangChain HubLangChain JS/TSv0.3v0.3v0.2v0.1üí¨SearchIntroductionTutorialsBuild a Question Answering application over a Graph DatabaseTutorialsBuild a Simple LLM Application with LCELBuild a Query Analysis SystemBuild a ChatbotConversational RAGBuild an Extraction ChainBuild an AgentTaggingd
```
This is essentially a dump of the text from the page's HTML. It may contain extraneous information like headings and navigation bars. If you are familiar with the expected HTML, you can specify desired `<div>` classes and other parameters via BeautifulSoup. Below we parse only the body text of the article:


```python
loader = WebBaseLoader(
    web_paths=[page_url],
    bs_kwargs={
        "parse_only": bs4.SoupStrainer(class_="theme-doc-markdown markdown"),
    },
    bs_get_text_kwargs={"separator": " | ", "strip": True},
)

docs = []
async for doc in loader.alazy_load():
    docs.append(doc)

assert len(docs) == 1
doc = docs[0]
```


```python
print(f"{doc.metadata}\n")
print(doc.page_content[:500])
```
```output
{'source': 'https://python.langchain.com/docs/how_to/chatbots_memory/'}

How to add memory to chatbots | A key feature of chatbots is their ability to use content of previous conversation turns as context. This state management can take several forms, including: | Simply stuffing previous messages into a chat model prompt. | The above, but trimming old messages to reduce the amount of distracting information the model has to deal with. | More complex modifications like synthesizing summaries for long running conversations. | We'll go into more detail on a few techniq
```

```python
print(doc.page_content[-500:])
```
```output
a greeting. Nemo then asks the AI how it is doing, and the AI responds that it is fine.'), | HumanMessage(content='What did I say my name was?'), | AIMessage(content='You introduced yourself as Nemo. How can I assist you today, Nemo?')] | Note that invoking the chain again will generate another summary generated from the initial summary plus new messages and so on. You could also design a hybrid approach where a certain number of messages are retained in chat history while others are summarized.
```
Note that this required advance technical knowledge of how the body text is represented in the underlying HTML.

We can parameterize `WebBaseLoader` with a variety of settings, allowing for specification of request headers, rate limits, and parsers and other kwargs for BeautifulSoup. See its [API reference](https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.web_base.WebBaseLoader.html) for detail.

## Advanced parsing

This method is appropriate if we want more granular control or processing of the page content. Below, instead of generating one `Document` per page and controlling its content via BeautifulSoup, we generate multiple `Document` objects representing distinct structures on a page. These structures can include section titles and their corresponding body texts, lists or enumerations, tables, and more.

Under the hood it uses the `langchain-unstructured` library. See the [integration docs](/oss/integrations/document_loaders/unstructured_file/) for more information about using [Unstructured](https://docs.unstructured.io/welcome) with LangChain.


```python
from langchain_unstructured import UnstructuredLoader

page_url = "https://python.langchain.com/docs/how_to/chatbots_memory/"
loader = UnstructuredLoader(web_url=page_url)

docs = []
async for doc in loader.alazy_load():
    docs.append(doc)
```
```output
INFO: Note: NumExpr detected 12 cores but "NUMEXPR_MAX_THREADS" not set, so enforcing safe limit of 8.
INFO: NumExpr defaulting to 8 threads.
```
Note that with no advance knowledge of the page HTML structure, we recover a natural organization of the body text:


```python
for doc in docs[:5]:
    print(doc.page_content)
```
```output
How to add memory to chatbots
A key feature of chatbots is their ability to use content of previous conversation turns as context. This state management can take several forms, including:
Simply stuffing previous messages into a chat model prompt.
The above, but trimming old messages to reduce the amount of distracting information the model has to deal with.
More complex modifications like synthesizing summaries for long running conversations.
ERROR! Session/line number was not unique in database. History logging moved to new session 2747
```
### Extracting content from specific sections

Each `Document` object represents an element of the page. Its metadata contains useful information, such as its category:


```python
for doc in docs[:5]:
    print(f"{doc.metadata['category']}: {doc.page_content}")
```
```output
Title: How to add memory to chatbots
NarrativeText: A key feature of chatbots is their ability to use content of previous conversation turns as context. This state management can take several forms, including:
ListItem: Simply stuffing previous messages into a chat model prompt.
ListItem: The above, but trimming old messages to reduce the amount of distracting information the model has to deal with.
ListItem: More complex modifications like synthesizing summaries for long running conversations.
```
Elements may also have parent-child relationships -- for example, a paragraph might belong to a section with a title. If a section is of particular interest (e.g., for indexing) we can isolate the corresponding `Document` objects.

As an example, below we load the content of the "Setup" sections for two web pages:


```python
from typing import List

from langchain_core.documents import Document


async def _get_setup_docs_from_url(url: str) -> List[Document]:
    loader = UnstructuredLoader(web_url=url)

    setup_docs = []
    parent_id = -1
    async for doc in loader.alazy_load():
        if doc.metadata["category"] == "Title" and doc.page_content.startswith("Setup"):
            parent_id = doc.metadata["element_id"]
        if doc.metadata.get("parent_id") == parent_id:
            setup_docs.append(doc)

    return setup_docs


page_urls = [
    "https://python.langchain.com/docs/how_to/chatbots_memory/",
    "https://python.langchain.com/docs/how_to/chatbots_tools/",
]
setup_docs = []
for url in page_urls:
    page_setup_docs = await _get_setup_docs_from_url(url)
    setup_docs.extend(page_setup_docs)
```


```python
from collections import defaultdict

setup_text = defaultdict(str)

for doc in setup_docs:
    url = doc.metadata["url"]
    setup_text[url] += f"{doc.page_content}\n"

dict(setup_text)
```



```output
{'https://python.langchain.com/docs/how_to/chatbots_memory/': "You'll need to install a few packages, and have your OpenAI API key set as an environment variable named OPENAI_API_KEY:\n%pip install --upgrade --quiet langchain langchain-openai\n\n# Set env var OPENAI_API_KEY or load from a .env file:\nimport dotenv\n\ndotenv.load_dotenv()\n[33mWARNING: You are using pip version 22.0.4; however, version 23.3.2 is available.\nYou should consider upgrading via the '/Users/jacoblee/.pyenv/versions/3.10.5/bin/python -m pip install --upgrade pip' command.[0m[33m\n[0mNote: you may need to restart the kernel to use updated packages.\n",
 'https://python.langchain.com/docs/how_to/chatbots_tools/': "For this guide, we'll be using a tool calling agent with a single tool for searching the web. The default will be powered by Tavily, but you can switch it out for any similar tool. The rest of this section will assume you're using Tavily.\nYou'll need to sign up for an account on the Tavily website, and install the following packages:\n%pip install --upgrade --quiet langchain-community langchain-openai tavily-python\n\n# Set env var OPENAI_API_KEY or load from a .env file:\nimport dotenv\n\ndotenv.load_dotenv()\nYou will also need your OpenAI key set as OPENAI_API_KEY and your Tavily API key set as TAVILY_API_KEY.\n"}
```


### Vector search over page content

Once we have loaded the page contents into LangChain `Document` objects, we can index them (e.g., for a RAG application) in the usual way. Below we use OpenAI [embeddings](/oss/concepts/embedding_models), although any LangChain embeddings model will suffice.


```python
%pip install -qU langchain-openai
```


```python
import getpass
import os

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")
```


```python
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

vector_store = InMemoryVectorStore.from_documents(setup_docs, OpenAIEmbeddings())
retrieved_docs = vector_store.similarity_search("Install Tavily", k=2)
for doc in retrieved_docs:
    print(f"Page {doc.metadata['url']}: {doc.page_content[:300]}\n")
```
```output
INFO: HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO: HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
``````output
Page https://python.langchain.com/docs/how_to/chatbots_tools/: You'll need to sign up for an account on the Tavily website, and install the following packages:

Page https://python.langchain.com/docs/how_to/chatbots_tools/: For this guide, we'll be using a tool calling agent with a single tool for searching the web. The default will be powered by Tavily, but you can switch it out for any similar tool. The rest of this section will assume you're using Tavily.
```
## Other web page loaders

For a list of available LangChain web page loaders, please see [this table](/oss/integrations/document_loaders/#webpages).
