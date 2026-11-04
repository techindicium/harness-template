#!/usr/bin/env python3
"""Handoff gate: may this item have a Handoff artifact?

One decision, enforced where the artifact is written. The Handoff entry conditions used to exist
only as prose in a skill; this turns them into a check that runs on the execution path.

An artifact is a file named `handoff-<ID>.md` (kept in `evidence/`) or `figures-<ID>.csv` (kept
in `delivery/`), at any depth, with `<ID>` such as REQUEST-007. It is allowed only when the
evidence files of the same item, in `evidence/`, say the item is clear (see CONTRACT). A missing
file, a missing field, an unreadable file and a field that appears twice with different values
all count as "not clear".

The evidence is written by the model, so the gate does not take its word for the build alone. It
also reads the track repository: an actor in the interaction extract that the first response mart
neither counts nor declares as not a response, and a mart with no rows, keep the item out of Handoff
too. The checks read the data and the SQL of the track, not a field of the evidence, and a track
that cannot be read counts as "not clear". The path of the track is pinned in the script
(TRACK_REPOSITORY); a `context_repository` in track.yaml that names another directory is "not
clear". One input still comes from a file the model can edit: for the check of actors, the metric in
the intake or route note, which skips that check for an item whose metric does not read
interactions (ACTOR_FREE_METRICS). The check of marts is never skipped.

Three layers, so the control does not depend on any one harness or model:

  core     pure functions: which item does this path or command touch, and what fails for it
  cli      `handoff_gate.py check <ID>` and `handoff_gate.py audit`; exit 0 clear, 1 not clear
  adapter  `handoff_gate.py hook`; reads one hook event as JSON on stdin and answers with exit 2
           (block) or 0 (pass). Only this layer knows the event format.

Another harness, a pre-commit or a CI job calls `check` or `audit` and needs no adapter. `audit`
reads the repository state, so it finds an artifact whichever tool or person created it.

The target is matched by file name, at any depth and in any spelling of the path, and the
evidence directory is derived from the target, so a relative path, an absolute path, `..`, a
symlink, upper case or a `cd` before the write all reach the same decision. A shell command is
split on unquoted operators; a segment is let through only when its command only reads (no
redirect, no command substitution, no output option) or only removes, so a stray artifact can be
cleaned up. Anything else that names an artifact is judged by the evidence. A name built at run
time (a variable, a glob, a script written earlier) is not visible to a command check: `audit`
finds that artifact afterwards. The gate fails closed: when it cannot read the event but the raw
text names an artifact, it blocks.

Exit codes of `hook`: 2 blocks, 0 passes. Only 2 blocks; an unhandled error would exit 1, which
does not, so every error path in `hook` is handled and decided explicitly.

Every decision on an artifact is appended to `traces/gate-decisions.jsonl` under the project
root, or to the file named by HANDOFF_GATE_LOG.
"""

import csv
import json
import os
import re
import shlex
import subprocess
import sys
from collections import Counter, namedtuple
from datetime import datetime, timezone

# Stage -> (check key, required fields). A value is compared without case; "@person" and
# "@date" are the two checks that are not an equality. The check key selects the wording of
# the block message. Change the fields here to move the gate to another process. Approval is read
# from the two fields a person fills. `status` is a label: the approve and handoff skills both say
# that Handoff does not read it.
CONTRACT = (
    ("approve", "approval", (("approved_by", "@person"), ("approved_at", "@date"))),
    (
        "verify",
        "verify",
        (
            ("verify_status", "clear"),
            ("shape_tests_verdict", "pass"),
            ("definition_alignment_verdict", "aligned"),
            ("period_alignment_verdict", "match"),
        ),
    ),
    ("context", "period", (("period_match", "true"),)),
    ("build", "build", (("exit_code", "0"),)),
)

