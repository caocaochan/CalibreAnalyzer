# Chinese Character Analyzer for Calibre

Calibre plugin for analyzing Chinese books by character or word, with HSK
coverage and optional Anki comparison.

## Releases

Every push to `main` publishes a GitHub release automatically.

Release versions use the format:

`YYYY.MM.DD.X`

- `YYYY.MM.DD` is the UTC release date
- `X` is the incrementing release number for that date

## Development

The plugin bundles platform-specific word-mode runtimes in `runtime_assets/`.
Those archives are extracted on first use of Word mode so end users do not need
an external download.
