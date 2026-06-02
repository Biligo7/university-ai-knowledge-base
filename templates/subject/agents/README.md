# {{SUBJECT_NAME}} — agents

Subject-specific agents live here. After the pipeline finishes, you will find:

| File | Role |
|---|---|
| `{{SUBJECT_SLUG}}-tutor.md` | The per-subject tutor. Authored by the root-level `tutor-generator` agent. Knows the topic index, the file layout, and when to open which image. |

You can add more subject-scoped agents here over time (for example a *flashcard generator* or an *exam-mode quizzer*). Keep them limited to material under `{{SUBJECT_SLUG}}/kb/` and `{{SUBJECT_SLUG}}/assets/` so they remain useful for this subject only.

See [`../../../docs/ide-integration.md`](../../../docs/ide-integration.md) for how to wire any of these agent files into your AI assistant.
