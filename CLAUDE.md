# CLAUDE.md - Documentation Update Policy

## Core Principle

Documentation serves three specific audiences:
1. **Brand new users** learning what PromptLayer does
2. **Prospective users** deciding whether to use PromptLayer
3. **Current users** seeking help with specific features

Focus on features that expand WHAT users can do, not HOW WELL they can do it.

## Decision Framework

When reviewing a commit, ask:

1. **Does this introduce a NEW capability?**
   - Yes → Document it
   - No, just improves existing → Skip

2. **Would this influence a purchase decision?**
   - Yes → Document it
   - No → Skip

3. **Do users need instructions to use this?**
   - Yes → Document it
   - No, it's self-evident → Skip

4. **Is this part of our public API/SDK?**
   - Yes → Must document
   - No → Skip

## What counts as "user-facing"?

### ✅ Include these changes:
- **New features that expand capabilities** - Things users couldn't do before
- **Features that differentiate from competitors** - Unique selling points
- **Major workflow changes** - New ways of working
- **New integrations or model support** - Expands what can be connected
- **Public API/SDK changes** - All endpoints, methods, breaking changes
- **Deployment & setup options** - Self-hosting, new installation methods
- **Authentication & rate limit changes** - Security and access updates
- **Deprecations or removals** - Features going away

### ❌ Ignore these changes:
- **UI/UX improvements** - Visual enhancements, reorganizations, loading states
- **Quality of life updates** - Button positions, tooltips, helper features
- **Performance improvements** - Speed, reliability, optimization
- **Backend refactoring** - Database changes, internal APIs, queue improvements
- **Bug fixes** - Unless they prevented core functionality
- **Error message improvements** - Better wording or formatting
- **Internal API routes** - `/api/dashboard/v2/*` endpoints (internal use only)
- **Test updates** - Testing infrastructure
- **Documentation-only changes** - Doc fixes themselves
- **CI/CD changes** - Build and deployment processes

## Documentation Style

### File to Update
- Primary file: `docs/changelog/whats-new.md` (or as specified)
- Only modify this designated file - no other files

### Format Requirements
- Create or update a section titled with today's date in **YYYY-MM-DD** format
- Use bullet points only, no paragraphs
- Format each bullet as: **Component: Short title** — one-sentence summary
- Include commit hash or PR link when available
- Group changes by component if multiple changes on same day:
  - **Frontend**: changes
  - **API**: changes
  - **Python SDK**: changes
  - **JavaScript SDK**: changes

### Example Entry
```markdown
## 2024-01-15

**Frontend: Added dark mode toggle** — Users can now switch between light and dark themes from settings menu. [#123](link)

**API: New /analytics endpoint** — Provides detailed usage analytics with customizable date ranges. [abc123](commit)

**Python SDK: Added batch processing** — New `batch_process()` method for handling multiple requests efficiently. [#456](link)

**JavaScript SDK: Breaking change to client init** — Constructor now requires explicit API version parameter. [def456](commit)
```

## Safety Guidelines

### Do's:
- Only modify the designated documentation file
- Verify changes are actually user-facing before documenting
- Keep descriptions concise and clear
- Focus on the "what" and "why" for users
- Preserve existing documentation sections

### Don'ts:
- Don't modify source code files
- Don't create new files unless explicitly instructed
- Don't duplicate entries across different dates
- Don't include internal implementation details
- Don't document draft PRs or unmerged changes

## Real Examples

### ✅ Examples to Document:
- "Add self-hosted deployment option" → New deployment capability
- "Add support for Claude 3.5 Sonnet" → New model support
- "New public API endpoint for prompt templates" → Public API addition
- "Add workflow branching and conditionals" → New feature capability
- "Introduce evaluation framework" → Major new capability

### ❌ Examples to Skip:
- "Add Jinja template snippets to slash command menu" → UX helper for existing feature
- "Add workflow execution counts display" → UI enhancement
- "Improved report score loading states" → UX improvement
- "Enhanced input variable parsing" → Backend improvement
- "Fix pagination end_time parameter" → Internal logic fix
- "Update prompt editor modal" → UI reorganization

## Commit Review Process

When reviewing commits:
1. Apply the Decision Framework questions first
2. Look for keywords: "new", "introduce", "support for", "integration"
3. Be skeptical of: "improve", "enhance", "fix", "update", "refactor"
4. Check if it's a PUBLIC API/SDK change (not internal `/api/dashboard/` routes)
5. Skip commits with only test files or internal refactoring

## Important API Distinctions

### Public APIs (DOCUMENT):
- REST API endpoints at `/api/v1/*` or `/api/public/*`
- SDK methods in promptlayer-python or promptlayer-js
- Webhook endpoints
- Authentication endpoints

### Internal APIs (SKIP):
- `/api/dashboard/v2/*` - Internal dashboard endpoints
- `/api/internal/*` - Internal service communication
- GraphQL mutations/queries for UI only
- Admin-only endpoints

## Priority Order

When multiple changes exist, prioritize documentation by impact:
1. Breaking changes (highest priority)
2. New features or capabilities
3. Deprecations
4. UI/UX improvements
5. API/SDK enhancements
6. Bug fixes (only if user-impacting)