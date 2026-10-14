# Reusing source views

Use `scripts/source_cache.py` when another run needs an already inspected source view. The cache imports local bytes; it does not download sources or decide applicability. Keep it outside Git, e.g. under output/source-cache.

```text
python source_cache.py put --root CACHE --file VIEW.png --url SOURCE_URL --model EXACT_MODEL --revision DOCUMENT_EDITION --locator "page 6 figure 2" --applicability "Exact variant and geometry this view supports"
python source_cache.py get --root CACHE --url SOURCE_URL --model EXACT_MODEL --revision DOCUMENT_EDITION --locator "page 6 figure 2"
```

All four identity fields form the cache key. Record an actual revision/access date when the publisher has no edition. Changed bytes/applicability require a new revision or locator, never silently overwrite the key. Assets are stored by SHA256 and verified on read/reuse; writes are locked on macOS/Linux. A found local entry does not establish that the live document remains current. Recheck current source identity and applicability when necessary; do not reuse one model's geometry across a whole brand. Use the returned original file as `archive-evidence --file` for each run to bind its exact view and source IDs. Shared assets are not targets for automatic product cleanup.