# The track repository, relative to the project root. It is pinned here, in reviewed code, because
# track.yaml is a data file the model edits: a `context_repository` repointed at a clean copy would let
# through an item that the real track blocks. track.yaml has to name the same directory, so the two
# cannot drift apart unnoticed.
TRACK_REPOSITORY = "../portwell-analytics"
# What the gate reads in the track repository itself. Paths are relative to the track. Change them,
# and TRACK_REPOSITORY, to move the gate to another process.
EXTRACT_CSV = "data/ops-extract/interaction.csv"
FILTER_SQL = "project/models/marts/first_response.sql"
WAREHOUSE = "warehouse.duckdb"
TRACK_PYTHON = ".venv/bin/python"
# Actors whose interactions are not a response to the customer. This is an assumption of the group:
# the owner of the metric has not recorded it, and the definition says only "first outbound
# interaction". An actor that is neither here nor in the mart's filter keeps the item out.
NON_RESPONSE_ACTORS = {"customer"}
# Metrics whose figure is not built from the interaction extract, so an actor the mart does not
# count cannot reach it. self_service_rate reads tickets and suggestions only (the SQL of its mart,
# `self_service.sql` under MARTS_DIR in the track). The check of actors is skipped only when the
# evidence names a metric from this set and nothing else. The note is written by the model: no note
# that names a metric, an unknown metric, or two notes that disagree leave the check on, and one note
# that names such a metric is enough to skip it.
ACTOR_FREE_METRICS = {"self_service_rate"}
# A heuristic reader of the mart: exactly one `actor IN (...)` in the file, and a WHERE that reaches it
# with no CASE, NOT or OR in between (a CASE elsewhere is fine). Anything else is not read; it is
# `cannot_evaluate`, because a filter the gate cannot tell from an exclusion would let a gap through.
ACTOR_FILTER = re.compile(r"\bactor\s+IN\s*\(([^)]*)\)", re.I)
WHERE_ACTOR = re.compile(r"\bWHERE\b(?:(?!\bCASE\b|\bNOT\b|\bOR\b|;).)*?\bactor\s+IN\s*\(", re.I | re.S)
# The tables the SQL of the track creates are the marts the warehouse has to hold.
MARTS_DIR = "project/models/marts"
MART_TABLE = re.compile(r"\bCREATE\s+(?:OR\s+REPLACE\s+)?TABLE\s+marts\.(\w+)", re.I)
# Asked of the warehouse through the track's own interpreter, which is the one that has duckdb:
# every mart and its row count, one `<mart> <rows>` line each.
MARTS_QUERY = (
    "import sys, duckdb\n"
    "con = duckdb.connect(sys.argv[1], read_only=True)\n"
    "sql = \"select table_name from information_schema.tables where table_schema = 'marts' order by 1\"\n"
    "for (name,) in con.execute(sql).fetchall():\n"
    "    print(name, con.execute(f'select count(*) from marts.\"{name}\"').fetchone()[0])\n"
)
TRACK_TIMEOUT = 30  # seconds; the query takes about a tenth of a second when the warehouse is there

# Words that mean the value is not a person: a placeholder, or a role instead of a name.
NOT_A_PERSON = {"unknown", "none", "null", "tbd", "pending", "todo", "placeholder", "nobody", "unassigned"}
ROLE_WORDS = {"lead", "owner", "manager", "approver", "team", "agent", "assistant", "automation", "bot", "model", "system", "user"}
EMPTY_VALUES = {"", "none", "null", "unknown", "tbd", "n/a", "na", "-"}
# What a field holds when the same key appears twice with different values.
CONFLICT = "more than one value"

# Commands that only read. A segment that also redirects, substitutes a command or names an
# output file is treated as a writer (see may_write).
READ_ONLY = {
    "cat", "head", "tail", "less", "more", "grep", "egrep", "fgrep", "rg", "wc", "ls", "stat", "file",
    "diff", "cmp", "md5sum", "sha1sum", "sha256sum", "echo", "printf", "test", "[", "realpath",
    "basename", "dirname", "readlink",
}
GIT_READ_ONLY = {"status", "diff", "log", "show", "ls-files", "blame", "grep"}
# Commands that only remove. Removing an artifact is how a stray one is cleaned up, so it passes.
REMOVERS = {"rm", "unlink"}
GIT_REMOVERS = {"rm"}
# Global git options that take the next word as their value, as in `git -C <dir> diff`.
GIT_OPTIONS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
# Redirects that write nothing: a stream copied to another, or anything sent to /dev/null.
SAFE_REDIRECT = re.compile(r"&?\d*>&\d+|&?\d*>>?\s*/dev/null(?![\w./-])")
QUOTED = re.compile(r"'[^']*'|\"(?:\\.|[^\"\\])*\"")
SINGLE_QUOTED = re.compile(r"'[^']*'")
# Words that run another command; they are skipped to find the command that matters.
WRAPPERS = {"sudo", "env", "rtk", "proxy", "time", "timeout", "nice", "nohup", "command", "exec", "xargs", "stdbuf"}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__"}

