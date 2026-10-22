#!/usr/bin/env python3
"""Context contract for the verify skill, enforced by Claude Code hooks.

One script, three events (dispatch on hook_event_name in the JSON read from stdin):
  PreToolUse   activate the run; deny prohibited reads, writes and over-limit reads; record Bash.
  PostToolUse  record the reads that succeeded.
  Stop         block the end of the run until the contract is met; escalate at the last check.

The control is inert unless a verify run is active for the session (a marker file).
Standard library only. Design: docs/module-2-design.md. Contract: harness/verify-contract.json.
"""
import fnmatch
import json
import os
import posixpath
import re
import sys
import time

CONTRACT_REL = "harness/verify-contract.json"
READ_KINDS = ("Read", "Grep", "Glob")
BASH_WRITE_PATTERNS = [
    r"(?<![<>0-9&])>>?(?!&)",       # output redirection, not 2>&1
    r"<<",                          # here-document
    r"\btee\b",
    r"\bsed\s+-i\b",
    r"\b(rm|mv|cp|mkdir)\b",
    r"\bgit\s+(add|commit|push|restore|checkout|reset)\b",
]


def utc_now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def norm(path):
    """Forward slashes, no duplicate slashes, `.` and `..` resolved. Case is kept; compare with .lower()."""
    s = re.sub(r"/+", "/", str(path).replace("\\", "/"))
    return posixpath.normpath(s) if s else s


def is_absolute(path):
    return bool(re.match(r"^[A-Za-z]:[\\/]", path)) or path.startswith(("/", "\\"))


def full_path(path, project):
    p = norm(path)
    return p if is_absolute(path) else norm(norm(project) + "/" + p)


def relative_to(path, base):
    """Path relative to base (forward slashes), or None when path is not inside base."""
    kp, kb = norm(path).lower(), norm(base).lower().rstrip("/")
    if kp == kb:
        return ""
    if kp.startswith(kb + "/"):
        return norm(path)[len(kb) + 1:]
    return None


def append_line(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def read_lines(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    return out


class Context:
    def __init__(self, event):
        self.event = event
        self.project = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()
        self.session = re.sub(r"[^A-Za-z0-9_.-]", "_", str(event.get("session_id") or "no-session"))
        self.mode = event.get("permission_mode")
        self.state_dir = os.path.join(self.project, ".claude", "verify-state", self.session)
        self.marker_path = os.path.join(self.state_dir, "marker.json")
        self.events_path = os.path.join(self.state_dir, "events.jsonl")
        self.trace_path = os.path.join(self.project, "traces", "verify-runs", self.session + ".jsonl")
        with open(os.path.join(self.project, CONTRACT_REL), encoding="utf-8") as f:
            self.contract = json.load(f)
        self._roots = None

    # state
    def marker(self):
        if not os.path.exists(self.marker_path):
            return None
        with open(self.marker_path, encoding="utf-8") as f:
            return json.load(f)

    def write_marker(self, marker):
        os.makedirs(self.state_dir, exist_ok=True)
        with open(self.marker_path, "w", encoding="utf-8") as f:
            json.dump(marker, f)

    def clear_marker(self):
        if os.path.exists(self.marker_path):
            os.remove(self.marker_path)

    def start_run(self, trigger):
        os.makedirs(self.state_dir, exist_ok=True)
        open(self.events_path, "w", encoding="utf-8").close()  # a new run starts with an empty registry
        self.write_marker({"session_id": self.session, "trigger": trigger, "status": "active",
                           "started": utc_now()})

    def raw(self, kind, **fields):
        append_line(self.events_path, dict(ts=utc_now(), kind=kind, **fields))

    def trace(self, **fields):
        append_line(self.trace_path, dict(ts=utc_now(), session_id=self.session,
                                          permission_mode=self.mode, **fields))

    def events(self):
        return read_lines(self.events_path)

    # contract
    def context_repository(self):
        track = os.path.join(self.project, "track.yaml")
        if not os.path.exists(track):
            return None
        with open(track, encoding="utf-8") as f:
            for line in f:
                m = re.match(r"^context_repository:\s*(?:'([^']*)'|\"([^\"]*)\"|([^#\n]+))", line)
                if m:
                    return (m.group(1) or m.group(2) or m.group(3) or "").strip() or None
        return None

    def roots(self):
        if self._roots is None:
            repo = self.context_repository()
            values = {"${project}": self.project, "${context_repository}": repo}
            self._roots = [values.get(r, r) for r in self.contract.get("roots", []) if values.get(r, r)]
        return self._roots


def emit(obj):
    sys.stdout.write(json.dumps(obj))


def pre_deny(c, tool, target, reason):
    c.raw("deny", tool=tool, path=target)
    c.trace(event="PreToolUse", tool=tool, path=target, decision="deny", reason=reason)
    denials = sum(1 for e in c.events() if e.get("kind") == "deny")
    marker = c.marker() or {}
    if denials >= c.contract.get("max_denials", 3) and marker.get("status") != "halted":
        marker["status"] = "halted"
        c.write_marker(marker)
    emit({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                 "permissionDecisionReason": reason}})
    return 0


def prohibited_hit(text, contract):
    k = norm(text).lower()
    for name in contract.get("prohibited_path_names", []):
        if name.lower() in k:
            return name
    for sub in contract.get("prohibited_substrings", []):
        if sub.lower() in k:
            return sub
    return None


SCAN_SKIP_DIRS = {".git", ".venv", "node_modules"}
SCAN_CAP = 20000


def prohibited_below(base, contract):
    """First prohibited path found under a folder (a recursive search would read it), or None.
    The scan stops after SCAN_CAP entries and then reports nothing: it fails open."""
    if not os.path.isdir(base):
        return None
    seen = 0
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SCAN_SKIP_DIRS]
        for name in dirnames + filenames:
            if prohibited_hit(name, contract):
                return os.path.join(dirpath, name)
            seen += 1
            if seen > SCAN_CAP:
                return None
    return None


