# How to inspect runnables

<Info>
**Prerequisites**


This guide assumes familiarity with the following concepts:
- [LangChain Expression Language (LCEL)](/oss/concepts/lcel)
- [Chaining runnables](/oss/how-to/sequence/)

</Info>

Once you create a runnable with [LangChain Expression Language](/oss/concepts/lcel), you may often want to inspect it to get a better sense for what is going on. This notebook covers some methods for doing so.

This guide shows some ways you can programmatically introspect the internal steps of chains. If you are instead interested in debugging issues in your chain, see [this section](/oss/how-to/debugging) instead.

First, let's create an example chain. We will create one that does retrieval:


```python
%pip install -qU langchain langchain-openai faiss-cpu tiktoken
```


```python
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

vectorstore = FAISS.from_texts(
    ["harrison worked at kensho"], embedding=OpenAIEmbeddings()
)
retriever = vectorstore.as_retriever()

template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

model = ChatOpenAI()

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)
```

## Get a graph

You can use the `get_graph()` method to get a graph representation of the runnable:


```python
chain.get_graph()
```

## Print a graph

While that is not super legible, you can use the `print_ascii()` method to show that graph in a way that's easier to understand:


```python
chain.get_graph().print_ascii()
```
```output
           +---------------------------------+         
           | Parallel<context,question>Input |         
           +---------------------------------+         
                    **               **                
                 ***                   ***             
               **                         **           
+----------------------+              +-------------+  
| VectorStoreRetriever |              | Passthrough |  
+----------------------+              +-------------+  
                    **               **                
                      ***         ***                  
                         **     **                     
           +----------------------------------+        
           | Parallel<context,question>Output |        
           +----------------------------------+        
                             *                         
                             *                         
                             *                         
                  +--------------------+               
                  | ChatPromptTemplate |               
                  +--------------------+               
                             *                         
                             *                         
                             *                         
                      +------------+                   
                      | ChatOpenAI |                   
                      +------------+                   
                             *                         
                             *                         
                             *                         
                   +-----------------+                 
                   | StrOutputParser |                 
                   +-----------------+                 
                             *                         
                             *                         
                             *                         
                +-----------------------+              
                | StrOutputParserOutput |              
                +-----------------------+
```
## Get the prompts

You may want to see just the prompts that are used in a chain with the `get_prompts()` method:


```python
chain.get_prompts()
```



```output
[ChatPromptTemplate(input_variables=['context', 'question'], messages=[HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['context', 'question'], template='Answer the question based only on the following context:\n{context}\n\nQuestion: {question}\n'))])]
```


## Next steps

You've now learned how to introspect your composed LCEL chains.

Next, check out the other how-to guides on runnables in this section, or the related how-to guide on [debugging your chains](/oss/how-to/debugging).


```python

```
