#!/usr/bin/env python3
"""Run trusted file/command evals with Codex; requires PyYAML and Codex CLI.

Example (run from the repository root, with Vale on PATH):
  python3 evals/run-codex.py --case vocab-local --ref HEAD --ref origin/main \
      --runs 10 --model gpt-6.1-sol --effort medium

Scaffolds execute as the caller. Each run keeps its workspace, JSONL events,
stderr, final response and verdicts. Regex, Bash/Skill and trusted local
Python script graders are supported. Skill use is a diagnostic proxy: a successful command reads the
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
import sys
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


def grade(spec, workspace, events, skill_name="technical-writing", grader_dir=None):
    kind = spec["type"]
    items = completed_items(events)
    if kind == "script":
        if grader_dir is None:
            raise ValueError("Script graders need their source directory")
        script = (grader_dir / spec["script"]).resolve()
        try:
            result = subprocess.run(
                [sys.executable, str(script), str(workspace), spec["check"]],
                input=json.dumps(events), text=True, capture_output=True,
                timeout=30, check=True)
            verdict = json.loads(result.stdout)
            if not isinstance(verdict, dict) or type(verdict.get("passed")) is not bool:
                raise ValueError("expected a boolean passed field")
            return verdict
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            raise RuntimeError(f"Local assessor failed: {script}: {exc}") from exc
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
        relative = f".agents/skills/{skill_name}/SKILL.md"
        skill = workspace / relative
        count = 0
        if skill.is_file():
            content = skill.read_text()
            signature = content[content.index("# "):][:160]
            count = sum(i.get("exit_code") == 0
                        and relative in i["command"]
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


def case_env(env, case, requirements):
    """Put a suite's trusted stub directories, such as a fake `gh`, first on PATH.

    Entries are relative to the case and must stay inside its suite.
    """
    stubs = []
    for entry in requirements.get("path_prepend", []):
        path = (case / entry).resolve()
        if not path.is_relative_to(case.parent.resolve()):
            raise ValueError(f"path_prepend entry must stay inside the suite: {entry}")
        if not path.is_dir():
            raise ValueError(f"path_prepend entry is not a directory: {entry}")
        stubs.append(str(path))
    if not stubs:
        return env
    return dict(env, PATH=":".join(stubs + [env.get("PATH", "")]))


def isolated_config(model, effort, fixture_git=False):
    lines = [f"model = {json.dumps(model)}",
             f"model_reasoning_effort = {json.dumps(effort)}",
             'approval_policy = "never"']
    if fixture_git:
        lines += ['default_permissions = "fixture-git"',
                  '[permissions.fixture-git]', 'extends = ":workspace"',
                  '[permissions.fixture-git.filesystem.":workspace_roots"]',
                  '".git" = "write"', '[permissions.fixture-git.network]', 'enabled = false']
    else:
        lines += ['sandbox_mode = "workspace-write"']
    lines += ["[skills.bundled]", "enabled = false", "[agents]", "enabled = false"]
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
    parser.add_argument("--suite", default="technical-writing")
    parser.add_argument("--skill", help="Skill to install (defaults to the suite name)")
    parser.add_argument("--allow-fixture-git", action="store_true",
                        help="Allow writes to the disposable workspace's .git; never the source checkout")
    parser.add_argument("--ref", action="append", required=True)
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--model", required=True)
    parser.add_argument("--effort", default="medium")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs must be positive")
    skill_name = args.skill or args.suite
    if any(not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value)
           for value in (args.suite, skill_name, args.case)):
        parser.error("suite, skill and case must be lowercase hyphenated names")
    root = Path(__file__).resolve().parents[1]
    suite = root / "evals" / args.suite
    case = suite / args.case
    manifest = case / "codex-case.yaml"
    requirements = {}
    if manifest.exists():
        requirements = yaml.safe_load(manifest.read_text())
        if requirements.get("requires_fixture_git") and not args.allow_fixture_git:
            parser.error("This case requires --allow-fixture-git for its disposable repository")
    prompt_path = case / "prompt.md"
    if not prompt_path.exists():
        prompt_path = case / "task.md"
    prompt_config, prompt = frontmatter(prompt_path)
    graders = {p.stem: frontmatter(p)[0] for p in sorted((case / "graders").glob("*.md"))}
    for name, spec in graders.items():
        if spec["type"] not in ("regex", "tool_used", "script") or (
            spec["type"] == "tool_used" and spec["tool"] not in ("Bash", "Skill")
        ):
            parser.error(f"Unsupported grader {name}: {spec}")
    output = (args.output_dir or root / "evals/results" / time.strftime("codex-%Y%m%dT%H%M%SZ", time.gmtime())).resolve()
    output.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(__file__, output / "runner.py")
    shutil.copytree(suite, output / "suite", ignore=shutil.ignore_patterns("__pycache__"))
    case = output / "suite" / args.case
    snapshots = []
    for index, ref in enumerate(args.ref):
        if ref == "none":
            snapshots.append({"ref": ref, "sha": None, "source": None})
            continue
        sha = git(root, "rev-parse", f"{ref}^{{commit}}").decode().strip()
        archive = git(root, "archive", sha, f"skills/{skill_name}")
        dest = output / f"source-{index}"
        dest.mkdir()
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(dest, filter="data")
        snapshots.append({"ref": ref, "sha": sha, "source": str(dest)})
    report = {"harness": "codex", "version": subprocess.check_output(["codex", "--version"], text=True).strip(),
              "model": args.model, "effort": args.effort, "case": args.case,
              "suite": args.suite, "skill": skill_name,
              "fixtureGitWritable": args.allow_fixture_git,
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
        (private / "config.toml").write_text(isolated_config(args.model, args.effort, args.allow_fixture_git))
        # Capture config without credentials so the experiment can be audited.
        shutil.copyfile(private / "config.toml", output / "codex-config.toml")
        env = dict(os.environ, CODEX_HOME=str(private), GIT_CONFIG_COUNT="1",
                   GIT_CONFIG_KEY_0="commit.gpgsign", GIT_CONFIG_VALUE_0="false")
        try:
            env = case_env(env, case, requirements)
        except ValueError as exc:
            parser.error(str(exc))
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
                    if source["source"] is not None:
                        skill = workspace / f".agents/skills/{skill_name}"
                        skill.parent.mkdir(parents=True)
                        shutil.copytree(Path(source["source"]) / f"skills/{skill_name}", skill)
                    command = ["codex", "exec", "--json", "--ephemeral", "--ignore-rules",
                               "--color", "never",
                               "--cd", str(workspace), "--output-last-message", str(run_dir / "response.txt"), "-"]
                    if not args.allow_fixture_git:
                        command[2:2] = ["--sandbox", "workspace-write"]
                    (run_dir / "prompt.txt").write_text(prompt + "\n")
                    write_json(run_dir / "command.json", command)
                    code = execute(command, workspace, env, run_dir / "events.jsonl", run_dir / "stderr.log",
                                   prompt_config.get("timeout_seconds", 600), prompt)
                    events = [json.loads(line) for line in (run_dir / "events.jsonl").read_text().splitlines() if line.strip()]
                    if code or any(e["type"] in ("error", "turn.failed") for e in events):
                        raise RuntimeError(f"Codex run failed (exit {code}); see events.jsonl and stderr.log")
                    if not any(e["type"] == "turn.completed" for e in events):
                        raise RuntimeError("No completed turn in Codex transcript")
                    record["graders"] = {}
                    for name, spec in graders.items():
                        if (source["source"] is None and spec.get("tool") == "Skill"
                                and spec.get("min", 1) > 0):
                            continue  # Positive selection has no meaning in the no-skill arm.
                        record["graders"][name] = grade(
                            spec, workspace, events, skill_name, case / "graders")
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