_ID = r"[A-Za-z][A-Za-z0-9]*-\d+"
_NAME = rf"handoff-(?P<hid>{_ID})\.md|figures-(?P<fid>{_ID})\.csv"
ARTIFACT_NAME = re.compile(_NAME, re.I)
# The directory part is optional and only used to find the evidence directory. The lookbehind and
# lookahead keep `myhandoff-X-1.md` and `handoff-X-1.md.bak` out.
ARTIFACT = re.compile(rf"(?<![\w.-])(?P<dir>[^\s'\"=;|&<>()`]*/)?(?P<name>{_NAME})(?![\w.-])", re.I)
FIELD = re.compile(r"^\s*(?:[-*]\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*?)\s*$")

Target = namedtuple("Target", "name item_id raw_path")

WHY = {
    "approval": "Figures are not delivered without a named approver on file (an entry condition of Handoff). Approval is a named human act.",
    "verify": "Handoff needs a clear Verify. Passing shape tests does not show the figure is right: the definition and the period must also be aligned.",
    "incoherent": "The Verify evidence says clear while one of its verdicts is not. Evidence that contradicts itself cannot support a delivery.",
    "period": "The extract has to cover the reporting period. A partial extract produces figures for a different period than the one delivered.",
    "build": "There is nothing to deliver without a successful build.",
    "coverage": "A figure is only as complete as the actors the mart counts. An actor in the extract that the mart neither counts nor declares as not a response drops its tickets from the figure, and no shape test fails.",
    "marts": "The shape tests pass against empty tables, so a build that produced no rows still reads as green. A figure needs every mart to exist and to have rows behind it.",
    "cannot_evaluate": "The gate fails closed: when it cannot read the evidence, the track or the event, it does not guess.",
    "audit": "A Handoff artifact exists although the item does not pass the gate, so it was created by a route the gate could not see.",
}
NEXT = {
    "approval": "Only a person records approved_by and approved_at in the approval evidence. Stop and ask the user for the approver's name.",
    "verify": "Do not deliver. The item goes back to Correction required or Escalated, as the Verify procedure says.",
    "incoherent": "Run Verify again. Do not edit the status to match the verdicts.",
    "period": "The extract does not cover the reporting period. Decide with the user whether to rebuild with the right extract. Do not deliver meanwhile.",
    "build": "Run Act again. Nothing is delivered without a successful build.",
    "coverage": "Do not edit the mart (the track repository is read-only) and do not add the actor to NON_RESPONSE_ACTORS yourself. Ask the user to put the question to the owner of the metric. Do not deliver meanwhile.",
    "marts": "Do not deliver. Run Act again and read the build output.",
    "cannot_evaluate": "Stop and tell the user. Do not try another path.",
    "audit": "Tell the user the artifact exists without passing the gate. Do not delete it unless told to.",
}
ASK = {
    "approval": "Who is the named approver for {id}?",
    "verify": "Verify for {id} is blocked ({reason}). Should this go to Correction required or Escalated?",
    "incoherent": "The verify evidence for {id} contradicts itself. Should I re-run verify?",
    "period": "The extract does not cover the period for {id}. Can it be rebuilt with the right extract?",
    "build": "The build for {id} did not succeed. Should I run Act again?",
    "coverage": "For {id}: {reason}. Is an interaction by that actor an outbound response, and who owns the decision?",
    "marts": "The warehouse for {id} has no rows behind a figure ({reason}). Should I run Act again?",
    "cannot_evaluate": "The handoff gate could not evaluate {id} ({reason}). How do you want to proceed?",
    "audit": "{artifact} exists but {id} does not pass the gate. Do you want it removed or the evidence completed?",
}
DO_NOT = (
    "retry this action through another path (absolute, relative, cd, shell, script): the gate resolves "
    "all of them to the same item. Do not edit the evidence files to satisfy the gate: approval is a "
    "named human act."
)


