# Reports Directory

Generated Markdown and JSON reports are written here when users choose a project-local reports directory.

Report files use this naming pattern:

```text
fashion-radar-YYYY-MM-DD.md
fashion-radar-YYYY-MM-DD.json
```

Optional local digest artifacts use these names:

```text
latest.md
latest.json
report-index.json
fashion-radar-YYYY-MM-DD.eml
```

Generated reports and digest artifacts are ignored by git. They contain source
attribution, links, snippets/metadata, matched entities, and score components.
Review reports before sharing them publicly, especially if your configured
sources include private or internal feeds.

`row-one refresh` keeps the ROW ONE local presentation path latest-only by
pruning older generated dated report artifacts in this directory that match
`fashion-radar-YYYY-MM-DD.md`, `fashion-radar-YYYY-MM-DD.json`, and
`fashion-radar-YYYY-MM-DD.html`. This is local report artifact retention only;
it does not prune SQLite data, collected items, matcher rows, source config,
connectors, `.eml` digest artifacts, report indexes, latest digest files, or
non-report files.
