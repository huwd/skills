#!/usr/bin/env bats
# check-shell-blocks.py: shellchecks fenced shell blocks in Markdown and
# reports findings against the Markdown file's own lines. Runs the real
# linter, which works offline.

load helper

setup() {
  setup_repo
  check="$BATS_TEST_DIRNAME/../check-shell-blocks.py"
}

@test "passes clean blocks, including <PLACEHOLDER> arguments" {
  cat > doc.md <<'MD'
# Doc

```bash
gh pr view <NUMBER> --repo <OWNER/REPO>
cat < input.txt
```
MD
  run "$check" doc.md
  [ "$status" -eq 0 ]
  [ -z "$output" ]
}

@test "reports a finding at the Markdown line and column" {
  cat > doc.md <<'MD'
# Doc

Some text.

```bash
echo ok
rm -rf $dir/*
```
MD
  run "$check" doc.md
  [ "$status" -eq 1 ]
  [[ "$output" == *"doc.md:7:8:"*"SC2115"* ]]
}

@test "adds the indent to the column for blocks inside lists" {
  cat > doc.md <<'MD'
1. Step

   ```sh
   cd $HOME/x
   ```
MD
  run "$check" doc.md
  [ "$status" -eq 1 ]
  [[ "$output" == *"doc.md:4:4:"*"SC2164"* ]]
}

@test "checks bash, sh and shell blocks, and ignores other languages" {
  cat > doc.md <<'MD'
```text
rm -rf $dir/*
```

```python
x = $y
```

```shell
cd $HOME/x
```
MD
  run "$check" doc.md
  [ "$status" -eq 1 ]
  [[ "$output" == *"doc.md:10:"* ]]
  [[ "$output" != *"doc.md:2:"* ]]
  [[ "$output" != *"doc.md:6:"* ]]
}

@test "checks every file given" {
  cat > clean.md <<'MD'
```bash
echo ok
```
MD
  cat > dirty.md <<'MD'
```bash
cd $HOME/x
```
MD
  run "$check" clean.md dirty.md
  [ "$status" -eq 1 ]
  [[ "$output" == *"dirty.md:2:"* ]]
  [[ "$output" != *"clean.md"* ]]
}
