# Review Guidelines

Use these guidelines when reviewing PRs into `promptlayer-docs`. Prioritize concise, public-facing docs with predictable structure and stable URLs.

## Structure

Place pages by user intent:

- **Get Started**: onboarding, quickstarts, setup, migration.
- **Core Concepts**: product concepts and UI reference.
- **Providers**: provider/model setup and compatibility.
- **Guides**: task-oriented workflows.
- **AI Tools**: assistant/tooling docs.
- **Reference**: SDKs, REST API, Webhooks, schemas, events, exact interfaces.

Keep REST API, SDKs, and Webhooks under **Reference**.

## REST API Pages

REST endpoint pages should be OpenAPI-first and lightweight:

```mdx
---
title: "List Datasets"
openapi: "GET /api/public/v2/datasets"
---

Briefly explain what the endpoint does and any key behavior.
```

The MDX page should usually contain only:

- `title` and `openapi` frontmatter.
- A short 1-3 sentence overview.
- Optional behavior notes for non-obvious semantics.
- Optional related links.

Put API mechanics in `openapi.json`, not Markdown: auth, headers, parameters, request bodies, response schemas, errors, pagination, filtering, and examples.

Avoid manual `Authentication`, `Example`, `Response`, parameter, or schema sections unless they explain behavior OpenAPI cannot express.

## Style

Write for users trying to complete a task.

Prefer:

- Direct, concrete language.
- Active voice and present tense.
- Specific titles and sidebar labels.
- Consistent PromptLayer terms.
- Action-oriented endpoint titles like `List X`, `Get X`, `Create X`, `Update X`, `Delete X`.

Avoid:

- Marketing copy.
- Internal implementation details.
- Long tutorials in reference pages.
- Duplicating generated OpenAPI content.
- Generic labels like `Usage`, `Features`, or `Integrations`.

## Review Comments

When leaving PR review comments, tag Claude directly:

```md
@claude <actionable review comment>
```

Keep comments specific, actionable, and tied to the docs guideline being enforced.

## Review Checklist

Before approving, check that:

- The page is in the right nav section.
- URLs are preserved, or redirects are included.
- Titles, labels, slugs, and links are clear and consistent.
- REST pages use the minimal OpenAPI-backed format.
- `openapi` frontmatter exactly matches `openapi.json`.
- OpenAPI contains the real API contract and examples.
- Copy is concise, useful, and public-facing.

For nav, frontmatter, OpenAPI, or link changes, run:

```sh
jq empty docs.json
jq empty openapi.json
mint broken-links
mint validate
```
