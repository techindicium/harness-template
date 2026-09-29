# PR: Portwell Analytics — DDLC Lifecycle (Module 1) — Grupo 5

---

## Intent

**Result:** A named-state lifecycle model for the Analytics team's monthly figure-production process, with evidence requirements for each transition, declared owners, and documented failure paths.

**Constraints:**
- `portwell-analytics` is read-only throughout. No file in the track repository was modified.
- No code was written to execute the lifecycle. All deliverables are prose, YAML, and Markdown.
- Contradictions between source documents are registered in full; none were resolved by choosing a more plausible version.
- No dates were estimated. Missing facts are recorded as UNKNOWN with the source where the search was conducted.
- No approval is recorded by any skill. Skills prepare decision packages; approvals are human acts.

**Non-goals:**
- No tools, permissions, or state-engine code (Module 2 scope). One exception, recorded under Decision record:
  a PreToolUse hook that refuses Write, Edit, MultiEdit and NotebookEdit under `portwell-analytics/`.
- No fixes to `portwell-analytics` models, tests, or data.
- No resolution of the structural contradiction that prevents `self_service_rate` v3 from being computed (C6).

**Owners:** Gabriel Campos (gabriel.campos@indicium.tech)

**Acceptance criteria (from SPEC §7):**
- `lifecycle.md` with current-process table and proposed lifecycle
- 9 skills in `skills/`, all following the template
- `traces/worked-case.md` with a real item traced end to end
- At least one explicit stop, refusal, or human-decision request in the skills
- PR with design, trace, limitations, and who did what

---

## What's in this PR

| File | What it delivers |
|------|-----------------|
| `track.yaml` | Group, track, team, process, all sources read, contradictions registered, member roles |
| `lifecycle.md` — Part 1 | 10-step current-process table for INCIDENT-03; three information-loss points (P1–P3); observed cost per loss point |
| `lifecycle.md` — Part 2 | 9-stage lifecycle map; 5 exception states; `stateDiagram-v2` Mermaid diagram; full specification of Verify and Approve; premises and limitations; human judgment boundaries; failure-and-recovery table; terminal states |
| `skills/intake/SKILL.md` | Accepts and bounds a work item; escalates on suspected duplicates before any build |
| `skills/context/SKILL.md` | Validates extract period and required fields; blocks on missing `human_edit_material` for v3 — the first hard gate |
| `skills/route/SKILL.md` | Determines build path; detects mart/definition misalignment; checks POLICY-05/06/13 applicability |
| `skills/act/SKILL.md` | Runs `project/run.py`; records definition version in build log |
| `skills/verify/SKILL.md` | Distinguishes shape-test evidence from definition-alignment evidence; blocks Approve on misalignment |
| `skills/approve/SKILL.md` | Assembles decision package only; never records approval; hard stop until named human signs |
| `skills/handoff/SKILL.md` | Delivers as file with provenance header; refuses message delivery; creates consumer log |
| `skills/observe/SKILL.md` | Monitors consumer citations; triggers Recover on definition changes |
| `skills/recover/SKILL.md` | Three paths (rebuild, restatement, retirement); notifies all consumers from Observe log |
| `traces/worked-case.md` | INCIDENT-03: 12-step retrospective trace with 3 catch points; REQUEST-007: 13-step prospective trace with duplicate flag + period gap |
| `notes/source-inventory.md` | 35+ sources from `portwell-analytics`, each with date and author (or UNKNOWN) |
| `notes/findings.md` | 9 sections: described vs. practised process, divergences, 6 contradictions (C1–C6), tracker inconsistencies, what the 6 shape tests verify and cannot see, versioned metrics, manual handoffs, trace candidates |

---

## Design

### Lifecycle overview

The proposed lifecycle has 9 ordered stages and 5 exception states.

```
Intake → Context → Route → Act → Verify → Approve → Handoff → Observe → Recover
```

