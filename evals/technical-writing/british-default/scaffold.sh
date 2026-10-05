#!/usr/bin/env bash
# No style guide and no Vale config. The doc uses American spellings in
# prose, and one in code that must stay as it is.
set -euo pipefail

mkdir -p docs
cat > docs/themes.md <<'MD'
# Themes

You can organize your themes by color. Each theme changes the behavior of
the editor and the color of the status bar.

To customize a theme, set its color in `theme.json`:

```json
{ "color": "blue" }
```
MD

git init -q
git add -A
git -c user.name=Fixture -c user.email=fixture@example.com commit -qm "Initial commit"
