---
sidebar_position: 7
---

# How to deal with high-cardinality categoricals when doing query analysis

You may want to do query analysis to create a filter on a categorical column. One of the difficulties here is that you usually need to specify the EXACT categorical value. The issue is you need to make sure the LLM generates that categorical value exactly. This can be done relatively easy with prompting when there are only a few values that are valid. When there are a high number of valid values then it becomes more difficult, as those values may not fit in the LLM context, or (if they do) there may be too many for the LLM to properly attend to.

In this notebook we take a look at how to approach this.

## Setup
#### Install dependencies


```python
%pip install -qU langchain langchain-community langchain-openai faker langchain-chroma
```
```output
Note: you may need to restart the kernel to use updated packages.
```
#### Set environment variables

We'll use OpenAI in this example:


```python
import getpass
import os

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass()

# Optional, uncomment to trace runs with LangSmith. Sign up here: https://smith.langchain.com.
# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass()
```

#### Set up data

We will generate a bunch of fake names


```python
from faker import Faker

fake = Faker()

names = [fake.name() for _ in range(10000)]
```

Let's look at some of the names


```python
names[0]
```



```output
'Jacob Adams'
```



```python
names[567]
```



```output
'Eric Acevedo'
```


## Query Analysis

We can now set up a baseline query analysis


```python
from pydantic import BaseModel, Field, model_validator
```


```python
class Search(BaseModel):
    query: str
    author: str
```


```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

system = """Generate a relevant search query for a library system"""
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
structured_llm = llm.with_structured_output(Search)
query_analyzer = {"question": RunnablePassthrough()} | prompt | structured_llm
```

We can see that if we spell the name exactly correctly, it knows how to handle it


```python
query_analyzer.invoke("what are books about aliens by Jesse Knight")
```



```output
Search(query='aliens', author='Jesse Knight')
```


The issue is that the values you want to filter on may NOT be spelled exactly correctly


```python
query_analyzer.invoke("what are books about aliens by jess knight")
```



```output
Search(query='aliens', author='Jess Knight')
```


### Add in all values

One way around this is to add ALL possible values to the prompt. That will generally guide the query in the right direction


```python
system = """Generate a relevant search query for a library system.

`author` attribute MUST be one of:

{authors}

Do NOT hallucinate author name!"""
base_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)
prompt = base_prompt.partial(authors=", ".join(names))
```


```python
query_analyzer_all = {"question": RunnablePassthrough()} | prompt | structured_llm
```

However... if the list of categoricals is long enough, it may error!


```python
try:
    res = query_analyzer_all.invoke("what are books about aliens by jess knight")
except Exception as e:
    print(e)
```

We can try to use a longer context window... but with so much information in there, it is not garunteed to pick it up reliably


```python
llm_long = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)
structured_llm_long = llm_long.with_structured_output(Search)
query_analyzer_all = {"question": RunnablePassthrough()} | prompt | structured_llm_long
```


```python
query_analyzer_all.invoke("what are books about aliens by jess knight")
```



```output
Search(query='aliens', author='jess knight')
```


### Find and all relevant values

Instead, what we can do is create an index over the relevant values and then query that for the N most relevant values,


```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_texts(names, embeddings, collection_name="author_names")
```


```python
def select_names(question):
    _docs = vectorstore.similarity_search(question, k=10)
    _names = [d.page_content for d in _docs]
    return ", ".join(_names)
```


```python
create_prompt = {
    "question": RunnablePassthrough(),
    "authors": select_names,
} | base_prompt
```


```python
query_analyzer_select = create_prompt | structured_llm
```


```python
create_prompt.invoke("what are books by jess knight")
```



```output
ChatPromptValue(messages=[SystemMessage(content='Generate a relevant search query for a library system.\n\n`author` attribute MUST be one of:\n\nJennifer Knight, Jill Knight, John Knight, Dr. Jeffrey Knight, Christopher Knight, Andrea Knight, Brandy Knight, Jennifer Keller, Becky Chambers, Sarah Knapp\n\nDo NOT hallucinate author name!'), HumanMessage(content='what are books by jess knight')])
```



```python
query_analyzer_select.invoke("what are books about aliens by jess knight")
```



```output
Search(query='books about aliens', author='Jennifer Knight')
```


### Replace after selection

Another method is to let the LLM fill in whatever value, but then convert that value to a valid value.
This can actually be done with the Pydantic class itself!


```python
class Search(BaseModel):
    query: str
    author: str

    @model_validator(mode="before")
    @classmethod
    def double(cls, values: dict) -> dict:
        author = values["author"]
        closest_valid_author = vectorstore.similarity_search(author, k=1)[
            0
        ].page_content
        values["author"] = closest_valid_author
        return values
```


```python
system = """Generate a relevant search query for a library system"""
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)
corrective_structure_llm = llm.with_structured_output(Search)
corrective_query_analyzer = (
    {"question": RunnablePassthrough()} | prompt | corrective_structure_llm
)
```


```python
corrective_query_analyzer.invoke("what are books about aliens by jes knight")
```



```output
Search(query='aliens', author='John Knight')
```



```python
# TODO: show trigram similarity
```
