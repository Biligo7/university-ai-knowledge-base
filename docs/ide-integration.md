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

Cursor reads agents from `.cursor/agents/*.md`. There is only **one** `.cursor` directory — at the repository root. Subject-specific tutors are referenced directly by path, not via a separate `.cursor`.

**Option A — symlink (recommended).** Run from the repository root:

```bash
cd university-ai-knowledge-base   # your clone
mkdir -p .cursor
ln -s ../agents .cursor/agents
```

This makes the pipeline agents (`kb-initializer`, `image-curator`, etc.) appear in the Cursor agent picker.

**Option B — copy.** If symlinks are awkward on Windows:

```bash
mkdir -p .cursor/agents
cp agents/*.md .cursor/agents/
# then copy subject specific agents (tutors)
cp subjects/yoursubject/agents/*.md .cursor/agents/
```

**Subject tutors.** After the pipeline runs, the tutor lives at `subjects/<slug>/agents/<slug>-tutor.md` (e.g. `subjects/algorithms/agents/algorithms-tutor.md`). Reference it directly in Cursor with `@subjects/algorithms/agents/algorithms-tutor.md`, or paste its contents into a chat. There is no need for a second `.cursor` directory inside each subject.

Invoke pipeline agents from the chat with `/kb-initializer`, `/image-curator`, etc., or by typing the agent's name.

---

## Claude Code

Claude Code reads agents from `.claude/agents/*.md`. The frontmatter format is the same.

```bash
mkdir -p .claude/agents
cp agents/*.md .claude/agents/
```

For per-subject tutors, reference `subjects/<slug>/agents/<slug>-tutor.md` directly with `@` or paste the contents.

Invoke with `@kb-initializer` or by mentioning the agent in chat.

---

## GitHub Copilot Chat

Copilot Chat does not have a multi-agent registry, but it does respect `.github/copilot-instructions.md` per repository. Two patterns work:

- **Single active agent.** Copy the body of one agent file into `.github/copilot-instructions.md`. Swap files when you need a different role.
- **Chat-time injection.** Open the agent's `.md` file, copy everything below the frontmatter, paste it into the chat as the first message, then ask your question.

For per-subject tutors, the second pattern is the most reliable — keep the tutor file in `subjects/<slug>/agents/<slug>-tutor.md` and paste it in when you need it.

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
subjects/<slug>/agents/<slug>-tutor.md
```

For example: `subjects/algorithms/agents/algorithms-tutor.md`.

Wire it into your IDE by referencing the file directly (`@` in Cursor/Claude Code) or by pasting its contents as the system prompt. The tutor is fully self-contained (it includes the topic index, exam patterns and image pointers in its prompt) so you do not need to attach the kb files separately, but doing so makes citations faster and more accurate.

---

## Multiple subjects in one workspace

Open the repository as the workspace root. The root agents in `agents/` apply to the whole workspace (pipeline operations). Each subject's tutor lives under `subjects/<slug>/agents/<slug>-tutor.md`. Reference whichever tutor you need by file path — no nested `.cursor` or `.claude` directories required.

If your IDE does not support file-path references, paste the tutor you currently need into the chat as a system prompt.