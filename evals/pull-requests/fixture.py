"""Build synthetic repositories with feature branches ready for a pull request.

Every case starts from the same small Python package, `ledger`. Branches add
work of different shapes: a small fix, a small core change buried in
mechanical and generated changes, and a large set of independent features.
The snapshot records refs and the size of the core change for the assessor.
"""

import hashlib
import json
from decimal import Decimal
from pathlib import Path
import subprocess
import sys

MODULES = ["invoice", "tax", "discount", "refund", "payroll", "ledger_entry", "budget", "forecast",
           "expense", "receipt", "statement", "credit", "debit", "transfer", "deposit", "withdrawal",
           "fee", "interest", "loan", "subscription", "shipping", "commission", "rebate", "voucher"]
CORE_FILES = ["src/ledger/rounding.py", "src/ledger/money.py", "src/ledger/invoice.py", "tests/test_rounding.py"]


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def write(root, name, text, executable=False):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    if executable:
        path.chmod(0o755)


def commit(root, message):
    git(root, "add", "-A")
    git(root, "commit", "-qm", message)


AGENTS = """# Repository instructions

Branches are named <type>/<short-description> and use Conventional Commits.
Run scripts/check before opening a pull request; it is required.
Pull requests are squash-merged into main.
"""

CHECK = """#!/usr/bin/env python3
import subprocess
import sys
raise SystemExit(subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-t', '.']).returncode)
"""

MONEY = '''"""Money values held as exact decimals."""
from decimal import Decimal


class Amount:
    def __init__(self, value):
        self.value = Decimal(str(value))

    @classmethod
    def zero(cls):
        return cls(0)

    def __add__(self, other):
        return Amount(self.value + other.value)

    def __sub__(self, other):
        return Amount(self.value - other.value)

    def scale(self, factor):
        return Amount(self.value * Decimal(str(factor)))

    def __eq__(self, other):
        return isinstance(other, Amount) and self.value == other.value

    def __repr__(self):
        return f"Amount({self.value})"
'''


def module(name, wrapped=True):
    title = name.replace("_", " ")
    call = ("    return total.scale(\n        rate\n    )\n" if wrapped else "    return total.scale(rate)\n")
    return f'''"""{title.capitalize()} calculations."""
from ledger.money import Amount


def {name}_total(items: list[Amount]) -> Amount:
    total = Amount.zero()
    for item in items:
        total = total + item
    return total


def {name}_difference(first: Amount, second: Amount) -> Amount:
    return first - second


def {name}_scaled(items: list[Amount], rate) -> Amount:
    total = {name}_total(items)
{call}

def {name}_largest(items: list[Amount]) -> Amount:
    best = Amount.zero()
    for item in items:
        if item.value > best.value:
            best = item
    return best


def {name}_is_zero(value: Amount) -> bool:
    return value == Amount.zero()
'''


def lockfile(generation):
    lines = ["version = 1", 'requires-python = ">=3.11"', ""]
    for index in range(400):
        version = f"{1 + index % 7}.{index % 13}.{generation + index % 5}"
        digest = hashlib.sha256(f"pkg{index}-{version}".encode()).hexdigest()
        lines += ["[[package]]", f'name = "dependency-{index:03d}"', f'version = "{version}"',
                  'source = { registry = "https://pypi.org/simple" }',
                  f'sdist = {{ url = "https://files.example.invalid/dependency-{index:03d}-{version}.tar.gz", '
                  f'hash = "sha256:{digest}" }}', ""]
    return "\n".join(lines)


def base(root):
    write(root, "pyproject.toml", '[project]\nname = "ledger"\nversion = "0.3.0"\n'
          'requires-python = ">=3.11"\n\n[tool.ruff]\nline-length = 88\n')
    write(root, "README.md", "# ledger\n\nSmall accounting helpers.\n")
    write(root, "src/ledger/__init__.py", "")
    write(root, "src/ledger/money.py", MONEY)
    for name in MODULES:
        write(root, f"src/ledger/{name}.py", module(name))
    write(root, "uv.lock", lockfile(0))
    write(root, "tests/__init__.py", "")
    write(root, "tests/test_money.py", "import sys\nimport unittest\nsys.path.insert(0, 'src')\n"
          "from ledger.money import Amount\nfrom ledger.invoice import invoice_total\n\n\n"
          "class MoneyTests(unittest.TestCase):\n    def test_total(self):\n"
          "        self.assertEqual(invoice_total([Amount('1.10'), Amount('2.20')]), Amount('3.30'))\n")
    commit(root, "feat: add ledger package")