def tool_target(tool, ti):
    if tool == "Read":
        return ti.get("file_path")
    return ti.get("path")  # Grep and Glob; None means the working directory


def tool_pattern_text(tool, ti):
    if tool == "Glob":
        return ti.get("pattern")
    if tool == "Grep":
        return ti.get("glob")
    return None


def handle_pre(event, c):
    tool = event.get("tool_name")
    ti = event.get("tool_input") or {}
    contract = c.contract
    marker = c.marker()

    if marker is None:
        act = contract.get("activation", {})
        if tool == "Skill" and ti.get("skill") in act.get("skill_names", []):
            c.start_run("skill")
            c.trace(event="PreToolUse", tool=tool, decision="activated", trigger="skill", skill=ti.get("skill"))
            return 0
        if tool == "Read" and ti.get("file_path"):
            rel = relative_to(full_path(ti["file_path"], c.project), c.project)
            if rel is not None and rel.lower() in [p.lower() for p in act.get("read_paths", [])]:
                c.start_run("read_skill_md")
                c.trace(event="PreToolUse", tool=tool, decision="activated", trigger="read_skill_md")
                marker = c.marker()
        if marker is None:
            return 0  # no active run: the control does nothing

    if marker.get("status") == "halted":
        return pre_deny(c, tool, tool_target(tool, ti),
                        "The verify run is halted after repeated denials. Escalate to the author. "
                        "No further tool calls are allowed in this run.")

    if tool in contract.get("write_tools", []):
        target = ti.get("file_path") or ""
        rel = relative_to(full_path(target, c.project), c.project) if target else None
        protected = rel is not None and any(fnmatch.fnmatch(rel.lower(), p.lower())
                                            for p in contract.get("protected", []))
        if protected:
            reason = (f"`{target}` is a protected control file (the verify hooks, their contract, state and "
                      "trace). Writes are denied during a verify run, and changes to the control itself need "
                      "the author. Return the report in the final message.")
        else:
            reason = "Writes are denied during a verify run. Return the report in the final message."
        return pre_deny(c, tool, target, reason)

    if tool in contract.get("read_tools", []):
        target = tool_target(tool, ti)
        texts = [t for t in (target, tool_pattern_text(tool, ti)) if t]
        for text in texts:
            hit = prohibited_hit(text, contract)
            if hit:
                names = ", ".join(contract.get("prohibited_path_names", []))
                subs = ", ".join(contract.get("prohibited_substrings", []))
                return pre_deny(c, tool, text,
                                f"`{text}` is outside the verify context contract (prohibited: {names}; paths "
                                f"containing {subs}). Use only the files named in the contract. If a fact needs "
                                "this file, report the fact as 'unknown' with the pointer. Do not retry this path.")
        if target:
            f = full_path(target, c.project)
            if not any(relative_to(f, root) is not None for root in c.roots()):
                return pre_deny(c, tool, target,
                                f"`{target}` is outside the two roots of the verify context contract (the project "
                                "and the context repository). If a fact needs this path, report the fact as "
                                "'unknown' with the pointer. Do not retry this path.")
        if tool == "Grep":
            base = full_path(target, c.project) if target else norm(c.project)
            found = prohibited_below(base, contract)
            if found:
                return pre_deny(c, tool, target or base,
                                f"`{target or 'the working directory'}` contains a prohibited path "
                                f"(`{norm(found)}`), and a search there would read it. Search a narrower folder "
                                "that does not contain it. If a fact needs this content, report the fact as "
                                "'unknown' with the pointer. Do not retry this path.")
        limit = contract.get("context_limit")
        attempts = sum(1 for e in c.events() if e.get("kind") == "pre" and e.get("tool") in READ_KINDS)
        if limit is not None and attempts >= limit:
            return pre_deny(c, tool, target,
                            f"The context limit of {limit} read calls is reached. Report with what was read and "
                            "state the gap.")
        whole = tool == "Read" and "offset" not in ti and "limit" not in ti
        c.raw("pre", tool=tool, path=norm(full_path(target, c.project)) if target else None, whole_file=whole)
        c.trace(event="PreToolUse", tool=tool, path=target, decision="allowed")
        return 0

    if tool == "Bash":
        command = str(ti.get("command") or "")
        flags = []
        if any(re.search(p, command) for p in BASH_WRITE_PATTERNS):
            flags.append("write_pattern")
        if prohibited_hit(command, contract):
            flags.append("prohibited_path_text")
        c.raw("bash", flags=flags)
        c.trace(event="PreToolUse", tool="Bash", decision="recorded", flags=flags, command=command[:200])
        return 0  # Bash is recorded, never prevented: a known limitation

    return 0


