# How to recursively split text by characters

<Info>
**Prerequisites**


This guide assumes familiarity with the following concepts:

- [Text splitters](/oss/concepts/text_splitters)

</Info>

This text splitter is the recommended one for generic text. It is parameterized by a list of characters. It tries to split on them in order until the chunks are small enough. The default list is `["\n\n", "\n", " ", ""]`. This has the effect of trying to keep all paragraphs (and then sentences, and then words) together as long as possible, as those would generically seem to be the strongest semantically related pieces of text.

1. How the text is split: by list of characters.
2. How the chunk size is measured: by number of characters.

Below we show example usage.

To obtain the string content directly, use `.splitText`.

To create LangChain [Document](https://api.js.langchain.com/classes/langchain_core.documents.Document.html) objects (e.g., for use in downstream tasks), use `.createDocuments`.


```typescript
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";

const text = `Hi.\n\nI'm Harrison.\n\nHow? Are? You?\nOkay then f f f f.
This is a weird text to write, but gotta test the splittingggg some how.\n\n
Bye!\n\n-H.`;
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 10,
  chunkOverlap: 1,
});

const output = await splitter.createDocuments([text]);

console.log(output.slice(0, 3));
```
```output
[
  Document {
    pageContent: "Hi.",
    metadata: { loc: { lines: { from: 1, to: 1 } } }
  },
  Document {
    pageContent: "I'm",
    metadata: { loc: { lines: { from: 3, to: 3 } } }
  },
  Document {
    pageContent: "Harrison.",
    metadata: { loc: { lines: { from: 3, to: 3 } } }
  }
]
```
You'll note that in the above example we are splitting a raw text string and getting back a list of documents. We can also split documents directly.


```typescript
import { Document } from "@langchain/core/documents";
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";

const text = `Hi.\n\nI'm Harrison.\n\nHow? Are? You?\nOkay then f f f f.
This is a weird text to write, but gotta test the splittingggg some how.\n\n
Bye!\n\n-H.`;
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 10,
  chunkOverlap: 1,
});

const docOutput = await splitter.splitDocuments([
  new Document({ pageContent: text }),
]);

console.log(docOutput.slice(0, 3));
```
```output
[
  Document {
    pageContent: "Hi.",
    metadata: { loc: { lines: { from: 1, to: 1 } } }
  },
  Document {
    pageContent: "I'm",
    metadata: { loc: { lines: { from: 3, to: 3 } } }
  },
  Document {
    pageContent: "Harrison.",
    metadata: { loc: { lines: { from: 3, to: 3 } } }
  }
]
```
You can customize the `RecursiveCharacterTextSplitter` with arbitrary separators by passing a `separators` parameter like this:


```typescript
import { RecursiveCharacterTextSplitter } from "langchain/text_splitter";
import { Document } from "@langchain/core/documents";

const text = `Some other considerations include:

- Do you deploy your backend and frontend together, or separately?
- Do you deploy your backend co-located with your database, or separately?

**Production Support:** As you move your LangChains into production, we'd love to offer more hands-on support.
Fill out [this form](https://airtable.com/appwQzlErAS2qiP0L/shrGtGaVBVAz7NcV2) to share more about what you're building, and our team will get in touch.

## Deployment Options

See below for a list of deployment options for your LangChain app. If you don't see your preferred option, please get in touch and we can add it to this list.`;

const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 50,
  chunkOverlap: 1,
  separators: ["|", "##", ">", "-"],
});

const docOutput = await splitter.splitDocuments([
  new Document({ pageContent: text }),
]);

console.log(docOutput.slice(0, 3));
```
```output
[
  Document {
    pageContent: "Some other considerations include:",
    metadata: { loc: { lines: { from: 1, to: 1 } } }
  },
  Document {
    pageContent: "- Do you deploy your backend and frontend together",
    metadata: { loc: { lines: { from: 3, to: 3 } } }
  },
  Document {
    pageContent: "r, or separately?",
    metadata: { loc: { lines: { from: 3, to: 3 } } }
  }
]
```
## Next steps

You've now learned a method for splitting text by character.

Next, check out [specific techinques for splitting on code](/oss/how-to/code_splitter) or the [full tutorial on retrieval-augmented generation](/oss/tutorials/rag).
