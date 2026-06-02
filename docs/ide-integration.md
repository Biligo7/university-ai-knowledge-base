# IDE integration

The agents in this repository are plain Markdown files with a small YAML frontmatter block. Any AI assistant that lets you load a system prompt — or paste one into a chat — can run them. The sections below give the shortest path that works for each popular IDE.

## Agent file format

Every file under `agents/` and `templates/tutor-agent.md` looks like this:

```markdown
---
name: kb-initializer
description: One-sentence summary used by IDEs that show an agent picker.
---

# Role

…instructions for the model…
```

The `name` and `description` fields are optional in pure-prompt IDEs but useful for IDEs that have a native agent registry.

---

## Cursor

Cursor reads agents from `.cursor/agents/*.md`. Two options:

**Option A — symlink (recommended).** Keeps the repository agents as the single source of truth.

```bash
mkdir -p .cursor
ln -s ../agents .cursor/agents
```

For per-subject tutors:

```bash
mkdir -p subjects/<slug>/.cursor
ln -s ../agents subjects/<slug>/.cursor/agents
```

**Option B — copy.** If symlinks are awkward on Windows:

```bash
mkdir -p .cursor/agents
cp agents/*.md .cursor/agents/
```

Invoke from the chat with `/kb-initializer`, `/image-curator`, etc., or by typing the agent's name.

---

## Claude Code

Claude Code reads agents from `.claude/agents/*.md`. The frontmatter format is the same.

```bash
mkdir -p .claude/agents
cp agents/*.md .claude/agents/
```

Per-subject tutors go under `subjects/<slug>/.claude/agents/`.

Invoke with `@kb-initializer` or by mentioning the agent in chat.

---

## GitHub Copilot Chat

Copilot Chat does not have a multi-agent registry, but it does respect `.github/copilot-instructions.md` per repository. Two patterns work:

- **Single active agent.** Copy the body of one agent file into `.github/copilot-instructions.md`. Swap files when you need a different role.
- **Chat-time injection.** Open the agent's `.md` file, copy everything below the frontmatter, paste it into the chat as the first message, then ask your question.

For per-subject tutors, the second pattern is the most reliable — keep the tutor file in `subjects/<slug>/agents/tutor.md` and paste it in when you need it.

---

## ChatGPT custom GPTs

Create a new GPT. In the **Instructions** field, paste the body of the agent (everything after the YAML frontmatter). Add the `description` from the frontmatter to the GPT's description field. Upload the relevant kb files as knowledge if you want the GPT to operate offline; otherwise let it call out to a file-search action that points back to this repository.

---

## Generic chat (any model)

Open the agent file. Copy everything from `# Role` onwards. Paste it as the first message of a new chat. Then send your real prompt.

This is the lowest common denominator and works with every assistant.

---

## Per-subject tutor

After the pipeline finishes, the tutor for a subject lives at:

```
subjects/<slug>/agents/tutor.md
```

Wire it into your IDE the same way as the root agents — symlink, copy, or paste. The tutor is fully self-contained (it includes the topic index, exam patterns and image pointers in its prompt) so you do not need to attach the kb files separately, but doing so makes citations faster and more accurate.

---

## Multiple subjects in one workspace

Open the repository as the workspace root. The root agents in `agents/` apply to the whole workspace; the tutor in `subjects/<slug>/agents/tutor.md` is scoped to one subject. In Cursor and Claude Code, both layers are discovered automatically when you symlink the per-subject `.cursor` / `.claude` directories as shown above.

If your IDE does not support nested agent registries, just paste the tutor you currently need into the chat as a system prompt.
