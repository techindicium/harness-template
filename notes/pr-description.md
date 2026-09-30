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
- No resolution of the contradiction about what moved the Sunder Retail Supply figure (C6, C15).
- No fix to the marts: C7 and C8 are recorded, and the executed trace escalates them to the Analytics team.

**Owners:** Gabriel Campos (gabriel.campos@indicium.tech), Yuri Alves (yuri.alves@indicium.ai), Eric Batista (eric.batista@indicium.ai)

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
| `traces/worked-case.md` | INCIDENT-03: 12-step counterfactual trace with 3 catch points; REQUEST-007: 7-step trace executed through the skills, ending Escalated at Verify with Approve refusing |
| `evidence/*-REQUEST-007.md` | What each skill wrote when it ran: intake, context, route, build (with the full `run.py` output), verify, and the approve refusal |
| `.claude/settings.json` | PreToolUse hook that refuses Write, Edit, MultiEdit and NotebookEdit under `portwell-analytics/` (see Decision record) |
| `notes/source-inventory.md` | 35+ sources from `portwell-analytics`, each with date and author (or UNKNOWN) |
| `notes/findings.md` | Described vs. practised process, divergences, 15 contradictions (C1–C15), dependencies on other tracks, the read-only hook, what the executed trace showed about the skills, tracker inconsistencies, what the 6 shape tests verify and cannot see, versioned metrics, manual handoffs, trace candidates |

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

### Red, measured — the published figures do not rebuild

`make build` on the track repository passes all 6 tests, and it does not reproduce what Reporting
received. `marts/first_response.sql` counts `actor IN ('agent', 'portal')`, and the extract names
the portal's reply `assist`, so 296 of 1234 tickets drop out of first response and SLA attainment
(C7).

| Export (`../portwell-knowledge/data/figures/`) | Account | Field | Published | Today |
| :- | :- | :- | -: | -: |
| `warehouse-export-2026-08-06.csv` (July) | ACCOUNT-1008 | attainment | 0.2696 | 0.08 |
| `warehouse-export-2026-08-06.csv` (July) | ACCOUNT-1008 | first_response_p50 | 70 | 103 |
| `warehouse-export-2026-08-29.csv` (August) | ACCOUNT-1008 | attainment | 0.3966 | 0.0952 |

Across both exports, self-service matches 6 of 6 and the other figures differ 18 of 18. Counting
`assist` as a response reproduces all of them. The same 6 tests also pass on empty tables (C9).

### Green — how the proposed lifecycle detects or blocks each loss point

**P1 → Context field check** (`traces/worked-case.md`, INCIDENT-03 trace step 3):
The Context skill reads required fields from `project/metrics/metric-definitions.yaml` and compares them with the column list in the extract CSV. `human_edit_material` is absent from `data/ops-extract/suggestion.csv`. The skill stops; the build does not start; a human decision is required before any number is produced. The undocumented fallback to a superseded definition is eliminated.

**P1 → Route alignment check** (`skills/route/SKILL.md`, step 2):
Even if the Context decision cleared the item for a v2 run, Route reads the mart SQL and compares the implementation with the authorised definition version. If they differ without an explicit human decision on file, the item is escalated before Act.

**P2 → Approve package + Handoff provenance** (`traces/worked-case.md`, INCIDENT-03 trace steps 9 and 11):
The Approve package states `definition_version_in_effect` and `policy_13_citation` explicitly. The approver sees which version they are signing. The Handoff delivery file carries `version: v2` in its header. When a consumer receives figures, the version is visible. The investigation triggered by a version question takes minutes, not two days.

**P3 → Handoff consumer log** (`skills/handoff/SKILL.md`, step 6):
The consumer log is created at the first Handoff and maintained at every subsequent delivery. This is the mechanism that makes POLICY-05 actionable — for the first time, there is a list of who received which version for which period.

### Second case, executed — REQUEST-007