def rename(root):
    for path in [root / "src/ledger/money.py", root / "tests/test_money.py",
                 *[root / f"src/ledger/{name}.py" for name in MODULES]]:
        path.write_text(path.read_text().replace("Amount", "Money"))
    commit(root, "refactor: rename Amount to Money\n\nMechanical rename across the package, generated with:\n\n"
           "    sed -i 's/\\bAmount\\b/Money/g' src/ledger/*.py tests/*.py\n\nNo behaviour change.")


def relock(root):
    write(root, "uv.lock", lockfile(1))
    commit(root, "build: refresh uv.lock\n\nRegenerated with `uv lock --upgrade`.")


def reformat(root):
    text = (root / "pyproject.toml").read_text()
    write(root, "pyproject.toml", text.replace("line-length = 88", "line-length = 100"))
    for name in MODULES:
        path = root / f"src/ledger/{name}.py"
        path.write_text(path.read_text().replace("    return total.scale(\n        rate\n    )\n",
                                                 "    return total.scale(rate)\n"))
    commit(root, "style: raise line length to 100 and reformat\n\nReformatted with `ruff format`.")


ROUNDING = '''"""Rounding rules for money values."""
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal

PLACES = Decimal("0.01")
MODES = {"bankers": ROUND_HALF_EVEN, "commercial": ROUND_HALF_UP}


def round_value(value: Decimal, mode: str = "bankers") -> Decimal:
    """Round to whole pence. Banker's rounding sends halves to the even digit."""
    try:
        rounding = MODES[mode]
    except KeyError:
        raise ValueError(f"unknown rounding mode: {mode}") from None
    return value.quantize(PLACES, rounding=rounding)


def round_lines(values: list[Decimal], mode: str = "bankers") -> list[Decimal]:
    """Round each line separately, as printed on an invoice."""
    return [round_value(value, mode) for value in values]


def rounding_error(values: list[Decimal], mode: str = "bankers") -> Decimal:
    """Difference between the rounded total and the total of rounded lines."""
    exact = round_value(sum(values, Decimal(0)), mode)
    return exact - sum(round_lines(values, mode), Decimal(0))
'''

ROUNDING_TESTS = '''import sys
import unittest
from decimal import Decimal
sys.path.insert(0, 'src')
from ledger.money import Money
from ledger.invoice import invoice_total
from ledger.rounding import round_value, rounding_error


class RoundingTests(unittest.TestCase):
    def test_halves_go_to_even(self):
        self.assertEqual(round_value(Decimal("0.125")), Decimal("0.12"))
        self.assertEqual(round_value(Decimal("0.135")), Decimal("0.14"))

    def test_commercial_mode_rounds_halves_up(self):
        self.assertEqual(round_value(Decimal("0.125"), "commercial"), Decimal("0.13"))

    def test_unknown_mode_is_rejected(self):
        with self.assertRaises(ValueError):
            round_value(Decimal("1"), "nearest")

    def test_rounding_error_is_reported(self):
        self.assertEqual(rounding_error([Decimal("0.005")] * 3), Decimal("0.02"))

    def test_invoice_total_is_rounded(self):
        self.assertEqual(invoice_total([Money("0.125"), Money("0.010")]), Money("0.14"))
'''


def rounding(root):
    write(root, "src/ledger/rounding.py", ROUNDING)
    money = (root / "src/ledger/money.py").read_text()
    money = money.replace('from decimal import Decimal\n',
                          'from decimal import Decimal\n\nfrom ledger.rounding import round_value\n')
    money = money.replace("    def scale(self, factor):",
                          "    def rounded(self, mode=\"bankers\"):\n"
                          "        return Money(round_value(self.value, mode))\n\n"
                          "    def scale(self, factor):")
    write(root, "src/ledger/money.py", money)
    invoice = (root / "src/ledger/invoice.py").read_text()
    write(root, "src/ledger/invoice.py", invoice.replace(
        "        total = total + item\n    return total\n\n\ndef invoice_difference",
        "        total = total + item\n    return total.rounded()\n\n\ndef invoice_difference", 1))
    write(root, "tests/test_rounding.py", ROUNDING_TESTS)
    commit(root, "feat: round invoice totals with banker's rounding\n\n"
           "Invoice totals now round to whole pence, sending halves to the even\n"
           "digit, so totals change for amounts ending in exactly half a penny.")


STEPS = [
    lambda p: [f"    if value < Decimal('-{p}'):", f"        raise ValueError('value below -{p}')"],
    lambda p: [f"    value = value * Decimal('1.{p:02d}')"],
    lambda p: [f"    value = value + Decimal('0.{p:02d}')"],
    lambda p: [f"    value = max(value - Decimal('{p % 9 + 1}'), Decimal(0))"],
    lambda p: [f"    if value > Decimal('{p + 20}'):", f"        value = Decimal('{p + 20}')"],
    lambda p: ["    value = value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)"],
    lambda p: ["    value = value.quantize(Decimal('0.1'), rounding=ROUND_DOWN)"],
    lambda p: ["    if value == 0:", f"        return Decimal('{p % 7 + 1}')"],
    lambda p: [f"    value = value / Decimal('{p % 5 + 2}')"],
    lambda p: ["    if int(value) % 2 == 0:", "        value = value + Decimal('0.5')"],
    lambda p: ["    if value < 1:", "        value = value * value"],
    lambda p: [f"    for _ in range({p % 3 + 1}):", f"        value = value - value / Decimal('{p % 4 + 10}')"],
]
VERBS = ["adjust", "normalise", "cap", "convert", "weight", "settle", "align", "reconcile"]


