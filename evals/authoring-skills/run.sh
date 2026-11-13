#!/usr/bin/env bash
# Run local evals with the maintainer's existing Claude subscription.
set -euo pipefail
cd "$(dirname "$0")/../.."
exec claude plugin eval . --tag authoring-skills \
  --scaffold --trust-plugin --no-publish --allow-tools Bash Edit Write "$@"
