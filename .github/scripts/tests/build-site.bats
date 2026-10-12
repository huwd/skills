#!/usr/bin/env bats
# build-site.py: writes index.json for a directory of versioned bundles,
# oldest first, so agent-manager's "last entry is latest" holds.

load helper

setup() {
  setup_repo
  site="$BATS_TEST_TMPDIR/site"
  index="$BATS_TEST_DIRNAME/../build-site.py"
}

# bundle VERSION [MANIFEST_VERSION]: a minimal versioned bundle.
bundle() {
  mkdir -p "$site/$1"
  python3 - "$site/$1/bundle.zip" "${2:-$1}" <<'PY'
import json, sys, zipfile
with zipfile.ZipFile(sys.argv[1], "w") as z:
    z.writestr("manifest.json", json.dumps({"version": sys.argv[2], "published": "2026-10-12T00:00:00Z"}))
PY
  (cd "$site/$1" && sha256sum bundle.zip > bundle.zip.sha256)
}

versions() {
  python3 -c 'import json, sys; print(" ".join(v["version"] for v in json.load(open(sys.argv[1]))["agents"]))' "$site/index.json"
}

@test "lists versions in semantic order, latest last" {
  bundle 0.10.0
  bundle 0.9.0
  bundle 0.10.0-rc.1
  bundle 1.0.0
  run "$index" "$site"
  [ "$status" -eq 0 ]
  [ "$(versions)" = "0.9.0 0.10.0-rc.1 0.10.0 1.0.0" ]
}

@test "writes no discovery document" {
  bundle 1.0.0
  "$index" "$site"
  [ ! -e "$site/.well-known" ]
}

@test "fails when a bundle's manifest names a different version" {
  bundle 1.0.0 2.0.0
  run "$index" "$site"
  [ "$status" -eq 1 ]
  [[ "$output" == *"says version '2.0.0'"* ]]
}

@test "fails when a checksum is missing" {
  bundle 1.0.0
  rm "$site/1.0.0/bundle.zip.sha256"
  run "$index" "$site"
  [ "$status" -eq 1 ]
  [[ "$output" == *"missing bundle.zip.sha256"* ]]
}

@test "fails when there are no bundles" {
  mkdir -p "$site"
  run "$index" "$site"
  [ "$status" -eq 1 ]
  [[ "$output" == *"No bundles found"* ]]
}
