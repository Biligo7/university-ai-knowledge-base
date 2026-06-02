# {{SUBJECT_NAME}} — assets

Extracted images, organised by source PDF. Layout:

```
assets/
├── <pdf-name>/
│   ├── p001-i01.png
│   ├── p007-i02.jpg
│   └── ...
└── <another-pdf-name>/
    └── ...
```

The folder name matches the slugified PDF filename. Within each folder, files are named `p<page>-i<index>.<ext>` so that the location in the original PDF is obvious at a glance.

## Lifecycle

1. `tools/pdf_to_md.py` extracts every embedded image, dropping the obviously mechanical ones (tiny, repeated across pages).
2. `tools/filter_images.py --apply` removes images that are smaller than the byte threshold or that repeat across many decks.
3. The `image-curator` agent then reviews every remaining image with vision and deletes the ones that carry no pedagogical value (logos, portraits, decorative screenshots). It also strips the corresponding `![...](...)` lines from the Markdown.

Anything left in here after step 3 is intentional — feel free to delete more by hand, but the kb Markdown references may break.
