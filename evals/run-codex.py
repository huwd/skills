#!/usr/bin/env python3
"""Run trusted file/command evals with Codex; requires PyYAML and Codex CLI.

Example (run from the repository root, with Vale on PATH):
  python3 evals/run-codex.py --case vocab-local --ref HEAD --ref origin/main \
      --runs 10 --model gpt-6.1-sol --effort medium

Scaffolds execute as the caller. Each run keeps its workspace, JSONL events,
stderr, final response and verdicts. Only regex and Bash/Skill graders are
supported. Skill use is a diagnostic proxy: a successful command reads the
installed SKILL.md and returns its content. It is not a Claude Skill event.
"""

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tarfile
import tempfile
import time

import yaml


def frontmatter(path):
    text = path.read_text()
    parts = text.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError(f"Missing frontmatter: {path}")
    return yaml.safe_load(parts[1]), parts[2].strip()


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def completed_items(events):
    return [e["item"] for e in events if e.get("type") == "item.completed"]


def grade(spec, workspace, events):
    kind = spec["type"]
    items = completed_items(events)
    if kind == "regex":
        target = spec.get("target", {})
        if target.get("source", "response") == "file":
            path = workspace / target["path"]
            if not path.is_file():
                return {"passed": False, "detail": "target file missing"}
            text = path.read_text()
        else:
            text = "\n".join(i["text"] for i in items if i["type"] == "agent_message")
        flags = 0
        for flag in spec.get("flags", ""):
            flags |= {"i": re.I, "m": re.M, "s": re.S}[flag]
        found = re.search(spec["pattern"], text, flags) is not None
        mode = spec.get("match", "contains")
        if mode not in ("contains", "not_contains"):
            raise ValueError(f"Unsupported regex mode: {mode}")
        return {"passed": found if mode == "contains" else not found}
    if kind != "tool_used":
        raise ValueError(f"Unsupported grader: {kind}")
    commands = [i for i in items if i["type"] == "command_execution"]
    tool = spec["tool"]
    if tool == "Bash":
        count = sum(bool(re.search(spec.get("input_match", ".*"), i["command"]))
                    for i in commands)
    elif tool == "Skill":
        # Require returned skill content as well as the path; mentions alone
        # are not evidence that the agent loaded the tested skill.
        skill = workspace / ".agents/skills/technical-writing/SKILL.md"
        content = skill.read_text()
        signature = content[content.index("# Technical Writing"):][:160]
        count = sum(i.get("exit_code") == 0
                    and ".agents/skills/technical-writing/SKILL.md" in i["command"]
                    and signature in i.get("aggregated_output", "") for i in commands)
    else:
        raise ValueError(f"Unsupported tool grader: {tool}")
    return {"passed": spec.get("min", 1) <= count <= spec.get("max", float("inf")),
            "count": count, "diagnostic": tool == "Skill"}