def handle_post(event, c):
    tool = event.get("tool_name")
    if tool not in READ_KINDS or c.marker() is None:
        return 0
    ti = event.get("tool_input") or {}
    target = tool_target(tool, ti)
    whole = tool == "Read" and "offset" not in ti and "limit" not in ti
    c.raw("post", tool=tool, path=norm(full_path(target, c.project)) if target else None, whole_file=whole)
    return 0


# The definition below is the one in skills/verify/SKILL.md. A self-test checks that both say the same.
DATA_LINE_DEFINITION = "every non-blank line after the table header"


def count_data_rows(text):
    """Data lines of the log: every non-blank line after the table header (header row and separator row)."""
    count, seen_separator = 0, False
    for line in text.splitlines():
        s = line.strip()
        if not seen_separator:
            if re.match(r"^\|[\s:\-|]+\|$", s):
                seen_separator = True
            continue
        if s:
            count += 1
    return count


def report_block(message, heading):
    m = re.search(r"(?im)^[ \t]*#{0,6}[ \t]*\**" + re.escape(heading) + r"\**[ \t]*:?[ \t]*$", message or "")
    if not m:
        return None
    rest = message[m.end():]
    end = re.search(r"(?m)^[ \t]*#{1,6}[ \t]", rest)
    return rest[:end.start()] if end else rest


