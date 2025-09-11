---
title: Dropbox
---

[Dropbox](https://en.wikipedia.org/wiki/Dropbox) is a file hosting service that brings everything-traditional files, cloud content, and web shortcuts together in one place.

This notebook covers how to load documents from *Dropbox*. In addition to common files such as text and PDF files, it also supports *Dropbox Paper* files.

## Prerequisites

1. Create a Dropbox app.
2. Give the app these scope permissions: `files.metadata.read` and `files.content.read`.
3. Generate access token: [www.dropbox.com/developers/apps/create](https://www.dropbox.com/developers/apps/create).
4. `pip install dropbox` (requires `pip install "unstructured[pdf]"` for PDF filetype).

## Instructions

`DropboxLoader`` requires you to create a Dropbox App and generate an access token. This can be done from [www.dropbox.com/developers/apps/create](https://www.dropbox.com/developers/apps/create). You also need to have the Dropbox Python SDK installed (pip install dropbox).

DropboxLoader can load data from a list of Dropbox file paths or a single Dropbox folder path. Both paths should be relative to the root directory of the Dropbox account linked to the access token.

```python
pip install dropbox
```

```output
Requirement already satisfied: dropbox in /Users/rbarragan/.local/share/virtualenvs/langchain-kv0dsrF5/lib/python3.11/site-packages (11.36.2)
Requirement already satisfied: requests>=2.16.2 in /Users/rbarragan/.local/share/virtualenvs/langchain-kv0dsrF5/lib/python3.11/site-packages (from dropbox) (2.31.0)
Requirement already satisfied: six>=1.12.0 in /Users/rbarragan/.local/share/virtualenvs/langchain-kv0dsrF5/lib/python3.11/site-packages (from dropbox) (1.16.0)
Requirement already satisfied: stone>=2 in /Users/rbarragan/.local/share/virtualenvs/langchain-kv0dsrF5/lib/python3.11/site-packages (from dropbox) (3.3.1)
Requirement already satisfied: charset-normalizer<4,>=2 in /Users/rbarragan/.local/share/virtualenvs/langchain-kv0dsrF5/lib/python3.11/site-packages (from requests>=2.16.2->dropbox) (3.2.0)
Requirement already satisfied: idna<4,>=2.5 in /Users/rbarragan/.local/share/virtualenvs/langchain-kv0dsrF5/lib/python3.11/site-packages (from requests>=2.16.2->dropbox) (3.4)
Requirement already satisfied: urllib3<3,>=1.21.1 in /Users/rbarragan/.local/share/virtualenvs/langchain-kv0dsrF5/lib/python3.11/site-packages (from requests>=2.16.2->dropbox) (2.0.4)
Requirement already satisfied: certifi>=2017.4.17 in /Users/rbarragan/.local/share/virtualenvs/langchain-kv0dsrF5/lib/python3.11/site-packages (from requests>=2.16.2->dropbox) (2023.7.22)
Requirement already satisfied: ply>=3.4 in /Users/rbarragan/.local/share/virtualenvs/langchain-kv0dsrF5/lib/python3.11/site-packages (from stone>=2->dropbox) (3.11)
Note: you may need to restart the kernel to use updated packages.
```

```python
from langchain_community.document_loaders import DropboxLoader
```

```python
# Generate access token: https://www.dropbox.com/developers/apps/create.
dropbox_access_token = "<DROPBOX_ACCESS_TOKEN>"
# Dropbox root folder
dropbox_folder_path = ""
```

```python
loader = DropboxLoader(
    dropbox_access_token=dropbox_access_token,
    dropbox_folder_path=dropbox_folder_path,
    recursive=False,
)
```

```python
documents = loader.load()
```

```output
File /JHSfLKn0.jpeg could not be decoded as text. Skipping.
File /A REPORT ON WILES’ CAMBRIDGE LECTURES.pdf could not be decoded as text. Skipping.
```

```python
for document in documents:
    print(document)
```