REQUEST-007 (Lucia Ferreira, Reporting, self-service per account for the August 2026 packs) was not
used to design the lifecycle. It was run through the skills on 2026-09-29, and each skill wrote its
evidence under `evidence/`. Human stops were answered by a group member playing the named role,
marked `simulated: true`.

1. **Intake stops** on a suspected duplicate of REQUEST-011. The question is deferred, not resolved.
2. **Context stops twice:** the extract ends on 2026-08-27, and `human_edit_material` (v3) is absent.
   The simulated decisions label the figures as partial August and compute v2.
3. **Route stops** on POLICY-05: the v3 change was never announced and there is no consumer list.
4. **Act builds**: exit 0, all 6 tests pass.
5. **Verify blocks**: v2 differs from the mart on denominator and period (C8), and the skill's own
   first-response check finds the dropped `assist` actor (C7).
6. **Approve refuses**: no package, no `approved_by`.

Final state: Escalated to the Analytics team. Nothing was delivered. Full trace:
`traces/worked-case.md` §"Trace 2 — Executed: REQUEST-007".

---

## Integration

**Shared interfaces respected:**
- Track repository accessed read-only throughout. No commits, edits, or writes to `portwell-analytics`.
- Skill evidence artifacts are produced in the harness (`evidence/`), not in the track repository. Running the build writes `warehouse.duckdb` and `.venv/` in the track root; both are gitignored, and `git status` there stayed empty.
- Lifecycle states, exception states, and evidence artifact names follow the patterns defined in the harness template.

**New artifact designed, not yet produced:**
- `evidence/consumer-log.md`: the consumer log the `handoff` skill creates and `observe` maintains. This artifact does not exist in `portwell-analytics` today (ISSUE-30), and the executed REQUEST-007 trace does not create it either: Verify blocked the item before Approve, so it never reached Handoff (`traces/worked-case.md` §"Trace 2 — Executed"). The design is in `skills/handoff/SKILL.md`; the first real Handoff run is what will produce this file.

**Dependencies on other groups/tracks:**
- **Engineering** publishes the operational database with no written contract (`../portwell-engineering/docs/dependencies.md`). A value rename there (C7) and a missing field (`human_edit_material`) both reach this track silently.
- **Knowledge and Reporting** consume our figures as CSV or pasted numbers, with no version, and cannot say which export a pack was built from (`../portwell-knowledge/docs/dependencies.md`). Their ISSUE-52 and our REQUEST-011 are the same open question.
- **Product** consumes figures by request (REQUEST-005, REQUEST-009). POLICY-11, cited by REQUEST-009, is defined in `../portwell-product/docs/Policies.docx` and does not cover what was sent (C14).
- INCIDENT-03 cites `ISSUE-13` in the Portal engineering backlog as the same problem; `ISSUE-13` there is a different problem (C13).
- Full table: `notes/findings.md` §"Dependências com outros tracks".

---

## Limitations & open risks

