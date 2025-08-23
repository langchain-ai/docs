# How to split by character

<Info>
**Prerequisites**


This guide assumes familiarity with the following concepts:

- [Text splitters](/oss/concepts/text_splitters)

</Info>

This is the simplest method for splitting text. This splits based on a given character sequence, which defaults to `"\n\n"`. Chunk length is measured by number of characters.

1. How the text is split: by single character separator.
2. How the chunk size is measured: by number of characters.

To obtain the string content directly, use `.splitText()`.

To create LangChain [Document](https://api.js.langchain.com/classes/langchain_core.documents.Document.html) objects (e.g., for use in downstream tasks), use `.createDocuments()`.


```typescript
import { CharacterTextSplitter } from "@langchain/textsplitters";
import * as fs from "node:fs";

// Load an example document
const rawData = await fs.readFileSync("../../../../examples/state_of_the_union.txt");
const stateOfTheUnion = rawData.toString();

const textSplitter = new CharacterTextSplitter({
    separator: "\n\n",
    chunkSize: 1000,
    chunkOverlap: 200,
});
const texts = await textSplitter.createDocuments([stateOfTheUnion]);
console.log(texts[0])
```
```output
Document {
  pageContent: "Madam Speaker, Madam Vice President, our First Lady and Second Gentleman. Members of Congress and th"... 839 more characters,
  metadata: { loc: { lines: { from: 1, to: 17 } } }
}
```
You can also propagate metadata associated with each document to the output chunks:


```typescript
const metadatas = [{ document: 1 }, { document: 2 }];

const documents = await textSplitter.createDocuments(
    [stateOfTheUnion, stateOfTheUnion], metadatas
)

console.log(documents[0])
```
```output
Document {
  pageContent: "Madam Speaker, Madam Vice President, our First Lady and Second Gentleman. Members of Congress and th"... 839 more characters,
  metadata: { document: 1, loc: { lines: { from: 1, to: 17 } } }
}
```
To obtain the string content directly, use `.splitText()`:


```typescript
const chunks = await textSplitter.splitText(stateOfTheUnion);

chunks[0];
```



```output
"Madam Speaker, Madam Vice President, our First Lady and Second Gentleman. Members of Congress and th"... 839 more characters
```


## Next steps

You've now learned a method for splitting text by character.

Next, check out a [more advanced way of splitting by character](/oss/how-to/recursive_text_splitter), or the [full tutorial on retrieval-augmented generation](/oss/tutorials/rag).
