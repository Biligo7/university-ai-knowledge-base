# Root Agents

These are the agents that drive the pipeline. They are deliberately IDE-agnostic: each one is a plain Markdown file with YAML frontmatter (`name`, `description`) and a body that describes a role, a contract, and a workflow.

## Pipeline at a glance

```
                 ┌────────────────────┐
   user input →  │  kb-initializer    │  ← orchestrator (start here)
                 └────────┬───────────┘
                          │ runs tools/init_subject.py, organises raw/,
                          │ runs tools/regenerate.py, then delegates ↓
        ┌─────────────────┼──────────────────┬───────────────────┐
        ▼                 ▼                  ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐   ┌────────────────┐
│ image-curator│  │ md-formatter │  │ (filter_     │   │ tutor-generator│
│ (vision)     │  │ (visual)     │  │  images.py)  │   │ (authoring)    │
└──────────────┘  └──────────────┘  └──────────────┘   └────────────────┘
```

## Agents in this folder

| Agent | Purpose |
|---|---|
| [`kb-initializer.md`](kb-initializer.md) | Entry point. Takes the user's subject name, PDFs and categories; bootstraps the whole subject and delegates to the others. |
| [`image-curator.md`](image-curator.md) | Reviews every extracted image with vision and removes decorative ones (logos, portraits, screenshots, watermarks). Updates Markdown references. |
| [`md-formatter.md`](md-formatter.md) | Reviews the final Markdown for readability, fixes anything the heuristic script missed (mis-classified headings, code blocks, stray symbols). |
| [`tutor-generator.md`](tutor-generator.md) | Reads the curated knowledge base and writes the per-subject tutor agent into `subjects/<slug>/agents/<slug>-tutor.md`. |

## Invoking these agents

See [`../docs/ide-integration.md`](../docs/ide-integration.md) for how to load these files into Cursor, Claude Code, GitHub Copilot Chat, ChatGPT custom GPTs, or a generic chat session.

The short version: open the agent's `.md` file and use its contents as the system prompt for a new chat. Pass the user inputs the agent asks for at the top, then let it run.