| Item | Detail | Source |
|------|--------|--------|
| C6 — Real cause of INCIDENT-03 is UNKNOWN | The attributed cause (v2→v3) conflicts with change note 0088 (mart still on v2) and with the July pack (self-service 0 to 0.3478); the July extract's columns are UNKNOWN; the ticket the incident cites was opened later, about the dashboard (C15) | `notes/findings.md` §C6, §C15 |
| Analytics lead name is UNKNOWN | Approve requires a named approver; POLICY-06 requires a named approver for destructive transforms; the Analytics lead who wrote INCIDENT-03 is not identified | `docs/incidents/INCIDENT-03.md` |
| `self_service_rate` v3 structurally blocked | Every request for v3 will block at Context until `data/ops-extract/suggestion.csv` includes `human_edit_material`; this requires a change to the extract query and to the operational database schema | `data/ops-extract/suggestion.csv`; `project/metrics/metric-definitions.yaml` |
| Consumer log does not exist today | The first real execution of the lifecycle must retroactively populate it with the three consumers identified in INCIDENT-03 | ISSUE-30, `data/tracker.csv`; `docs/incidents/INCIDENT-03.md` |
| `suggestion_acceptance_rate` v1 has no mart | Any request for this metric blocks at Route (no implementation to build from) | `project/metrics/metric-definitions.yaml`; glob of `project/models/marts/` |
| `docs/systems.md` not found | Phase 0 required reading this file; it does not exist in the track repository. System information derived from interview and incident sources only | `docs/` directory listing |
| `course-shared/tools/mock-systems.json` not found | Separate repository not cloned; systems list in `track.yaml` marked UNKNOWN | Phase 0 notes |
| `docs/data-dictionary.xlsx` is out of date | Read as a zip; at least four divergences from the models | `notes/findings.md` §C12 |
| Published figures do not rebuild | SLA attainment and p50 in the packs cannot be reproduced from the repository today; fixing it means changing the track's marts | `notes/findings.md` §C7 |
| Human decisions in the executed trace are simulated | A group member played Declan Byrne, Sofia Marques and Lucia Ferreira; none of those decisions was taken by them | `evidence/*-REQUEST-007.md` |
| The executed trace stops at Verify | Handoff, Observe and Recover have not run against a real item | `traces/worked-case.md` Trace 2 |
| The hook does not cover Bash writes | `sed -i`, redirects or scripts can still write into the track; sessions opened inside the track use its own permissions | `notes/findings.md` §"Controle de leitura do track (hook)" |
| Lifecycle is descriptive only (Module 1) | All transitions depend on human discipline. No state engine enforces them. Each "stop" in a skill is a documented instruction, not a technical block | SPEC §1 non-goals |

**Contradictions registered but not resolved:**
C1 (mart v2 vs. definition v3), C2 (incident index incomplete), C3 (REQUEST-007/011 possible duplicate), C4 (extract period not compared to reporting period in pipeline), C5 (POLICY-13 not enforced by any mart), C6 (INCIDENT-03 cause conflicts with change note 0088 and the July pack), C7 (first response drops the `assist` actor; published figures do not rebuild), C8 (v2 denominator, period and grain differ from the mart), C9 (the 6 tests pass on empty tables), C10 (extract_metadata records build time), C11 (course layer on where the harness lives), C12 (data dictionary), C13 (ISSUE-13), C14 (POLICY-11 against REQUEST-009), C15 (TICKET-004424 against INCIDENT-03). Full details: `notes/findings.md` §Contradições.

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
6. **Recover exercised after a clean Handoff:** the INCIDENT-03 trace now shows that version provenance alone does not close a consumer magnitude dispute — Observe → Recover still needs a human path choice when root cause remains UNKNOWN (C6).

---

## Who did what

| Person | Contribution |
|--------|-------------|
| Gabriel Campos | Read and inventoried all 35+ track-repo sources; identified 6 contradictions (C1–C6), including the INCIDENT-03 root-cause question later narrowed in C6; designed the 9-stage lifecycle and 5 exception states; wrote all deliverables: `lifecycle.md` (Parts 1 and 2), 9 skill files, `traces/worked-case.md`, `notes/source-inventory.md`, `notes/findings.md`, `track.yaml`, and this PR description |
| Yuri Alves | Ran the build and compared the warehouse with the figures Reporting received (C7); narrowed C6 and added C8 to C15 with the dependencies on other tracks; fixed the read-only hook and recorded the decision; restored the template keys in `track.yaml` and the template columns in `lifecycle.md`; ran REQUEST-007 through the skills and wrote `evidence/*-REQUEST-007.md`; recorded the skill gaps the run exposed |
| Eric Batista | Reviewed deliverables against the Module 1 activity guide; aligned `evidence/consumer-log.md` path in `lifecycle.md` with the skills; extended the INCIDENT-03 counterfactual with Observe → Correction required → Recover (catch point 4); generalised `context` / `verify` / `route` beyond `self_service_rate`-only wording |
