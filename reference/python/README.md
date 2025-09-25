## Python Reference Docs

All python reference docs are auto-generated as apart of a github workflow in the [langchain-ai/langchain](https://github.com/langchain-ai/langchain) repo. Once a day, a new release of reference docs is generated through that action, and artifacts are uploaded to the [langchain-ai/langchain-api-docs-html](https://github.com/langchain-ai/langchain-api-docs-html) repo. (See the [workflow](https://github.com/langchain-ai/langchain/tree/master/.github/workflows/api_doc_build.yml))

The `Makefile` in this directory is used to pull those artifacts into this repo to be used in the reference docs served at `reference.langchain.com`