Exception states reachable from multiple stages: **Blocked**, **Escalated**, **Rejected**, **Correction required**, **Retired**.

Full transition diagram: `lifecycle.md` §3c (Mermaid `stateDiagram-v2`).

### Key design decisions

**Context is the first hard gate.** Before any build starts, the extract period must match the reporting period (using only `extract-manifest.yaml` as the authoritative source — `project/run.py` explicitly does not verify this) and every field required by the current metric definition must be present in the extract CSVs. If either check fails, the item moves to Blocked. This gate is the direct response to three documented failures: the wrong-period build described in the Declan Byrne interview; the missing `human_edit_material` field that makes `self_service_rate` v3 permanently uncomputable with the current extract; and the undocumented v2 fallback that produced INCIDENT-03.

**Verify separates "valid" from "correct."** The 6 existing shape tests in `project/tests/` verify that numbers are of a type that a number should be (range, non-null, referential integrity). They do not check whether the mart implements the current definition, whether the extract covers the correct period, or whether the version cited in the pack matches the version computed. Verify adds three explicit checks beyond the shape tests: (1) mart logic vs. current definition, field by field; (2) extract period vs. reporting period; (3) required fields present in extract. All three must pass before the item reaches Approve. Source: Declan Byrne interview; `notes/findings.md` §"O que os 6 testes verificam."

**Approve is a human-only act.** The `approve` skill assembles the decision package (number + metric name + version + period + extract date + build log + test results + definition-alignment report). It stops. A named person reviews the package and records `approved_by` and `approved_at`. The skill never writes these fields. This is the direct response to POLICY-06 (named approver for destructive transforms) and to the Approve stage's stated purpose: "the number is correct, not just valid."

**Handoff mandates file delivery with provenance.** The `handoff` skill refuses to deliver figures as a message or paste. The delivery file includes a provenance header with metric name, version, period, extract date, and approver name. This is the enforcement point for POLICY-13, which the current pipeline does not enforce. The consumer log created at Handoff is the mechanism that makes POLICY-05 (notify consumers one period ahead of definition changes) achievable — it does not exist today (ISSUE-30 in `data/tracker.csv`).

---

## Evidence

### Red — where the current process lost information

**P1 — Definition and code desynchronised** (`lifecycle.md` Part 1, step 2):
`self_service_rate` v3 was declared current on 2026-07-01 (`project/metrics/metric-definitions.yaml`). The mart (`project/models/marts/self_service.sql`) and staging model (`stg_suggestions.sql`: `CAST(sent AS BOOLEAN) AS is_self_served`) were never updated. The intent to update was recorded only as text in a PR note (`docs/pr-notes/0088-self-service-v3.md`: "noticed and left") with no ticket, no owner, and no follow-up date. Every figure produced since 2026-07-01 uses v2 logic while the definition declares v3 as current.

**P2 — Figures delivered without version metadata** (`lifecycle.md` Part 1, step 6):
No mart emits a version field. POLICY-13 (`docs/policies.md`) requires that figures in packs cite the metric name and version. No artefact enforces this. When Sunder Retail Supply asked why their self-service number changed, nobody could answer from evidence — only from memory. Source: `docs/interviews/2026-08-12 Declan Byrne...`: "if someone asks in three months where a number came from, I have a message and a memory."

**P3 — No consumer list** (`lifecycle.md` Part 1, step 3):
POLICY-05 requires announcing definition changes one reporting period ahead. This is structurally impossible without knowing who consumes each metric. No consumer list exists. Source: ISSUE-30 in `data/tracker.csv` ("No list of who consumes which metric"), `docs/incidents/INCIDENT-03.md` ("Nobody was told").

### Green — how the proposed lifecycle detects or blocks each loss point

