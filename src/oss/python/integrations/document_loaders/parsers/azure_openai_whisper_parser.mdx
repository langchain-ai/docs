---
title: Azure OpenAI Whisper Parser
---

>[Azure OpenAI Whisper Parser](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/whisper-overview) is a wrapper around the Azure OpenAI Whisper API which utilizes machine learning to transcribe audio files to english text.
>
>The Parser supports `.mp3`, `.mp4`, `.mpeg`, `.mpga`, `.m4a`, `.wav`, and `.webm`.

The current implementation follows LangChain core principles and can be used with other loaders to handle both audio downloading and parsing. As a result of this the parser will `yield` an `Iterator[Document]`.

## Prerequisites

The service requires Azure credentials, Azure endpoint and Whisper Model deployment, which can be set up by following the guide [here](https://learn.microsoft.com/en-us/azure/ai-services/openai/whisper-quickstart?tabs=command-line%2Cpython-new%2Cjavascript&pivots=programming-language-python). Furthermore, the required dependencies must be installed.

```python
%pip install -Uq  langchain langchain-community openai
```

## Example 1

The `AzureOpenAIWhisperParser`'s method, `.lazy_parse`, accepts a `Blob` object as a parameter containing the file path of the file to be transcribed.

```python
from langchain_core.documents.base import Blob

audio_path = "path/to/your/audio/file"
audio_blob = Blob(path=audio_path)
```

```python
from langchain_community.document_loaders.parsers.audio import AzureOpenAIWhisperParser

endpoint = "<your_endpoint>"
key = "<your_api_key"
version = "<your_api_version>"
name = "<your_deployment_name>"

parser = AzureOpenAIWhisperParser(
    api_key=key, azure_endpoint=endpoint, api_version=version, deployment_name=name
)
```

```python
documents = parser.lazy_parse(blob=audio_blob)
```

```python
for doc in documents:
    print(doc.page_content)
```

## Example 2

The `AzureOpenAIWhisperParser` can also be used in conjunction with audio loaders, like the `YoutubeAudioLoader` with a `GenericLoader`.

```python
from langchain_community.document_loaders.blob_loaders.youtube_audio import (
    YoutubeAudioLoader,
)
from langchain_community.document_loaders.generic import GenericLoader
```

```python
# Must be a list
url = ["www.youtube.url.com"]

save_dir = "save/directory/"
```

```python
name = "<your_deployment_name>"

loader = GenericLoader(
    YoutubeAudioLoader(url, save_dir), AzureOpenAIWhisperParser(deployment_name=name)
)

docs = loader.load()
```

```python
for doc in documents:
    print(doc.page_content)
```
