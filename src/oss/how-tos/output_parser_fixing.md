# How to use the output-fixing parser

This [output parser](/oss/concepts/output_parsers/) wraps another output parser, and in the event that the first one fails it calls out to another LLM to fix any errors.

But we can do other things besides throw errors. Specifically, we can pass the misformatted output, along with the formatted instructions, to the model and ask it to fix it.

For this example, we'll use the above Pydantic output parser. Here's what happens if we pass it a result that does not comply with the schema:


```python
from typing import List

from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
```


```python
class Actor(BaseModel):
    name: str = Field(description="name of an actor")
    film_names: List[str] = Field(description="list of names of films they starred in")


actor_query = "Generate the filmography for a random actor."

parser = PydanticOutputParser(pydantic_object=Actor)
```


```python
misformatted = "{'name': 'Tom Hanks', 'film_names': ['Forrest Gump']}"
```


```python
try:
    parser.parse(misformatted)
except OutputParserException as e:
    print(e)
```
```output
Invalid json output: {'name': 'Tom Hanks', 'film_names': ['Forrest Gump']}
For troubleshooting, visit: https://python.langchain.com/docs/troubleshooting/errors/OUTPUT_PARSING_FAILURE
```
Now we can construct and use a `OutputFixingParser`. This output parser takes as an argument another output parser but also an LLM with which to try to correct any formatting mistakes.


```python
from langchain.output_parsers import OutputFixingParser

new_parser = OutputFixingParser.from_llm(parser=parser, llm=ChatOpenAI())
```


```python
new_parser.parse(misformatted)
```



```output
Actor(name='Tom Hanks', film_names=['Forrest Gump'])
```


Find out api documentation for [OutputFixingParser](https://python.langchain.com/api_reference/langchain/output_parsers/langchain.output_parsers.fix.OutputFixingParser.html#langchain.output_parsers.fix.OutputFixingParser).


```python

```
