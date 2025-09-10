---
title: SageMaker
---

Let's load the `SageMaker Endpoints Embeddings` class. The class can be used if you host, e.g. your own Hugging Face model on SageMaker.

For instructions on how to do this, please see [here](https://www.philschmid.de/custom-inference-huggingface-sagemaker).

**Note**: In order to handle batched requests, you will need to adjust the return line in the `predict_fn()` function within the custom `inference.py` script:

Change from

`return {"vectors": sentence_embeddings[0].tolist()}`

to:

`return {"vectors": sentence_embeddings.tolist()}`.

```python
!pip3 install langchain boto3
```

```python
import json
from typing import Dict, List

from langchain_community.embeddings import SagemakerEndpointEmbeddings
from langchain_community.embeddings.sagemaker_endpoint import EmbeddingsContentHandler


class ContentHandler(EmbeddingsContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, inputs: list[str], model_kwargs: Dict) -> bytes:
        """
        Transforms the input into bytes that can be consumed by SageMaker endpoint.
        Args:
            inputs: List of input strings.
            model_kwargs: Additional keyword arguments to be passed to the endpoint.
        Returns:
            The transformed bytes input.
        """
        # Example: inference.py expects a JSON string with a "inputs" key:
        input_str = json.dumps({"inputs": inputs, **model_kwargs})
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> List[List[float]]:
        """
        Transforms the bytes output from the endpoint into a list of embeddings.
        Args:
            output: The bytes output from SageMaker endpoint.
        Returns:
            The transformed output - list of embeddings
        Note:
            The length of the outer list is the number of input strings.
            The length of the inner lists is the embedding dimension.
        """
        # Example: inference.py returns a JSON string with the list of
        # embeddings in a "vectors" key:
        response_json = json.loads(output.read().decode("utf-8"))
        return response_json["vectors"]


content_handler = ContentHandler()


embeddings = SagemakerEndpointEmbeddings(
    # credentials_profile_name="credentials-profile-name",
    endpoint_name="huggingface-pytorch-inference-2023-03-21-16-14-03-834",
    region_name="us-east-1",
    content_handler=content_handler,
)


# client = boto3.client(
#     "sagemaker-runtime",
#     region_name="us-west-2"
# )
# embeddings = SagemakerEndpointEmbeddings(
#     endpoint_name="huggingface-pytorch-inference-2023-03-21-16-14-03-834",
#     client=client
#     content_handler=content_handler,
# )
```

```python
query_result = embeddings.embed_query("foo")
```

```python
doc_results = embeddings.embed_documents(["foo"])
```

```python
doc_results
```

```python

```
