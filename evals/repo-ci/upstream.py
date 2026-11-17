"""Synthetic upstream releases shared by the gh stub, fixtures and assessor.

Commit IDs are derived from names, so no real action's commit appears here.
A pin recalled from memory, or copied from a real repository, therefore
cannot match. Release dates are relative to the time of the run, so a
release inside a seven-day cooldown stays recent whenever the suite runs.
"""

from datetime import datetime, timedelta, timezone
import hashlib

# repository -> [(tag, days before the run)], oldest first
RELEASES = {
    "actions/checkout": [("v6.0.0", 300), ("v7.0.0", 140), ("v7.0.1", 62), ("v7.0.2", 3)],
    "actions/setup-python": [("v6.0.0", 250), ("v6.1.0", 88)],
    "astral-sh/setup-uv": [("v10.2.0", 107), ("v10.3.0", 45)],
    "acme-org/shared-workflows": [("v2.0.0", 160), ("v2.1.0", 27)],
    "github/gh-actions-lock": [("v0.3.0", 25), ("v0.4.0", 24), ("v0.4.1", 14)],
}
IDS = {name: (1000 + index * 7, 50000 + index * 11) for index, name in enumerate(sorted(RELEASES))}


def sha(repo, tag):
    return hashlib.sha1(f"synthetic:{repo}@{tag}".encode()).hexdigest()


def published(days):
    moment = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(days=days)
    return moment.isoformat().replace("+00:00", "Z")


def tags(repo):
    """Every tag, including floating major tags, mapped to its commit."""
    result = {tag: sha(repo, tag) for tag, _ in RELEASES[repo]}
    for tag, _ in RELEASES[repo]:  # oldest first, so the newest release wins
        result[tag.split(".")[0]] = sha(repo, tag)
    return result


def latest(repo):
    return RELEASES[repo][-1][0]


def tag_for(repo, commit):
    """The full release tag whose commit this is, or None."""
    return next((tag for tag, _ in RELEASES.get(repo, []) if sha(repo, tag) == commit), None)