# --- core -------------------------------------------------------------------------------------


def is_person(value):
    """A name a person would sign with: not empty, not a placeholder, not a role."""
    value = (value or "").strip()
    if not value or value.casefold() in EMPTY_VALUES or re.fullmatch(r"[<\[].*[>\]]", value):
        return False
    words = set(re.findall(r"[^\W\d_]+", value.casefold()))
    return bool(words) and not words & (NOT_A_PERSON | ROLE_WORDS)


def is_date(value):
    """An ISO date, alone or followed by a time. A placeholder or an impossible date is not one."""
    if not re.match(r"\d{4}-\d{2}-\d{2}(?:[T ].*)?$", value):
        return False
    try:
        datetime.strptime(value[:10], "%Y-%m-%d")
    except ValueError:
        return False
    return True


def satisfies(value, expected):
    if value is None or value == CONFLICT:
        return False
    if expected == "@person":
        return is_person(value)
    if expected == "@date":
        return is_date(value)
    return value.casefold() == expected


def describe(expected):
    return {"@person": "a person's name", "@date": "a date"}.get(expected, expected)


def read_fields(path):
    """`key: value` lines of an evidence file; None when unreadable. A key that appears twice
    with different values holds CONFLICT, because there is no telling which line is the record."""
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            lines = handle.read().splitlines()
    except OSError:
        return None
    fields = {}
    for line in lines:
        match = FIELD.match(line)
        if match:
            key = match.group(1)
            value = re.sub(r"\s+#.*$", "", match.group(2)).strip().strip("\"'`")
            fields[key] = value if fields.get(key, value) == value else CONFLICT
    return fields


def failure(check, file, field, found, expected):
    return {"check": check, "file": file, "field": field, "found": found, "expected": expected}


def cannot_evaluate(file, field, found, expected):
    return [failure("cannot_evaluate", file, field, found, expected)]


def track_root(root):
    """The track repository the project names, as (path, []), or (None, the failure that says why not)."""
    fields = read_fields(os.path.join(root, "track.yaml"))
    if fields is None:
        return None, cannot_evaluate("track.yaml", "-", "missing or unreadable", "the file to exist")
    value = fields.get("context_repository")
    if not value or value == CONFLICT:
        return None, cannot_evaluate("track.yaml", "context_repository", value or "missing", "a path to the track repository")
    track = os.path.realpath(os.path.join(root, value))
    if track != os.path.realpath(os.path.join(root, TRACK_REPOSITORY)):
        return None, cannot_evaluate("track.yaml", "context_repository", "another directory than the pinned track", f"{TRACK_REPOSITORY} (TRACK_REPOSITORY in the gate)")
    if not os.path.isdir(track):
        return None, cannot_evaluate("track.yaml", "context_repository", "not a directory", "a path to the track repository")
    return track, []


def read_sql(path):
    """The SQL of a file without its comments, line and block."""
    with open(path, encoding="utf-8", errors="replace") as handle:
        return re.sub(r"/\*.*?\*/", "", re.sub(r"--[^\n]*", "", handle.read()), flags=re.S)


def show_actor(actor):
    """An actor as the message names it: quoted when a space would not show, `(blank)` when empty."""
    if not actor:
        return "(blank)"
    return repr(actor) if actor != actor.strip() else actor


