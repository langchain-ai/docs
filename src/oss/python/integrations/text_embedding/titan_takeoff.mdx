---
title: Titan Takeoff
---

`TitanML` helps businesses build and deploy better, smaller, cheaper, and faster NLP models through our training, compression, and inference optimization platform.

Our inference server, [Titan Takeoff](https://docs.titanml.co/docs/intro) enables deployment of LLMs locally on your hardware in a single command. Most embedding models are supported out of the box, if you experience trouble with a specific model, please let us know at [hello@titanml.co](mailto:hello@titanml.co).

## Example usage

Here are some helpful examples to get started using Titan Takeoff Server. You need to make sure Takeoff Server has been started in the background before running these commands. For more information see [docs page for launching Takeoff](https://docs.titanml.co/docs/Docs/launching/).

```python
import time

from langchain_community.embeddings import TitanTakeoffEmbed
```

### Example 1

Basic use assuming Takeoff is running on your machine using its default ports (ie localhost:3000).

```python
embed = TitanTakeoffEmbed()
output = embed.embed_query(
    "What is the weather in London in August?", consumer_group="embed"
)
print(output)
```

### Example 2

Starting readers using TitanTakeoffEmbed Python Wrapper. If you haven't created any readers with first launching Takeoff, or you want to add another you can do so when you initialize the TitanTakeoffEmbed object. Just pass a list of models you want to start as the `models` parameter.

You can use `embed.query_documents` to embed multiple documents at once. The expected input is a list of strings, rather than just a string expected for the `embed_query` method.

```python
# Model config for the embedding model, where you can specify the following parameters:
#   model_name (str): The name of the model to use
#   device: (str): The device to use for inference, cuda or cpu
#   consumer_group (str): The consumer group to place the reader into
embedding_model = {
    "model_name": "BAAI/bge-large-en-v1.5",
    "device": "cpu",
    "consumer_group": "embed",
}
embed = TitanTakeoffEmbed(models=[embedding_model])

# The model needs time to spin up, length of time need will depend on the size of model and your network connection speed
time.sleep(60)

prompt = "What is the capital of France?"
# We specified "embed" consumer group so need to send request to the same consumer group so it hits our embedding model and not others
output = embed.embed_query(prompt, consumer_group="embed")
print(output)
```