**P1 → Context field check** (`traces/worked-case.md`, INCIDENT-03 trace step 3):
The Context skill reads required fields from `project/metrics/metric-definitions.yaml` and compares them with the column list in the extract CSV. `human_edit_material` is absent from `data/ops-extract/suggestion.csv`. The skill stops; the build does not start; a human decision is required before any number is produced. The undocumented fallback to a superseded definition is eliminated.

**P1 → Route alignment check** (`skills/route/SKILL.md`, step 2):
Even if the Context decision cleared the item for a v2 run, Route reads the mart SQL and compares the implementation with the authorised definition version. If they differ without an explicit human decision on file, the item is escalated before Act.

**P2 → Approve package + Handoff provenance** (`traces/worked-case.md`, INCIDENT-03 trace steps 9 and 11):
The Approve package states `definition_version_in_effect` and `policy_13_citation` explicitly. The approver sees which version they are signing. The Handoff delivery file carries `version: v2` in its header. When a consumer receives figures, the version is visible. The investigation triggered by a version question takes minutes, not two days.

**P3 → Handoff consumer log** (`skills/handoff/SKILL.md`, step 6):
The consumer log is created at the first Handoff and maintained at every subsequent delivery. This is the mechanism that makes POLICY-05 actionable — for the first time, there is a list of who received which version for which period.

### Held-out — REQUEST-007

REQUEST-007 (Lucia Ferreira, Reporting, self-service per account for August 2026 packs, deadline 2026-09-04) was not used to design the lifecycle. Source: `data/requests/REQUEST-007.docx`, `data/requests/inbox.csv`.

The lifecycle covers it, surfacing two issues that INCIDENT-03 did not expose:

1. **Duplicate flag at Intake:** REQUEST-007 and REQUEST-011 have the same deadline and overlapping summaries. The tracker note records: "ninguém perguntou se eles querem o mesmo número" (`data/tracker.csv`). The Intake skill escalates before any work begins. Resolution is UNKNOWN at time of writing.

2. **Extract coverage gap at Context:** The August extract manifest declares coverage through 2026-08-28. August ends 2026-08-31 — three days short. The current process has no period check (`project/run.py` docstring: "Nothing here compares that date to the period being reported on"). The Context skill catches the gap and requires clarification before proceeding.

3. **Same structural block as INCIDENT-03:** `human_edit_material` absent from extract → blocked at Context for v3. This confirms the constraint is systemic, not a one-off.

Full trace: `traces/worked-case.md` §"Trace 2 — Held-out: REQUEST-007."

---

## Integration

**Shared interfaces respected:**
- Track repository accessed read-only throughout. No commits, edits, or writes to `portwell-analytics`.
- Skill evidence artifacts are produced in the harness (`claude_ddlc/evidence/`), not in the track repository.
- Lifecycle states, exception states, and evidence artifact names follow the patterns defined in the harness template.

**New artifact introduced:**
- `evidence/consumer-log.md`: the consumer log created at Handoff and maintained by Observe. This artifact does not exist in `portwell-analytics` today (ISSUE-30). Future modules that implement POLICY-05 enforcement will need to read from this log.

**Dependencies on other groups/tracks:**
- The Portwell help portal (`ops.suggestion` table) is the upstream source of the extract data. Changes to the portal schema (e.g., adding `human_edit_material`) would unblock `self_service_rate` v3 for every team consuming it. No cross-group coordination was required in Module 1 scope.

---

## Limitations & open risks