def check_coverage(track):
    """An actor in the interaction extract that the first response mart neither counts nor declares
    as not a response: its tickets drop out of the figure and no shape test notices."""
    try:
        with open(os.path.join(track, EXTRACT_CSV), newline="", encoding="utf-8", errors="replace") as handle:
            reader = csv.DictReader(handle)
            if "actor" not in (reader.fieldnames or []):
                return cannot_evaluate(EXTRACT_CSV, "actor", "no such column", "an actor column")
            # The value is kept as it is: DuckDB keeps a space and the case, and the mart filter is an
            # exact match, so a trimmed value would count as covered a row that the mart drops.
            seen = Counter(row.get("actor") or "" for row in reader)
        sql = read_sql(os.path.join(track, FILTER_SQL))
    except (OSError, csv.Error) as error:
        return cannot_evaluate(EXTRACT_CSV, "-", f"could not read the extract or the mart ({error.__class__.__name__})", "both files to be readable")
    if not seen:
        return cannot_evaluate(EXTRACT_CSV, "actor", "no interactions", "at least one row")
    clauses = ACTOR_FILTER.findall(sql)
    counted = set(re.findall(r"'([^']*)'", clauses[0])) if len(clauses) == 1 and WHERE_ACTOR.search(sql) else set()
    if not counted:
        return cannot_evaluate(FILTER_SQL, "actor", "not exactly one plain `WHERE ... actor IN (...)` filter", "one filter the gate can read")
    uncovered = sorted(actor for actor in seen if actor not in counted | NON_RESPONSE_ACTORS)
    if not uncovered:
        return []
    absent = sorted(counted - set(seen))
    note = f"; {', '.join(absent)} {'is' if len(absent) == 1 else 'are'} not in the extract" if absent else ""
    expected = f"counted by {os.path.basename(FILTER_SQL)} ({', '.join(sorted(counted))}{note}) or declared as not a response"
    found = ", ".join(f"{show_actor(actor)} ({seen[actor]} interaction{'' if seen[actor] == 1 else 's'})" for actor in uncovered)
    return [failure("coverage", EXTRACT_CSV, "actor", found, expected)]


def check_marts(track):
    """A mart the track defines that the warehouse lacks or holds with no rows. The shape tests of the
    track pass against empty tables, so a build that produced nothing reads as green; this asks the
    warehouse itself, through the track's interpreter."""
    warehouse = os.path.join(track, WAREHOUSE)
    if not os.path.isfile(warehouse):
        return cannot_evaluate(WAREHOUSE, "-", "missing", "a warehouse built by the track")
    defined = set()
    try:
        directory = os.path.join(track, MARTS_DIR)
        for name in sorted(os.listdir(directory)):
            if name.endswith(".sql"):
                defined |= set(MART_TABLE.findall(read_sql(os.path.join(directory, name))))
    except OSError as error:
        return cannot_evaluate(MARTS_DIR, "-", f"could not read ({error.__class__.__name__})", "the SQL of the marts to be readable")
    if not defined:
        return cannot_evaluate(MARTS_DIR, "-", "no table defined", "SQL that creates the marts")
    command = [os.path.join(track, TRACK_PYTHON), "-I", "-c", MARTS_QUERY, warehouse]
    try:
        done = subprocess.run(command, capture_output=True, encoding="utf-8", errors="replace", timeout=TRACK_TIMEOUT)
    except (OSError, subprocess.SubprocessError) as error:
        return cannot_evaluate(TRACK_PYTHON, "-", f"could not run ({error.__class__.__name__})", "the track interpreter to answer")
    if done.returncode != 0:
        return cannot_evaluate(TRACK_PYTHON, "exit_code", str(done.returncode), "0")
    rows = {}
    for line in done.stdout.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"(\S+) (\d+)", line.strip())
        if not match:
            return cannot_evaluate(TRACK_PYTHON, "-", "an answer that is not a mart and a row count", "lines of `<mart> <rows>`")
        rows[match.group(1)] = int(match.group(2))
    missing = [failure("marts", WAREHOUSE, mart, "missing", "a table with at least one row") for mart in sorted(defined - set(rows))]
    empty = [failure("marts", WAREHOUSE, mart, "0 rows", "at least one row") for mart, count in rows.items() if count == 0]
    return missing + empty


def names_only_actor_free_metrics(evidence_dir, item_id):
    """True when the intake or route note names a metric and every metric named is in ACTOR_FREE_METRICS."""
    names = set()
    for stage in ("intake", "route"):
        fields = read_fields(os.path.join(evidence_dir, f"{stage}-{item_id}.md")) or {}
        if fields.get("metric_name"):
            names.add(fields["metric_name"].casefold())
    return bool(names) and names <= ACTOR_FREE_METRICS


