# Data Directory

Runtime SQLite databases and caches are written here when users choose a project-local data directory.

The default database filename is:

```text
fashion-radar.sqlite
```

SQLite may also create sidecar files such as `fashion-radar.sqlite-wal` and
`fashion-radar.sqlite-shm`.

Generated data is ignored by git. Do not commit local databases, sidecars,
source caches, account/session files, cookies, or private exports.

Use `fashion-radar clean-old-data` to prune old collected items and their
matched entity rows. See `docs/data-retention.md` for the retention behavior,
including why stable `entity_first_seen` rows are not pruned.
