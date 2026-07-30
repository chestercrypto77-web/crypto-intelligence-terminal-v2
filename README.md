# Crypto Intelligence Terminal V2 — Release 2.1.2

This complete release fixes the Morning Brief crash and dark-theme readability.

## Fixes

### Morning Brief crash

The portfolio profile uses readable conviction labels such as `Core`, `High`
and `Medium`. The attention engine previously attempted to convert those words
directly to a number, causing:

`ValueError: could not convert string to float`

The engine now safely maps conviction labels to numeric scores and also supports
an explicit `conviction_score` field.

### Dark navigation readability

The permanent dark background was working, but Streamlit retained low-opacity
navigation text. Release 2.1.2 explicitly restores readable colours and opacity
for:

- sidebar page names
- sidebar section headings
- selected navigation item
- metrics
- captions
- expanders and alerts

## Deployment

Extract the ZIP and upload everything inside the extracted folder into the root
of the GitHub repository, replacing the existing files.