| Item | Detail | Source |
|------|--------|--------|
| C6 — Real cause of INCIDENT-03 is UNKNOWN | The attributed cause (v2→v3 transition) is structurally impossible; v3 was never computable; the actual reason the Sunder Retail Supply figure changed is not established | `notes/findings.md` §C6; `data/ops-extract/suggestion.csv`; `project/models/staging/stg_suggestions.sql` |
| Analytics lead name is UNKNOWN | Approve requires a named approver; POLICY-06 requires a named approver for destructive transforms; the Analytics lead who wrote INCIDENT-03 is not identified | `docs/incidents/INCIDENT-03.md` |
| `self_service_rate` v3 structurally blocked | Every request for v3 will block at Context until `data/ops-extract/suggestion.csv` includes `human_edit_material`; this requires a change to the extract query and to the operational database schema | `data/ops-extract/suggestion.csv`; `project/metrics/metric-definitions.yaml` |
| Consumer log does not exist today | The first real execution of the lifecycle must retroactively populate it with the three consumers identified in INCIDENT-03 | ISSUE-30, `data/tracker.csv`; `docs/incidents/INCIDENT-03.md` |
| `suggestion_acceptance_rate` v1 has no mart | Any request for this metric blocks at Route (no implementation to build from) | `project/metrics/metric-definitions.yaml`; glob of `project/models/marts/` |
| `docs/systems.md` not found | Phase 0 required reading this file; it does not exist in the track repository. System information derived from interview and incident sources only | `docs/` directory listing |
| `course-shared/tools/mock-systems.json` not found | Separate repository not cloned; systems list in `track.yaml` marked UNKNOWN | Phase 0 notes |
| `docs/data-dictionary.xlsx` not read | Binary format; alignment between data dictionary and current models not verified | `notes/source-inventory.md` |
| Lifecycle is descriptive only (Module 1) | All transitions depend on human discipline. No state engine enforces them. Each "stop" in a skill is a documented instruction, not a technical block | SPEC §1 non-goals |

**Contradictions registered but not resolved:**
C1 (mart v2 vs. definition v3), C2 (incident index incomplete), C3 (REQUEST-007/011 possible duplicate), C4 (extract period not compared to reporting period in pipeline), C5 (POLICY-13 not enforced by any mart), C6 (INCIDENT-03 root-cause attribution structurally impossible). Full details: `notes/findings.md` §Contradições.

---

## Decision record

**The read-only hook is kept, and fixed, ahead of Module 2.** The first version never blocked: it read
`file_path` at the top of the payload instead of `tool_input.file_path`, exited 1 (only exit 2 blocks),
and used `onFailure` and `blockMessage`, which are not hook fields. Keeping a control the PR declares,
rather than deleting it, was the group's choice; the trade-off is building one Module 2 interception
point early. What it still does not cover (Bash writes, sessions opened inside the track repository) is
in `notes/findings.md` under "Controle de leitura do track (hook)".

---

## Next improvement

The executable lifecycle (Module 2) would add:

1. **State engine:** transitions enforced by code, not just documented in prose. A skill that "proposes" a state cannot be overridden silently.
2. **Automated field-presence check in Context:** replace manual column inspection with a schema comparison between the extract CSV headers and the current metric definition's required fields. This would catch the `human_edit_material` absence automatically.
3. **Version citation injected at Act:** the build log currently requires the operator to manually record `definition_version_in_effect`. In Module 2, `run.py` would emit this field into the mart output directly, making POLICY-13 compliance automatic.
4. **Consumer log as a queryable artifact:** the current consumer log is a Markdown file. Module 2 would make it a structured CSV or database table that Observe and Recover can query by metric, version, and period — enabling automated notification drafts when a definition changes.
5. **Named approver slot enforced by the harness:** the `approve` skill currently leaves `approved_by` blank and waits. Module 2 would gate the Handoff transition on this field being non-empty, enforcing the rule mechanically rather than by instruction.

---

## Who did what

| Person | Contribution |
|--------|-------------|
| Gabriel Campos | Read and inventoried all 35+ track-repo sources; identified 6 contradictions (C1–C6) including the structurally impossible root cause in INCIDENT-03 (C6); designed the 9-stage lifecycle and 5 exception states; wrote all deliverables: `lifecycle.md` (Parts 1 and 2), 9 skill files, `traces/worked-case.md`, `notes/source-inventory.md`, `notes/findings.md`, `track.yaml`, and this PR description |