def generated_feature(root, name, title, count):
    """Write a module whose functions each combine a different sequence of steps."""
    body = [f'"""{title}."""', "from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal", ""]
    state = sum(map(ord, name))
    for index in range(count):
        steps = []
        for _ in range(4 + index % 3):
            state = (state * 1103515245 + 12345) % 2**31
            steps += STEPS[state % len(STEPS)](state % 97)
        body += ["", "", f"def {name}_{VERBS[index % len(VERBS)]}_{index:02d}(value: Decimal) -> Decimal:",
                 f'    """{title}: step {index}."""', *steps, "    return value"]
    source = "\n".join(body) + "\n"
    namespace = {}
    exec(compile(source, name, "exec"), namespace)
    tests = ["import sys", "import unittest", "from decimal import Decimal", "sys.path.insert(0, 'src')",
             f"from ledger import {name}", "", "", f"class {name.title().replace('_', '')}Tests(unittest.TestCase):"]
    for index in range(count):
        function = f"{name}_{VERBS[index % len(VERBS)]}_{index:02d}"
        expected = namespace[function](Decimal("7.35"))
        tests += [f"    def test_{function}(self):",
                  f"        self.assertEqual({name}.{function}(Decimal('7.35')), Decimal('{expected}'))", ""]
    write(root, f"src/ledger/{name}.py", source)
    write(root, f"tests/test_{name}.py", "\n".join(tests) + "\n")


def oversized(root):
    for name, title, kind in [("export_csv", "CSV export of ledger entries", "export entries as CSV"),
                              ("fx", "Currency conversion", "convert between currencies"),
                              ("audit", "Audit log of ledger changes", "record an audit log")]:
        generated_feature(root, name, title, 38)
        commit(root, f"feat: {kind}")


def small_fix(root):
    path = root / "src/ledger/tax.py"
    path.write_text(path.read_text().replace(
        "        if item.value > best.value:", "        if item.value >= best.value and item.value != 0:"))
    with (root / "tests/test_money.py").open("a") as tests:
        tests.write("\n    def test_tax_largest_ignores_zero(self):\n"
                    "        from ledger.tax import tax_largest\n"
                    "        self.assertEqual(tax_largest([Amount('0'), Amount('2')]), Amount('2'))\n")
    commit(root, "fix(tax): skip zero lines when finding the largest")


BRANCHES = {"large-mixed": "feat/currency-rounding", "explain-branch": "feat/currency-rounding",
            "oversized": "feat/ledger-extensions", "small-fix": "fix/tax-largest"}


def numstat(root, base_ref, head_ref, paths=None):
    output = git(root, "diff", "--numstat", base_ref, head_ref, *(["--", *paths] if paths else []))
    added = deleted = 0
    for line in output.splitlines():
        a, d, _ = line.split("\t", 2)
        added += int(a)
        deleted += int(d)
    return {"added": added, "deleted": deleted}


def create(root, case):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.name", "Fixture Maintainer")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "config", "commit.gpgsign", "false")
    write(root, ".gitignore", ".agents/\n__pycache__/\n*.pyc\n")
    write(root, "AGENTS.md", AGENTS)
    write(root, "scripts/check", CHECK, True)
    base(root)
    if case not in BRANCHES:
        raise ValueError(case)
    git(root, "switch", "-q", "-c", BRANCHES[case])
    snapshot = {"case": case, "branch": BRANCHES[case]}
    if BRANCHES[case] == "feat/currency-rounding":
        rename(root)
        relock(root)
        reformat(root)
        before = git(root, "rev-parse", "HEAD")
        rounding(root)
        snapshot["core"] = numstat(root, before, "HEAD")
        snapshot["core_files"] = CORE_FILES
    elif case == "oversized":
        oversized(root)
    else:
        small_fix(root)
    snapshot["total"] = numstat(root, "main", "HEAD")
    snapshot["refs"] = git(root, "for-each-ref", "--format=%(refname) %(objectname)").splitlines()
    snapshot["status"] = git(root, "status", "--porcelain")
    (root.parent / "fixture-initial.json").write_text(json.dumps(snapshot, indent=2) + "\n")
    return snapshot


if __name__ == "__main__":
    create(Path.cwd(), sys.argv[1])