def check_track(root, evidence_dir, item_id):
    """Failures found by reading the track repository directly. They read the data and the SQL of the
    track, not a field of the evidence. The path of the track is pinned (TRACK_REPOSITORY); whether the
    actor check applies still comes from a file the model can edit (the metric in the intake note)."""
    track, failures = track_root(root)
    if track is None:
        return failures
    coverage = [] if names_only_actor_free_metrics(evidence_dir, item_id) else check_coverage(track)
    return coverage + check_marts(track)


def check_item(evidence_dir, item_id):
    """Failures that keep the item out of Handoff; an empty list means it is clear."""
    failures = []
    for stage, check, rules in CONTRACT:
        name = f"{stage}-{item_id}.md"
        fields = read_fields(os.path.join(evidence_dir, name))
        if fields is None:
            failures.append(failure(check, name, "-", "missing", "the file to exist"))
            continue
        stage_failures = [
            failure(check, name, field, fields.get(field, "missing"), describe(expected))
            for field, expected in rules
            if not satisfies(fields.get(field), expected)
        ]
        if stage == "verify" and satisfies(fields.get("verify_status"), "clear"):
            for item in stage_failures:
                item["check"] = "incoherent"
        failures += stage_failures
    failures += check_track(os.path.dirname(os.path.abspath(evidence_dir)), evidence_dir, item_id)
    return failures


def find_targets(text):
    """Artifacts named anywhere in a piece of text, whatever the spelling of the path."""
    found, seen = [], set()
    for match in ARTIFACT.finditer(text):
        target = Target(match.group("name"), match.group("hid") or match.group("fid"), (match.group("dir") or "") + match.group("name"))
        if (target.name.casefold(), target.raw_path) not in seen:
            seen.add((target.name.casefold(), target.raw_path))
            found.append(target)
    return found


def targets_for_path(path, cwd):
    """Artifacts a Write or Edit would touch: the path as given and where it really lands."""
    resolved = os.path.realpath(os.path.join(cwd, os.path.expanduser(path)))
    found = find_targets(path)
    for target in find_targets(resolved):
        if target.name.casefold() not in {t.name.casefold() for t in found}:
            found.append(target)
    return found


def segments(command):
    """Split a shell command on unquoted `;`, `&`, `|` and newlines."""
    out, buf, quote, i = [], [], None, 0
    while i < len(command):
        char = command[i]
        if quote:
            buf.append(char)
            if char == "\\" and quote == '"' and i + 1 < len(command):
                i += 1
                buf.append(command[i])
            elif char == quote:
                quote = None
        elif char == "\\" and i + 1 < len(command):
            i += 1
            buf += [char, command[i]]
        elif char in "'\"":
            quote = char
            buf.append(char)
        elif char == "&" and (command[i - 1:i] == ">" or command[i + 1:i + 2] == ">"):
            buf.append(char)  # `2>&1` and `&>` redirect; they do not end the command
        elif char in ";&|\n":
            out.append("".join(buf))
            buf = []
        else:
            buf.append(char)
        i += 1
    out.append("".join(buf))
    return [part.strip() for part in out if part.strip()]


def git_subcommand(words):
    """The git subcommand, after global options such as `-C <dir>`, `-c k=v` and `--no-pager`."""
    rest = iter(words[1:])
    for word in rest:
        if word in GIT_OPTIONS_WITH_VALUE:
            next(rest, None)
        elif not word.startswith("-"):
            return word
    return ""


def may_write(segment):
    """A read-only or removing command can still write: it redirects, runs another command through
    a substitution, or names an output file. Quoted text is literal, except that a substitution
    still runs inside double quotes."""
    plain = QUOTED.sub("", SAFE_REDIRECT.sub("", segment))
    live = SINGLE_QUOTED.sub("", segment)
    return ">" in plain or "--output" in plain or any(mark in live for mark in ("$(", "`", "<("))


