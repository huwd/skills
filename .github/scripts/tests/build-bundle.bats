#!/usr/bin/env bats
# build-bundle.py: zips every tracked skill, plus a manifest, into
# OUT/VERSION/bundle.zip with a sha256 sidecar, reproducibly.

load helper

setup() {
  setup_repo
  build="$BATS_TEST_DIRNAME/../build-bundle.py"
  add_skill alpha
  add_skill beta
  mkdir -p skills/alpha/references
  echo "# Notes" > skills/alpha/references/notes.md
  git add -A
  git -c user.name=T -c user.email=t@example.com commit -qm init
}

@test "bundles tracked skill files at the top level, with a manifest" {
  echo "scratch" > skills/alpha/untracked.txt
  run "$build" 1.2.3 out
  [ "$status" -eq 0 ]
  run python3 -c 'import sys, zipfile; print("\n".join(sorted(zipfile.ZipFile(sys.argv[1]).namelist())))' out/1.2.3/bundle.zip
  [ "$output" = "alpha/SKILL.md
alpha/references/notes.md
beta/SKILL.md
manifest.json" ]
}

@test "the manifest records the version and the commit time" {
  "$build" 1.2.3 out
  run python3 -c 'import json, sys, zipfile; m = json.loads(zipfile.ZipFile(sys.argv[1]).read("manifest.json")); print(m["version"], m["published"])' out/1.2.3/bundle.zip
  expected="$(TZ=UTC git log -1 --format=%cd --date=format-local:%Y-%m-%dT%H:%M:%SZ)"
  [ "$output" = "1.2.3 $expected" ]
}

@test "writes a sha256 sidecar that checks out" {
  "$build" 1.2.3 out
  cd out/1.2.3
  run sha256sum --check bundle.zip.sha256
  [ "$status" -eq 0 ]
  [[ "$(cat bundle.zip.sha256)" =~ ^[0-9a-f]{64}\ \ bundle\.zip$ ]]
}

@test "builds the same bytes from the same commit" {
  "$build" 1.2.3 first
  sleep 1
  "$build" 1.2.3 second
  cmp first/1.2.3/bundle.zip second/1.2.3/bundle.zip
}

@test "rejects a version that isn't semantic" {
  run "$build" v1.2 out
  [ "$status" -eq 2 ]
  [[ "$output" == *"Not a semantic version"* ]]
  [ ! -e out ]
}

@test "fails loudly when there are no skills" {
  git rm -rq skills
  git -c user.name=T -c user.email=t@example.com commit -qm empty
  run "$build" 1.2.3 out
  [ "$status" -eq 1 ]
  [[ "$output" == *"No skills found"* ]]
}
