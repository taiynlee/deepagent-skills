# Find Skills — Detailed Reference

## Skills CLI Overview

The Skills CLI (`npx skills`) is the package manager for the open agent skills ecosystem.

**Key commands:**

| Command | Description |
|---------|-------------|
| `npx skills find [query]` | Search for skills interactively or by keyword |
| `npx skills add <package>` | Install a skill from GitHub or other sources |
| `npx skills check` | Check for skill updates |
| `npx skills update` | Update all installed skills |
| `npx skills init <name>` | Create a new skill from scratch |
| `npx skills list` | List installed skills |

**Browse skills at:** https://skills.sh/

## Search Examples

### By Task Domain

```
npx skills find "API documentation"
npx skills find "database schema"
npx skills find "docker deployment"
npx skills find "CI/CD pipeline"
npx skills find "security audit"
```

### By Tool/Framework

```
npx skills find "React hooks"
npx skills find "Next.js routing"
npx skills find "PostgreSQL query"
npx skills find "Kubernetes helm"
```

### By Use Case

```
npx skills find "email sending"
npx skills find "Slack notification"
npx skills find "calendar integration"
npx skills find "payment processing"
```

## Install Syntax

```
npx skills add <owner/repo@skill> [flags]
```

### Common Flags

| Flag | Description |
|------|-------------|
| `-g, --global` | Install globally (user-level) |
| `-y, --yes` | Skip confirmation prompts |
| `-o, --overwrite` | Overwrite if skill already exists |

### Examples

```bash
# From a GitHub repo
npx skills add vercel-labs/agent-skills@react-best-practices -g -y

# From a specific branch
npx skills add owner/repo@skill-name -g -y --branch main

# Local development
npx skills add ./my-custom-skill -y
```

## Skill Quality Checklist

Before recommending a skill to the user, verify:

- [ ] Install count ≥ 1,000 (prefer higher)
- [ ] Source is a reputable organization or author
- [ ] GitHub repo has ≥ 100 stars
- [ ] README is clear and well-documented
- [ ] Skill is actively maintained (recent commits)
- [ ] Compatible with the current agent platform version

## Skill Creation Workflow

If no existing skill fits the user's needs:

1. **Initialize:**
   ```bash
   npx skills init my-new-skill
   ```

2. **Structure:**
   ```
   my-new-skill/
   ├── SKILL.md           # Required: name, description, instructions
   ├── references/        # Optional: detailed docs
   ├── scripts/           # Optional: executable code
   └── assets/            # Optional: templates, images
   ```

3. **SKILL.md Frontmatter (required):**
   ```yaml
   ---
   name: my-new-skill
   description: "What this skill does and when to use it."
   license: MIT
   compatibility: designed for deepagents-cli
   ---
   ```

4. **Test locally before sharing.**

## Skill Sources to Check

| Source | URL | Notes |
|--------|-----|-------|
| skills.sh | https://skills.sh/ | Official skill marketplace |
| vercel-labs | GitHub | 100K+ installs each skill |
| anthropics | GitHub | Official Claude skills |
| microsoft | GitHub | Enterprise-focused skills |
| ComposioHQ | GitHub | Broad tool integrations |

## Troubleshooting

**"No skills found"**
- Try broader keywords
- Check the skills.sh leaderboard for similar terms
- Consider if the task is too niche for a shared skill

**"Install failed"**
- Verify GitHub repo exists and is public
- Check if the skill name/branch is correct
- Try with `--yes` flag to see detailed errors

**"Skill not working"**
- Check if the skill is compatible with your agent platform
- Verify all required files are present in the skill directory
- Check the skill's documentation for platform-specific notes