def writing_segments(command, depth=0):
    """Segments that name an artifact and may write it; reads and removals are let through."""
    risky = []
    for segment in segments(command):
        if not ARTIFACT.search(segment):
            continue
        try:
            words = shlex.split(segment)
        except ValueError:
            words = segment.split()
        while words and (re.fullmatch(r"[A-Za-z_]\w*=.*", words[0]) or os.path.basename(words[0]) in WRAPPERS or re.fullmatch(r"-\S*|\d+(\.\d+)?[smhd]?", words[0])):
            words.pop(0)
        if len(words) == 1 and " " in words[0] and depth < 3:
            risky += writing_segments(words[0], depth + 1)
            continue
        command_word = os.path.basename(words[0]) if words else ""
        subcommand = git_subcommand(words) if command_word == "git" else ""
        harmless = command_word in READ_ONLY or command_word in REMOVERS or subcommand in GIT_READ_ONLY | GIT_REMOVERS
        if harmless and not may_write(segment):
            continue
        risky.append(segment)
    return risky


def targets_in_command(command):
    found = []
    for segment in writing_segments(command):
        found += find_targets(segment)
    return found


def find_root(start):
    """Nearest directory at or above `start` that holds an `evidence/` directory."""
    current = os.path.realpath(start)
    while True:
        if os.path.isdir(os.path.join(current, "evidence")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return os.path.realpath(start)
        current = parent


def evidence_dir(target, cwd, root):
    directory = os.path.dirname(target.raw_path)
    if directory:
        directory = os.path.realpath(os.path.join(cwd, directory))
        if os.path.basename(directory).casefold() == "evidence" and os.path.isdir(directory):
            return directory
        sibling = os.path.join(os.path.dirname(directory), "evidence")
        if os.path.basename(directory).casefold() == "delivery" and os.path.isdir(sibling):
            return sibling
    candidates = [cwd] if os.path.basename(cwd).casefold() == "evidence" else []
    for candidate in candidates + [os.path.join(cwd, "evidence"), os.path.join(root, "evidence")]:
        if os.path.isdir(candidate):
            return candidate
    return os.path.join(root, "evidence")


def audit(root):
    """Artifacts that exist in the tree, in any directory, although their item does not pass."""
    violations = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            match = ARTIFACT_NAME.fullmatch(filename)
            if not match:
                continue
            target = Target(filename, match.group("hid") or match.group("fid"), os.path.join(dirpath, filename))
            failures = check_item(evidence_dir(target, dirpath, root), target.item_id)
            if failures:
                failures.append(failure("audit", filename, "-", "exists", "absent until the item is clear"))
                violations.append({"target": target, "failures": failures})
    return violations


def format_block(subject, item_id, failures, artifact=""):
    """The message an agent reads when blocked: what, why, what was found, what not to do, what next."""
    checks = list(dict.fromkeys(f["check"] for f in failures))
    # Each question cites the first failure of its own check, never one found by another check.
    reasons = {}
    for item in failures:
        reasons.setdefault(item["check"], item["found"] if item["field"] == "-" else f"{item['field']} is {item['found']}")
    found = []
    for item in failures:
        if item["field"] == "-" and item["found"] == "missing":
            found.append(f"  {item['file']} does not exist")
        elif item["field"] == "-":
            found.append(f"  {item['file']}: {item['found']}")
        else:
            found.append(f"  {item['file']}: {item['field']} is {item['found'] or 'empty'}, expected {item['expected']}")
    lines = [f"BLOCKED by the handoff gate: {subject}", "WHY:"]
    lines += [f"  {WHY[check]}" for check in checks]
    lines += ["FOUND:"] + found + [f"DO NOT: {DO_NOT}", "NEXT:"]
    lines += [f"  {NEXT[check]}" for check in checks]
    lines.append("ASK THE USER:")
    lines += [f"  \"{ASK[check].format(id=item_id, reason=reasons[check], artifact=artifact)}\"" for check in checks]
    return "\n".join(lines)


# --- adapter ----------------------------------------------------------------------------------


def project_relative(path, root):
    """How a path is written in the log: relative to the project, absolute only when outside it."""
    root = os.path.realpath(root)
    try:
        inside = os.path.commonpath([path, root]) == root
    except ValueError:
        inside = False
    return os.path.relpath(path, root) if inside else path


def record(root, event, tool, target, cwd, decision, failures):
    path = os.path.abspath(os.environ.get("HANDOFF_GATE_LOG") or os.path.join(root, "traces", "gate-decisions.jsonl"))
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "event": event,
        "tool": tool,
        "target": project_relative(os.path.realpath(os.path.join(cwd, target.raw_path)), root),
        "item": target.item_id,
        "decision": decision,
        "failed": sorted({f["check"] for f in failures}),
    }
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")
    except OSError:
        pass  # the decision matters more than its trace


