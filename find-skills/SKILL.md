---
name: find-skills
description: "Helps users discover and install agent skills when they ask: how do I do X, find a skill for X, is there a skill that can..., or express interest in extending capabilities. Also use when the user mentions they wish they had help with a specific domain. Triggered by phrases like \"find a skill\", \"search skills\", \"is there a skill for X\", \"how to extend agent\", \"install a skill\"."
license: MIT
compatibility: designed for deepagents-cli
---

# Find Skills

This skill helps discover and install skills from the open agent skills ecosystem.

## When to Use This Skill

Use this skill when the user:
- Asks "how do I do X" where X might have an existing skill
- Says "find a skill for X" or "is there a skill for X"
- Asks "can you do X" where X is a specialized capability
- Expresses interest in extending agent capabilities
- Wants to search for tools, templates, or workflows
- Mentions they wish they had help with a specific domain

## Workflow

### Step 1: Understand What They Need

Identify:
1. The domain (e.g., React, testing, design, deployment)
2. The specific task (e.g., writing tests, creating animations, reviewing PRs)
3. Whether this is common enough that a skill likely exists

### Step 2: Check the Leaderboard First

Check [skills.sh leaderboard](https://skills.sh/) to see if a well-known skill already exists.

Top sources:
- `vercel-labs/agent-skills` — React, Next.js, web design (100K+ installs)
- `anthropics/skills` — Frontend design, document processing (100K+ installs)

### Step 3: Search for Skills

If leaderboard doesn't cover the need, run:

```bash
npx skills find [query]
```

Examples:
- "how do I make React faster?" → `npx skills find react performance`
- "can you help with PR reviews?" → `npx skills find pr review`
- "I need to create a changelog" → `npx skills find changelog`

### Step 4: Verify Quality

**Do not recommend based solely on search results.** Always verify:

1. **Install count** — Prefer 1K+ installs, be cautious with <100
2. **Source reputation** — Official sources (`vercel-labs`, `anthropics`, `microsoft`) are more trustworthy
3. **GitHub stars** — <100 stars should be treated with skepticism

### Step 5: Present Options

Present to the user with:
1. Skill name and what it does
2. Install count and source
3. Install command
4. Link to learn more at skills.sh

Example:
```
Found one! The "react-best-practices" skill provides React and Next.js
performance optimization guidelines from Vercel Engineering. (185K installs)

To install:
npx skills add vercel-labs/agent-skills@react-best-practices

Learn more: https://skills.sh/vercel-labs/agent-skills/react-best-practices
```

### Step 6: Offer to Install

If the user wants to proceed:

```bash
npx skills add <owner/repo@skill> -g -y
```

The `-g` flag installs globally (user-level), `-y` skips confirmation.

## When No Skills Found

If no relevant skills exist:
1. Acknowledge that no existing skill was found
2. Offer to help with the task directly
3. Suggest creating their own skill: `npx skills init my-skill`

## Common Categories

| Category | Example Queries |
|----------|----------------|
| Web Dev | react, nextjs, typescript, tailwind |
| Testing | jest, playwright, e2e |
| DevOps | docker, kubernetes, ci-cd |
| Documentation | docs, readme, changelog |
| Code Quality | review, lint, refactor |
| Design | ui, ux, design-system |

## Tips

1. **Use specific keywords**: "react testing" is better than just "testing"
2. **Try alternative terms**: If "deploy" doesn't work, try "deployment" or "ci-cd"
3. **Check popular sources**: `vercel-labs/agent-skills`, `ComposioHQ/awesome-claude-skills`

## Detailed Reference

For detailed instructions and complete workflow, see [references/find-skills-guide.md](references/find-skills-guide.md).