---
title: Titan Takeoff
---

`TitanML` helps businesses build and deploy better, smaller, cheaper, and faster NLP models through our training, compression, and inference optimization platform.

Our inference server, [Titan Takeoff](https://docs.titanml.co/docs/intro) enables deployment of LLMs locally on your hardware in a single command. Most generative model architectures are supported, such as Falcon, Llama 2, GPT2, T5 and many more. If you experience trouble with a specific model, please let us know at [hello@titanml.co](mailto:hello@titanml.co).

## Example usage

Here are some helpful examples to get started using Titan Takeoff Server. You need to make sure Takeoff Server has been started in the background before running these commands. For more information see [docs page for launching Takeoff](https://docs.titanml.co/docs/Docs/launching/).

```python
import time

# Note importing TitanTakeoffPro instead of TitanTakeoff will work as well both use same object under the hood
from langchain_community.llms import TitanTakeoff
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate
```

### Example 1

Basic use assuming Takeoff is running on your machine using its default ports (ie localhost:3000).

```python
llm = TitanTakeoff()
output = llm.invoke("What is the weather in London in August?")
print(output)
```

### Example 2

Specifying a port and other generation parameters

```python
llm = TitanTakeoff(port=3000)
# A comprehensive list of parameters can be found at https://docs.titanml.co/docs/next/apis/Takeoff%20inference_REST_API/generate#request
output = llm.invoke(
    "What is the largest rainforest in the world?",
    consumer_group="primary",
    min_new_tokens=128,
    max_new_tokens=512,
    no_repeat_ngram_size=2,
    sampling_topk=1,
    sampling_topp=1.0,
    sampling_temperature=1.0,
    repetition_penalty=1.0,
    regex_string="",
    json_schema=None,
)
print(output)
```

### Example 3

Using generate for multiple inputs

```python
llm = TitanTakeoff()
rich_output = llm.generate(["What is Deep Learning?", "What is Machine Learning?"])
print(rich_output.generations)
```

### Example 4

Streaming output

```python
llm = TitanTakeoff(
    streaming=True, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)
prompt = "What is the capital of France?"
output = llm.invoke(prompt)
print(output)
```

### Example 5

Using LCEL

```python
llm = TitanTakeoff()
prompt = PromptTemplate.from_template("Tell me about {topic}")
chain = prompt | llm
output = chain.invoke({"topic": "the universe"})
print(output)
```

### Example 6

Starting readers using TitanTakeoff Python Wrapper. If you haven't created any readers with first launching Takeoff, or you want to add another you can do so when you initialize the TitanTakeoff object. Just pass a list of model configs you want to start as the `models` parameter.

```python
# Model config for the llama model, where you can specify the following parameters:
#   model_name (str): The name of the model to use
#   device: (str): The device to use for inference, cuda or cpu
#   consumer_group (str): The consumer group to place the reader into
#   tensor_parallel (Optional[int]): The number of gpus you would like your model to be split across
#   max_seq_length (int): The maximum sequence length to use for inference, defaults to 512
#   max_batch_size (int_: The max batch size for continuous batching of requests
llama_model = {
    "model_name": "TheBloke/Llama-2-7b-Chat-AWQ",
    "device": "cuda",
    "consumer_group": "llama",
}
llm = TitanTakeoff(models=[llama_model])

# The model needs time to spin up, length of time need will depend on the size of model and your network connection speed
time.sleep(60)

prompt = "What is the capital of France?"
output = llm.invoke(prompt, consumer_group="llama")
print(output)
```
