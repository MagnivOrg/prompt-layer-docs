# Documentation Updater Setup - TODO

## ✅ Completed Steps
- [x] Workflow file deployed to `.github/workflows/update-docs.yml`
- [x] CLAUDE.md policy file copied to docs repository root

## 📋 Remaining Setup Steps

### 1. Install Claude Code GitHub App
Run this command in Claude Code (in a new session):
```bash
/install-github-app
```
This will open a browser to authorize the Claude Code GitHub integration.

### 2. Create Personal Access Token (PAT)

1. **Go to:** https://github.com/settings/tokens/new

2. **Configure the token:**
   - **Token name:** `Docs Updater Read Token`
   - **Expiration:** 90 days (or custom)
   - **Repository access:** Select "Selected repositories" and add:
     - `MagnivOrg/prompt-layer-front-end`
     - `MagnivOrg/prompt-layer-api`
     - `MagnivOrg/prompt-layer-library`
     - `MagnivOrg/prompt-layer-js`
   - **Permissions:**
     - Repository permissions → **Contents:** Read
     - Repository permissions → **Metadata:** Read (automatically selected)

3. **Click:** "Generate token"

4. **IMPORTANT:** Copy the token immediately (starts with `ghp_`)

### 3. Add Secrets to GitHub Repository

1. **Go to:** https://github.com/MagnivOrg/prompt-layer-docs/settings/secrets/actions

2. **Add Secret #1:**
   - Click "New repository secret"
   - **Name:** `GH_READ_TOKEN`
   - **Value:** [Paste your Personal Access Token from step 2]
   - Click "Add secret"

3. **Add Secret #2:**
   - Click "New repository secret"
   - **Name:** `ANTHROPIC_API_KEY`
   - **Value:** [Your Anthropic API key from console.anthropic.com]
   - Click "Add secret"

### 4. Commit and Push the Changes

```bash
cd prompt-layer-docs
git add .github/workflows/update-docs.yml CLAUDE.md
git commit -m "feat: add automated documentation updater workflow

- Daily GitHub Action to scan repos for user-facing changes
- Uses Claude Code to identify documentable changes
- Creates one PR per day with updates
- Excludes internal APIs and UI improvements"
git push origin main
```

### 5. Test the Workflow

**Option A: Wait for the daily run**
- The workflow runs daily at 09:00 UTC

**Option B: Trigger manually (recommended for first test)**
```bash
# From the prompt-layer-docs directory
gh workflow run update-docs.yml
gh run watch  # Watch the execution
```

**Option C: Via GitHub UI**
1. Go to: https://github.com/MagnivOrg/prompt-layer-docs/actions
2. Click "Update Documentation" workflow
3. Click "Run workflow" → "Run workflow"

### 6. Verify the Setup

After the first run, check:
- [ ] Workflow completes successfully (green checkmark)
- [ ] If changes were found, a PR was created
- [ ] The PR contains only legitimate user-facing changes
- [ ] No internal API endpoints were documented

## 🔒 Security Checklist

- [ ] PAT has minimal permissions (read-only)
- [ ] PAT is set to expire (90 days recommended)
- [ ] Secrets are stored in GitHub, not in code
- [ ] Workflow file doesn't expose any secrets

## 🚨 Troubleshooting

### If the workflow fails:

1. **Check Actions tab:** https://github.com/MagnivOrg/prompt-layer-docs/actions
2. **Common issues:**
   - Missing secrets (GH_READ_TOKEN or ANTHROPIC_API_KEY)
   - PAT doesn't have access to all 4 repos
   - Claude Code GitHub app not installed

### If no PR is created:
- This is normal if no user-facing changes were found
- Check the workflow logs to see what commits were analyzed

### If wrong things are documented:
- Review the CLAUDE.md policy file
- Internal `/api/dashboard/v2/*` endpoints should be skipped
- UI improvements should be skipped

## 📞 Support

- **Claude Code issues:** https://github.com/anthropics/claude-code/issues
- **Workflow logs:** https://github.com/MagnivOrg/prompt-layer-docs/actions