def check_contract(c, message):
    """Return the list of problems, empty when the contract is met."""
    problems = []
    events = c.events()
    for req in c.contract.get("required_reads", []):
        key = norm(full_path(req["path"], c.project)).lower()
        want_whole = bool(req.get("whole_file"))
        done = [e for e in events if e.get("kind") == "post" and norm(e.get("path") or "").lower() == key]
        tried = [e for e in events if e.get("kind") == "pre" and norm(e.get("path") or "").lower() == key]
        if want_whole:
            ok = any(e.get("whole_file") for e in done)
        else:
            ok = bool(done)
        if ok:
            continue
        if done and want_whole:
            problems.append(f"{req['path']} was read only in part (offset or limit given). Read it in full.")
        elif tried:
            problems.append(f"{req['path']} was attempted but did not complete (no successful read recorded). "
                            "Another hook may have blocked it. Read it again in full, or report the gap if it "
                            "stays blocked.")
        else:
            problems.append(f"{req['path']} was not read.")
    log_cfg = c.contract.get("log_check", {})
    heading = log_cfg.get("report_block_heading", "Context read")
    block = report_block(message, heading)
    if block is None:
        problems.append(f"The report has no `{heading}` block. Add one that lists the files read and states the "
                        f"number of data lines in {log_cfg.get('path')}.")
    else:
        log_path = os.path.join(c.project, log_cfg.get("path", ""))
        # An optional backtick after the path is a format tolerance only: the number is still compared below.
        m = re.search(re.escape(log_cfg.get("path", "")) + r"(`?)\s*\((\d+)\s+data\s+lines?\)", block)
        if not m:
            problems.append(f"The `{heading}` block does not state the number of data lines of "
                            f"{log_cfg.get('path')}, as `{log_cfg.get('path')} (N data lines)`.")
        elif os.path.exists(log_path):
            with open(log_path, encoding="utf-8") as f:
                actual = count_data_rows(f.read())
            if int(m.group(2)) != actual:
                problems.append(f"The report states {m.group(2)} data lines for {log_cfg.get('path')}. "
                                f"The file has {actual}. Correct the report.")
    return problems


def handle_stop(event, c):
    marker = c.marker()
    if marker is None:
        return 0
    max_blocks = c.contract.get("max_blocks", 3)
    if marker.get("status") == "halted":
        problems = ["The run was halted after repeated denials."]
    else:
        problems = check_contract(c, event.get("last_assistant_message") or "")
    if not problems:
        c.trace(event="Stop", decision="allowed", status="satisfied")
        c.clear_marker()
        return 0
    lines = read_lines(c.trace_path)
    since = max([i for i, t in enumerate(lines) if t.get("decision") == "activated"], default=-1)
    checks = sum(1 for t in lines[since + 1:] if t.get("event") == "Stop" and t.get("status") in ("blocked", "escalated"))
    if marker.get("status") != "halted" and checks + 1 < max_blocks:
        reason = ("The verify contract is not satisfied. " + " ".join(problems) +
                  " Read each missing file in full, then give the report again with a `Context read` block that "
                  "states the number of data lines in traces/transition-log.md as read.")
        c.trace(event="Stop", decision="block", status="blocked", blocks=checks + 1, problems=problems)
        emit({"decision": "block", "reason": reason})
        return 0
    c.trace(event="Stop", decision="escalate", status="escalated", blocks=checks + 1, problems=problems)
    c.clear_marker()
    emit({"systemMessage": "Verify contract unmet after " + str(checks + 1) +
          " checks. The run ended and is escalated to the author. Problems: " + " ".join(problems)})
    return 0


def main():
    raw = sys.stdin.read()
    try:
        event = json.loads(raw) if raw.strip() else None
    except ValueError:
        return 0
    if not isinstance(event, dict):
        return 0
    c = Context(event)
    name = event.get("hook_event_name")
    if name == "PreToolUse":
        return handle_pre(event, c)
    if name == "PostToolUse":
        return handle_post(event, c)
    if name == "Stop":
        return handle_stop(event, c)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # never exit 2 by accident: that would block the tool call
        sys.stderr.write(f"verify_contract: internal error: {exc!r}\n")
        sys.exit(1)