def execute(command, cwd, env, stdout, stderr, timeout, prompt=None):
    with stdout.open("w") as out, stderr.open("w") as err:
        process = subprocess.Popen(command, cwd=cwd, env=env, stdout=out, stderr=err,
                                   stdin=subprocess.PIPE, text=True, start_new_session=True)
        try:
            process.communicate(prompt, timeout=timeout)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            raise
    return process.returncode


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def isolated_config(model, effort):
    lines = [f"model = {json.dumps(model)}",
             f"model_reasoning_effort = {json.dumps(effort)}",
             'approval_policy = "never"', 'sandbox_mode = "workspace-write"',
             "[skills.bundled]", "enabled = false", "[agents]", "enabled = false"]
    # CODEX_HOME isolates config/plugins, but ~/.agents/skills is a separate
    # discovery root. Disable those skills by both their scanned and real paths.
    paths = set()
    for base in (Path.home() / ".agents/skills", Path("/etc/codex/skills")):
        if base.is_dir():
            for path in base.glob("*/SKILL.md"):
                paths.update((str(path), str(path.resolve())))
    for path in sorted(paths):
        lines.extend(("[[skills.config]]", f"path = {json.dumps(path)}", "enabled = false"))
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--case", required=True)
    parser.add_argument("--ref", action="append", required=True)
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--model", required=True)
    parser.add_argument("--effort", default="medium")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs must be positive")
    root = Path(__file__).resolve().parents[1]
    case = root / "evals/technical-writing" / args.case
    if case.parent != root / "evals/technical-writing":
        parser.error("--case must name a direct child of evals/technical-writing")
    prompt_config, prompt = frontmatter(case / "prompt.md")
    graders = {p.stem: frontmatter(p)[0] for p in sorted((case / "graders").glob("*.md"))}
    for name, spec in graders.items():
        if spec["type"] not in ("regex", "tool_used") or (
            spec["type"] == "tool_used" and spec["tool"] not in ("Bash", "Skill")
        ):
            parser.error(f"Unsupported grader {name}: {spec}")
    output = (args.output_dir or root / "evals/results" / time.strftime("codex-%Y%m%dT%H%M%SZ", time.gmtime())).resolve()
    output.mkdir(parents=True, exist_ok=False)
    snapshots = []
    for index, ref in enumerate(args.ref):
        sha = git(root, "rev-parse", f"{ref}^{{commit}}").decode().strip()
        archive = git(root, "archive", sha, "skills/technical-writing")
        dest = output / f"source-{index}"
        dest.mkdir()
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(dest, filter="data")
        snapshots.append({"ref": ref, "sha": sha, "source": str(dest)})
    report = {"harness": "codex", "version": subprocess.check_output(["codex", "--version"], text=True).strip(),
              "model": args.model, "effort": args.effort, "case": args.case,
              "runsPerRef": args.runs, "sources": snapshots,
              "fixtureHashes": {str(p.relative_to(case)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sorted(case.rglob("*")) if p.is_file()},
              "skillUseIsDiagnostic": True, "runs": [], "complete": False}
    write_json(output / "aggregate-result.json", report)
    # Keep the authentication copy outside the retained artifacts, then remove
    # it even when a model run fails. No user config, rules or plugins are copied.
    with tempfile.TemporaryDirectory(prefix="skills-codex-auth-") as private:
        private = Path(private)
        auth = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "auth.json"
        if not auth.is_file():
            parser.error("Saved Codex login required (auth.json was not found)")
        shutil.copyfile(auth, private / "auth.json")
        (private / "auth.json").chmod(0o600)
        (private / "config.toml").write_text(isolated_config(args.model, args.effort))
        # Capture config without credentials so the experiment can be audited.
        shutil.copyfile(private / "config.toml", output / "codex-config.toml")
        env = dict(os.environ, CODEX_HOME=str(private), GIT_CONFIG_COUNT="1",
                   GIT_CONFIG_KEY_0="commit.gpgsign", GIT_CONFIG_VALUE_0="false")
        for number in range(1, args.runs + 1):
            # Alternate which ref starts each pair, reducing ordering effects.
            order = list(enumerate(snapshots))
            if number % 2 == 0:
                order.reverse()
            for index, source in order:
                run_dir = output / f"ref-{index}-run-{number:02}"
                workspace = run_dir / "workspace"
                workspace.mkdir(parents=True)
                print(f"{source['ref']} run {number}/{args.runs}: {run_dir}", flush=True)
                record = {"ref": source["ref"], "sha": source["sha"], "number": number,
                          "directory": str(run_dir), "error": None}
                started = time.monotonic()
                try:
                    scaffold_code = execute(["bash", str(case / "scaffold.sh")], workspace, env,
                                            run_dir / "scaffold.stdout", run_dir / "scaffold.stderr", 120)
                    if scaffold_code:
                        raise RuntimeError(f"Scaffold exited {scaffold_code}; see scaffold.stderr")
                    skill = workspace / ".agents/skills/technical-writing"
                    skill.parent.mkdir(parents=True)
                    shutil.copytree(Path(source["source"]) / "skills/technical-writing", skill)
                    command = ["codex", "exec", "--json", "--ephemeral", "--ignore-rules",
                               "--sandbox", "workspace-write", "--color", "never",
                               "--cd", str(workspace), "--output-last-message", str(run_dir / "response.txt"), "-"]
                    (run_dir / "prompt.txt").write_text(prompt + "\n")
                    write_json(run_dir / "command.json", command)
                    code = execute(command, workspace, env, run_dir / "events.jsonl", run_dir / "stderr.log",
                                   prompt_config.get("timeout_seconds", 600), prompt)
                    events = [json.loads(line) for line in (run_dir / "events.jsonl").read_text().splitlines() if line.strip()]
                    if code or any(e["type"] in ("error", "turn.failed") for e in events):
                        raise RuntimeError(f"Codex run failed (exit {code}); see events.jsonl and stderr.log")
                    if not any(e["type"] == "turn.completed" for e in events):
                        raise RuntimeError("No completed turn in Codex transcript")
                    record["graders"] = {name: grade(spec, workspace, events) for name, spec in graders.items()}
                    scored = [v for v in record["graders"].values() if not v.get("diagnostic")]
                    record["score"] = sum(v["passed"] for v in scored) / len(scored)
                    record["passed"] = all(v["passed"] for v in record["graders"].values())
                    record["usage"] = [e.get("usage") for e in events if e["type"] == "turn.completed"]
                except (RuntimeError, subprocess.TimeoutExpired) as exc:
                    record["error"] = str(exc)
                record["seconds"] = round(time.monotonic() - started, 2)
                report["runs"].append(record)
                write_json(run_dir / "result.json", record)
                write_json(output / "aggregate-result.json", report)
                if record["error"]:
                    print(record["error"], flush=True)
                    return 2  # Auth, quota, sandbox and runtime errors stop the batch.
                failed = [k for k, v in record["graders"].items() if not v["passed"]]
                print(f"score {record['score']:.3f}; failed: {failed}", flush=True)
    report["complete"] = True
    write_json(output / "aggregate-result.json", report)
    print(f"Results: {output}")
    return int(any(not r["passed"] for r in report["runs"]))


if __name__ == "__main__":
    raise SystemExit(main())