def judge(event, tool, targets, cwd, root):
    blocked = False
    for target in targets:
        failures = check_item(evidence_dir(target, cwd, root), target.item_id)
        record(root, event, tool, target, cwd, "block" if failures else "allow", failures)
        if failures:
            subject = f"{tool} on {target.raw_path}" if tool in ("Write", "Edit") else f"shell command naming {target.name}"
            print(format_block(subject, target.item_id, failures), file=sys.stderr)
            blocked = True
    return 2 if blocked else 0


def on_pre_tool_use(payload, cwd, root):
    tool, args = payload["tool_name"], payload["tool_input"]
    if tool in ("Write", "Edit"):
        targets = targets_for_path(args["file_path"], cwd)
    elif tool == "Bash":
        targets = targets_in_command(args["command"])
    else:
        return 0
    return judge("PreToolUse", tool, targets, cwd, root)


def on_stop(payload, cwd, root):
    violations = audit(root)
    if not violations:
        return 0
    guard = bool(payload.get("stop_hook_active"))
    for violation in violations:
        target = violation["target"]
        record(root, "Stop", "-", target, cwd, "allow-loop-guard" if guard else "block", violation["failures"])
        if not guard:
            subject = f"artifact {target.raw_path} exists but item {target.item_id} does not pass the gate"
            print(format_block(subject, target.item_id, violation["failures"], artifact=target.raw_path), file=sys.stderr)
    if guard:
        print("handoff gate: an artifact still exists without a clear item; letting the turn end to avoid a loop.", file=sys.stderr)
        return 0
    return 2


def fail_closed(raw, error):
    targets = find_targets(raw)
    if not targets:
        print(f"handoff gate: could not read the event ({error}); it names no artifact, so it passes.", file=sys.stderr)
        return 0
    item = targets[0].item_id
    problem = [failure("cannot_evaluate", "event", "-", str(error), "an event the gate can read")]
    print(format_block(f"an event the gate could not read, naming {targets[0].name}", item, problem), file=sys.stderr)
    return 2


def hook(raw):
    try:
        payload = json.loads(raw)
        cwd = payload.get("cwd") or os.getcwd()
        root = os.environ.get("CLAUDE_PROJECT_DIR") or find_root(cwd)
        event = payload["hook_event_name"]
        if event == "PreToolUse":
            return on_pre_tool_use(payload, cwd, root)
        if event == "Stop":
            return on_stop(payload, cwd, root)
        return 0
    except Exception as error:  # an unhandled error exits 1, which does not block
        return fail_closed(raw, error)


# --- cli --------------------------------------------------------------------------------------


def cli(argv):
    root = find_root(os.getcwd())
    if argv[0] == "check" and len(argv) == 2:
        failures = check_item(os.path.join(root, "evidence"), argv[1])
        if failures:
            print(format_block(f"item {argv[1]} cannot enter Handoff", argv[1], failures), file=sys.stderr)
            return 1
        return 0
    if argv[0] == "audit" and len(argv) == 1:
        violations = audit(root)
        for violation in violations:
            target = violation["target"]
            subject = f"artifact {target.raw_path} exists but item {target.item_id} does not pass the gate"
            print(format_block(subject, target.item_id, violation["failures"], artifact=target.raw_path), file=sys.stderr)
        return 1 if violations else 0
    return usage()


def usage():
    print("usage: handoff_gate.py hook | check <ID> | audit", file=sys.stderr)
    return 64


def main(argv):
    if not argv:
        return usage()
    if argv[0] == "hook":
        return hook(sys.stdin.buffer.read().decode("utf-8", "replace"))
    return cli(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
