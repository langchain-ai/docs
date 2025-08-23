---
sidebar_position: 1
---

# How to use example selectors

<Info>
**Prerequisites**


This guide assumes familiarity with the following concepts:

- [Prompt templates](/oss/concepts/prompt_templates)
- [Few-shot examples](/oss/how-to/few_shot_examples)

</Info>

If you have a large number of examples, you may need to select which ones to include in the prompt. The Example Selector is the class responsible for doing so.

The base interface is defined as below:

```typescript
class BaseExampleSelector {
  addExample(example: Example): Promise<void | string>;

  selectExamples(input_variables: Example): Promise<Example[]>;
}
```

The only method it needs to define is a `selectExamples` method. This takes in the input variables and then returns a list of examples. It is up to each specific implementation as to how those examples are selected.

LangChain has a few different types of example selectors. For an overview of all these types, see the below table.

In this guide, we will walk through creating a custom example selector.

## Examples

In order to use an example selector, we need to create a list of examples. These should generally be example inputs and outputs. For this demo purpose, let's imagine we are selecting examples of how to translate English to Italian.


```typescript
const examples = [
    { input: "hi", output: "ciao" },
    { input: "bye", output: "arrivaderci" },
    { input: "soccer", output: "calcio" },
];
```

## Custom Example Selector

Let's write an example selector that chooses what example to pick based on the length of the word.


```typescript
import { BaseExampleSelector } from "@langchain/core/example_selectors";
import { Example } from "@langchain/core/prompts";


class CustomExampleSelector extends BaseExampleSelector {
    private examples: Example[];
  
    constructor(examples: Example[]) {
      super();
      this.examples = examples;
    }
  
    async addExample(example: Example): Promise<void | string> {
      this.examples.push(example);
      return;
    }
  
    async selectExamples(inputVariables: Example): Promise<Example[]> {
      // This assumes knowledge that part of the input will be a 'text' key
      const newWord = inputVariables.input;
      const newWordLength = newWord.length;
  
      // Initialize variables to store the best match and its length difference
      let bestMatch: Example | null = null;
      let smallestDiff = Infinity;
  
      // Iterate through each example
      for (const example of this.examples) {
        // Calculate the length difference with the first word of the example
        const currentDiff = Math.abs(example.input.length - newWordLength);
  
        // Update the best match if the current one is closer in length
        if (currentDiff < smallestDiff) {
          smallestDiff = currentDiff;
          bestMatch = example;
        }
      }
  
      return bestMatch ? [bestMatch] : [];
    }
  }
```


```typescript
const exampleSelector = new CustomExampleSelector(examples)
```


```typescript
await exampleSelector.selectExamples({ input: "okay" })
```



```output
[ { input: "bye", output: "arrivaderci" } ]
```



```typescript
await exampleSelector.addExample({ input: "hand", output: "mano" })
```


```typescript
await exampleSelector.selectExamples({ input: "okay" })
```



```output
[ { input: "hand", output: "mano" } ]
```


## Use in a Prompt

We can now use this example selector in a prompt


```typescript
import { PromptTemplate, FewShotPromptTemplate } from "@langchain/core/prompts"

const examplePrompt = PromptTemplate.fromTemplate("Input: {input} -> Output: {output}")
```


```typescript
const prompt = new FewShotPromptTemplate({
    exampleSelector,
    examplePrompt,
    suffix: "Input: {input} -> Output:",
    prefix: "Translate the following words from English to Italian:",
    inputVariables: ["input"],
})

console.log(await prompt.format({ input: "word" }))
```
```output
Translate the following words from English to Italian:

Input: hand -> Output: mano

Input: word -> Output:
```
## Example Selector Types

| Name       | Description                                                                                 |
|------------|---------------------------------------------------------------------------------------------|
| Similarity | Uses semantic similarity between inputs and examples to decide which examples to choose.    |
| Length     | Selects examples based on how many can fit within a certain length                          |

## Next steps

You've now learned a bit about using example selectors to few shot LLMs.

Next, check out some guides on some other techniques for selecting examples:

- [How to select examples by length](/oss/how-to/example_selectors_length_based)
- [How to select examples by similarity](/oss/how-to/example_selectors_similarity)
