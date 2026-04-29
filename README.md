# PromptLayer Docs

PromptLayer is an AI engineering workbench for teams building with prompts, agents, and LLM workflows. It helps you version prompts, evaluate changes, manage datasets, inspect traces, and monitor production behavior across providers.

This repository contains the PromptLayer documentation site. The site is built with [Mintlify](https://mintlify.com), a documentation framework for MDX content, navigation, API references, and local previews. Global site configuration lives in `docs.json`.

## Quick Start

Install the Mintlify CLI:

```bash
npm i -g mint
```

Run the docs locally from this directory:

```bash
mint dev
```

The local preview runs at `http://localhost:3000`.

You can also run the preview without a global install:

```bash
npx mint dev
```

Before opening a pull request, validate the docs build:

```bash
mint validate
```

## Contributing

Contributions are welcome. If you see an update, typo, missing explanation, unclear example, or you are working on something others would find helpful, please open a pull request.

Good contributions include:

- Improving quickstarts, guides, and examples
- Adding screenshots or clarifying product flows
- Updating SDK, API, or provider details
- Fixing broken links, outdated screenshots, or confusing wording

Keep changes focused, test the site locally when possible, and include enough context in the pull request for reviewers to understand the update.
