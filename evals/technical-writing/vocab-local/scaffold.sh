#!/usr/bin/env bash
# A British-English repository with its own Vale config and House
# vocabulary. The doc has a real project term (Zellij) and a misspelling.
set -euo pipefail

# The repository provides its own prose check. Resolve the binary now: the
# agent's sandbox may not have it on PATH.
vale_bin="$(command -v vale)" || {
  echo "vale not on PATH; see evals/technical-writing/run.sh" >&2
  exit 1
}

mkdir -p scripts docs .vale/styles/House .vale/styles/config/vocabularies/House \
  .vale/styles/config/dictionaries

# An -ise en_GB Hunspell dictionary, copied in so the run doesn't depend on
# where the machine keeps it.
dict=""
if command -v nix >/dev/null 2>&1; then
  dict="$(nix build --no-link --print-out-paths nixpkgs#hunspellDicts.en_GB-ise)/share/hunspell"
elif [ -f /usr/share/hunspell/en_GB.dic ]; then
  dict=/usr/share/hunspell
fi
[ -n "$dict" ] || { echo "no en_GB Hunspell dictionary found" >&2; exit 1; }
cp -L "$dict/en_GB.aff" "$dict/en_GB.dic" .vale/styles/config/dictionaries/

cat > scripts/lint-prose <<SH
#!/usr/bin/env bash
# Prose and spelling check (advisory): scripts/lint-prose FILE...
exec "$vale_bin" --output=line "\$@"
SH
chmod +x scripts/lint-prose

cat > CONTRIBUTING.md <<'MD'
# Contributing

Check prose and spelling in docs you change with `scripts/lint-prose FILE`.
MD

cat > .vale.ini <<'INI'
StylesPath = .vale/styles
Vocab = House

[*.md]
BasedOnStyles = House
Vale.Spelling = NO
INI

cat > .vale/styles/House/Spelling.yml <<'YAML'
extends: spelling
message: "'%s' isn't in the British English dictionary or the House vocabulary."
level: error
dictionaries:
  - en_GB
YAML

cat > .vale/styles/config/vocabularies/House/accept.txt <<'TXT'
(?i)dotfiles
Neovim
WezTerm
TXT

cat > docs/terminal.md <<'MD'
# Terminal

We use WezTerm with Zellij for panes and sessions. Open Neovim in a new
pane, and you will recieve a prompt to restore the last session.
MD

git init -q
git add -A
git -c user.name=Fixture -c user.email=fixture@example.com commit -qm "Initial commit"
