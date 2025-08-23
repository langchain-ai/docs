# How to use multimodal prompts

Here we demonstrate how to use prompt templates to format [multimodal](/oss/concepts/multimodality/) inputs to models. 

To use prompt templates in the context of multimodal data, we can templatize elements of the corresponding content block.
For example, below we define a prompt that takes a URL for an image as a parameter:


```python
from langchain_core.prompts import ChatPromptTemplate

# Define prompt
prompt = ChatPromptTemplate(
    [
        {
            "role": "system",
            "content": "Describe the image provided.",
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source_type": "url",
                    # highlight-next-line
                    "url": "{image_url}",
                },
            ],
        },
    ]
)
```

Let's use this prompt to pass an image to a [chat model](/oss/concepts/chat_models/#multimodality):


```python
from langchain.chat_models import init_chat_model

llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")

url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"

chain = prompt | llm
response = chain.invoke({"image_url": url})
print(response.text())
```
```output
This image shows a beautiful wooden boardwalk cutting through a lush green wetland or marsh area. The boardwalk extends straight ahead toward the horizon, creating a strong leading line through the composition. On either side, tall green grasses sway in what appears to be a summer or late spring setting. The sky is particularly striking, with wispy cirrus clouds streaking across a vibrant blue background. In the distance, you can see a tree line bordering the wetland area. The lighting suggests this may be during "golden hour" - either early morning or late afternoon - as there's a warm, gentle quality to the light that's illuminating the scene. The wooden planks of the boardwalk appear well-maintained and provide safe passage through what would otherwise be difficult terrain to traverse. It's the kind of scene you might find in a nature preserve or wildlife refuge designed to give visitors access to observe wetland ecosystems while protecting the natural environment.
```
Note that we can templatize arbitrary elements of the content block:


```python
prompt = ChatPromptTemplate(
    [
        {
            "role": "system",
            "content": "Describe the image provided.",
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source_type": "base64",
                    "mime_type": "{image_mime_type}",
                    "data": "{image_data}",
                    "cache_control": {"type": "{cache_type}"},
                },
            ],
        },
    ]
)
```


```python
import base64

import httpx

image_data = base64.b64encode(httpx.get(url).content).decode("utf-8")

chain = prompt | llm
response = chain.invoke(
    {
        "image_data": image_data,
        "image_mime_type": "image/jpeg",
        "cache_type": "ephemeral",
    }
)
print(response.text())
```
```output
This image shows a beautiful wooden boardwalk cutting through a lush green marsh or wetland area. The boardwalk extends straight ahead toward the horizon, creating a strong leading line in the composition. The surrounding vegetation consists of tall grass and reeds in vibrant green hues, with some bushes and trees visible in the background. The sky is particularly striking, featuring a bright blue color with wispy white clouds streaked across it. The lighting suggests this photo was taken during the "golden hour" - either early morning or late afternoon - giving the scene a warm, peaceful quality. The raised wooden path provides accessible access through what would otherwise be difficult terrain to traverse, allowing visitors to experience and appreciate this natural environment.
```

```python

```
