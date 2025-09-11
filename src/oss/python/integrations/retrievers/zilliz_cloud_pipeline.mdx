---
title: Zilliz Cloud Pipeline
---

> [Zilliz Cloud Pipelines](https://docs.zilliz.com/docs/pipelines) transform your unstructured data to a searchable vector collection, chaining up the embedding, ingestion, search, and deletion of your data.
>
> Zilliz Cloud Pipelines are available in the Zilliz Cloud Console and via RestFul APIs.

This notebook demonstrates how to prepare Zilliz Cloud Pipelines and use the them via a LangChain Retriever.

## Prepare Zilliz Cloud Pipelines

To get pipelines ready for LangChain Retriever, you need to create and configure the services in Zilliz Cloud.

**1. Set up Database**

- [Register with Zilliz Cloud](https://docs.zilliz.com/docs/register-with-zilliz-cloud)
- [Create a cluster](https://docs.zilliz.com/docs/create-cluster)

**2. Create Pipelines**

- [Document ingestion, search, deletion](https://docs.zilliz.com/docs/pipelines-doc-data)
- [Text ingestion, search, deletion](https://docs.zilliz.com/docs/pipelines-text-data)

## Use LangChain Retriever

```python
%pip install -qU langchain-milvus
```

```python
from langchain_milvus import ZillizCloudPipelineRetriever

retriever = ZillizCloudPipelineRetriever(
    pipeline_ids={
        "ingestion": "<YOUR_INGESTION_PIPELINE_ID>",  # skip this line if you do NOT need to add documents
        "search": "<YOUR_SEARCH_PIPELINE_ID>",  # skip this line if you do NOT need to get relevant documents
        "deletion": "<YOUR_DELETION_PIPELINE_ID>",  # skip this line if you do NOT need to delete documents
    },
    token="<YOUR_ZILLIZ_CLOUD_API_KEY>",
)
```

### Add documents

To add documents, you can use the method `add_texts` or `add_doc_url`, which inserts documents from a list of texts or a presigned/public url with corresponding metadata into the store.

- if using a **text ingestion pipeline**, you can use the method `add_texts`, which inserts a batch of texts with the corresponding metadata into the Zilliz Cloud storage.

    **Arguments:**
  - `texts`: A list of text strings.
  - `metadata`: A key-value dictionary of metadata will be inserted as preserved fields required by ingestion pipeline. Defaults to None.

```python
# retriever.add_texts(
#     texts = ["example text 1e", "example text 2"],
#     metadata={"<FIELD_NAME>": "<FIELD_VALUE>"}  # skip this line if no preserved field is required by the ingestion pipeline
#     )
```

- if using a **document ingestion pipeline**, you can use the method `add_doc_url`, which inserts a document from url with the corresponding metadata into the Zilliz Cloud storage.

    **Arguments:**
  - `doc_url`: A document url.
  - `metadata`: A key-value dictionary of metadata will be inserted as preserved fields required by ingestion pipeline. Defaults to None.

The following example works with a document ingestion pipeline, which requires milvus version as metadata. We will use an [example document](https://publicdataset.zillizcloud.com/milvus_doc.md) describing how to delete entities in Milvus v2.3.x.

```python
retriever.add_doc_url(
    doc_url="https://publicdataset.zillizcloud.com/milvus_doc.md",
    metadata={"version": "v2.3.x"},
)
```

```output
{'token_usage': 1247, 'doc_name': 'milvus_doc.md', 'num_chunks': 6}
```

### Get relevant documents

To query the retriever, you can use the method `get_relevant_documents`, which returns a list of LangChain Document objects.

**Arguments:**

- `query`: String to find relevant documents for.
- `top_k`: The number of results. Defaults to 10.
- `offset`: The number of records to skip in the search result. Defaults to 0.
- `output_fields`: The extra fields to present in output.
- `filter`: The Milvus expression to filter search results. Defaults to "".
- `run_manager`: The callbacks handler to use.

```python
retriever.get_relevant_documents(
    "Can users delete entities by complex boolean expressions?"
)
```

```output
[Document(page_content='# Delete Entities\nThis topic describes how to delete entities in Milvus.  \nMilvus supports deleting entities by primary key or complex boolean expressions. Deleting entities by primary key is much faster and lighter than deleting them by complex boolean expressions. This is because Milvus executes queries first when deleting data by complex boolean expressions.  \nDeleted entities can still be retrieved immediately after the deletion if the consistency level is set lower than Strong.\nEntities deleted beyond the pre-specified span of time for Time Travel cannot be retrieved again.\nFrequent deletion operations will impact the system performance.  \nBefore deleting entities by comlpex boolean expressions, make sure the collection has been loaded.\nDeleting entities by complex boolean expressions is not an atomic operation. Therefore, if it fails halfway through, some data may still be deleted.\nDeleting entities by complex boolean expressions is supported only when the consistency is set to Bounded. For details, see Consistency.\\\n\\\n# Delete Entities\n## Prepare boolean expression\nPrepare the boolean expression that filters the entities to delete.  \nMilvus supports deleting entities by primary key or complex boolean expressions. For more information on expression rules and supported operators, see Boolean Expression Rules.', metadata={'id': 448986959321277978, 'distance': 0.7871403694152832}),
 Document(page_content='# Delete Entities\n## Prepare boolean expression\n### Simple boolean expression\nUse a simple expression to filter data with primary key values of 0 and 1:  \n\`\`\`python\nexpr = "book_id in [0,1]"\n\`\`\`\\\n\\\n# Delete Entities\n## Prepare boolean expression\n### Complex boolean expression\nTo filter entities that meet specific conditions, define complex boolean expressions.  \nFilter entities whose word_count is greater than or equal to 11000:  \n\`\`\`python\nexpr = "word_count >= 11000"\n\`\`\`  \nFilter entities whose book_name is not Unknown:  \n\`\`\`python\nexpr = "book_name != Unknown"\n\`\`\`  \nFilter entities whose primary key values are greater than 5 and word_count is smaller than or equal to 9999:  \n\`\`\`python\nexpr = "book_id > 5 && word_count <= 9999"\n\`\`\`', metadata={'id': 448986959321277979, 'distance': 0.7775762677192688}),
 Document(page_content='# Delete Entities\n## Delete entities\nDelete the entities with the boolean expression you created. Milvus returns the ID list of the deleted entities.\n\`\`\`python\nfrom pymilvus import Collection\ncollection = Collection("book")      # Get an existing collection.\ncollection.delete(expr)\n\`\`\`  \nParameter\tDescription\nexpr\tBoolean expression that specifies the entities to delete.\npartition_name (optional)\tName of the partition to delete entities from.\\\n\\\n# Upsert Entities\nThis topic describes how to upsert entities in Milvus.  \nUpserting is a combination of insert and delete operations. In the context of a Milvus vector database, an upsert is a data-level operation that will overwrite an existing entity if a specified field already exists in a collection, and insert a new entity if the specified value doesn’t already exist.  \nThe following example upserts 3,000 rows of randomly generated data as the example data. When performing upsert operations, it\'s important to note that the operation may compromise performance. This is because the operation involves deleting data during execution.', metadata={'id': 448986959321277980, 'distance': 0.680284857749939}),
 Document(page_content='# Upsert Entities\n## Flush data\nWhen data is upserted into Milvus it is updated and inserted into segments. Segments have to reach a certain size to be sealed and indexed. Unsealed segments will be searched brute force. In order to avoid this with any remainder data, it is best to call flush(). The flush() call will seal any remaining segments and send them for indexing. It is important to only call this method at the end of an upsert session. Calling it too often will cause fragmented data that will need to be cleaned later on.\\\n\\\n# Upsert Entities\n## Limits\nUpdating primary key fields is not supported by upsert().\nupsert() is not applicable and an error can occur if autoID is set to True for primary key fields.', metadata={'id': 448986959321277983, 'distance': 0.5672488212585449}),
 Document(page_content='# Upsert Entities\n## Prepare data\nFirst, prepare the data to upsert. The type of data to upsert must match the schema of the collection, otherwise Milvus will raise an exception.  \nMilvus supports default values for scalar fields, excluding a primary key field. This indicates that some fields can be left empty during data inserts or upserts. For more information, refer to Create a Collection.  \n\`\`\`python\n# Generate data to upsert\n\nimport random\nnb = 3000\ndim = 8\nvectors = [[random.random() for _ in range(dim)] for _ in range(nb)]\ndata = [\n[i for i in range(nb)],\n[str(i) for i in range(nb)],\n[i for i in range(10000, 10000+nb)],\nvectors,\n[str("dy"*i) for i in range(nb)]\n]\n\`\`\`', metadata={'id': 448986959321277981, 'distance': 0.5107149481773376}),
 Document(page_content='# Upsert Entities\n## Upsert data\nUpsert the data to the collection.  \n\`\`\`python\nfrom pymilvus import Collection\ncollection = Collection("book") # Get an existing collection.\nmr = collection.upsert(data)\n\`\`\`  \nParameter\tDescription\ndata\tData to upsert into Milvus.\npartition_name (optional)\tName of the partition to upsert data into.\ntimeout (optional)\tAn optional duration of time in seconds to allow for the RPC. If it is set to None, the client keeps waiting until the server responds or error occurs.\nAfter upserting entities into a collection that has previously been indexed, you do not need to re-index the collection, as Milvus will automatically create an index for the newly upserted data. For more information, refer to Can indexes be created after inserting vectors?', metadata={'id': 448986959321277982, 'distance': 0.4341375529766083})]
```
