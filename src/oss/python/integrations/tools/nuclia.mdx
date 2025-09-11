---
title: Nuclia Understanding
---

>[Nuclia](https://nuclia.com) automatically indexes your unstructured data from any internal and external source, providing optimized search results and generative answers. It can handle video and audio transcription, image content extraction, and document parsing.

The `Nuclia Understanding API` supports the processing of unstructured data, including text, web pages, documents, and audio/video contents. It extracts all texts wherever it is (using speech-to-text or OCR when needed), it identifies entities, it also extracts metadata, embedded files (like images in a PDF), and web links. It also provides a summary of the content.

To use the `Nuclia Understanding API`, you need to have a `Nuclia` account. You can create one for free at [https://nuclia.cloud](https://nuclia.cloud), and then [create a NUA key](https://docs.nuclia.dev/docs/docs/using/understanding/intro).

```python
%pip install -qU  protobuf
%pip install -qU  nucliadb-protos
```

```python
import os

os.environ["NUCLIA_ZONE"] = "<YOUR_ZONE>"  # e.g. europe-1
os.environ["NUCLIA_NUA_KEY"] = "<YOUR_API_KEY>"
```

```python
from langchain_community.tools.nuclia import NucliaUnderstandingAPI

nua = NucliaUnderstandingAPI(enable_ml=False)
```

You can push files to the Nuclia Understanding API using the `push` action. As the processing is done asynchronously, the results might be returned in a different order than the files were pushed. That is why you need to provide an `id` to match the results with the corresponding file.

```python
nua.run({"action": "push", "id": "1", "path": "./report.docx"})
nua.run({"action": "push", "id": "2", "path": "./interview.mp4"})
```

You can now call the `pull` action in a loop until you get the JSON-formatted result.

```python
import time

pending = True
data = None
while pending:
    time.sleep(15)
    data = nua.run({"action": "pull", "id": "1", "path": None})
    if data:
        print(data)
        pending = False
    else:
        print("waiting...")
```

You can also do it in one step in `async` mode, you only need to do a push, and it will wait until the results are pulled:

```python
import asyncio


async def process():
    data = await nua.arun(
        {"action": "push", "id": "1", "path": "./talk.mp4", "text": None}
    )
    print(data)


asyncio.run(process())
```

## Retrieved information

Nuclia returns the following information:

- file metadata
- extracted text
- nested text (like text in an embedded image)
- a summary (only when `enable_ml` is set to `True`)
- paragraphs and sentences splitting (defined by the position of their first and last characters, plus start time and end time for a video or audio file)
- named entities: people, dates, places, organizations, etc. (only when `enable_ml` is set to `True`)
- links
- a thumbnail
- embedded files
- the vector representations of the text (only when `enable_ml` is set to `True`)

Note:

  Generated files (thumbnail, extracted embedded files, etc.) are provided as a token. You can download them with the [`/processing/download` endpoint](https://docs.nuclia.dev/docs/api#operation/Download_binary_file_processing_download_get).

  Also at any level, if an attribute exceeds a certain size, it will be put in a downloadable file and will be replaced in the document by a file pointer. This will consist of `{"file": {"uri": "JWT_TOKEN"}}`. The rule is that if the size of the message is greater than 1000000 characters, the biggest parts will be moved to downloadable files. First, the compression process will target vectors. If that is not enough, it will target large field metadata, and finally it will target extracted text.
