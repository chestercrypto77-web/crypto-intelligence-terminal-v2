# Crypto Intelligence Terminal V2 — Release 2.1.3

Release 2.1.3 fixes the remaining Morning Brief crash and improves visual
separation across the complete terminal.

## Crash fix

The Personal Intelligence service has been fully rewritten around defensive
numeric conversion. It now safely handles:

- `None` values from live APIs
- missing price and percentage fields
- malformed numeric strings
- readable conviction labels such as Core, High and Medium
- incomplete scanner and conviction records

A single missing API field can no longer crash the Morning Brief.

## Navigation readability

The sidebar now uses:

- brighter page names
- stronger font weight
- a clearly highlighted selected page
- blue navigation section headings
- higher contrast against the dark sidebar

## Page colour hierarchy

Across all pages:

- page titles remain off-white
- major section headings are blue
- smaller headings are amber
- collapsed technical sections are green
- labels and supporting copy remain softer grey

This provides clear separation without turning the terminal into a brightly
coloured dashboard.

## Deployment

This is a complete release. Extract it and upload everything inside the
extracted folder into the root of the GitHub repository, replacing existing
files.
