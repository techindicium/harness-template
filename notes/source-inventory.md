# Source Inventory

Generated during Phase 1 reading. All files from `portwell-analytics` (TRACK_REPO), read-only.

| Fonte | O que contém | Data | Autor |
|-------|-------------|------|-------|
| `docs/how-we-work-today.md` | Descrição do processo atual: 6 passos, tabela "onde as coisas estão escritas", julgamentos não documentados | UNKNOWN | UNKNOWN |
| `docs/interviews/2026-08-12 Declan Byrne, where the numbers come from.docx` | Entrevista de 50 min com Data Engineer: extract manual, build, handoff para Reporting | 2026-08-12 | Mei Tan (interviewer); Declan Byrne (entrevistado) |
| `data/tracker.csv` | 10 itens (6 issues, 4 requests) com tipo, status, owner, datas e notas | UNKNOWN | UNKNOWN |
| `docs/incidents/README.md` | Índice de incidentes — lista apenas INCIDENT-01 e INCIDENT-02 | UNKNOWN | UNKNOWN |
| `docs/incidents/INCIDENT-01.md` | Artigo supersedido chegou ao cliente (billing, 30-day vs 60-day refund) | 2026-07-14 | UNKNOWN (on call) |
| `docs/incidents/INCIDENT-02.md` | Conselho de retry parou feed EDI de conta Enterprise por quase um dia | 2026-07-29 | Solution consultant (não nomeado) |
| `docs/incidents/INCIDENT-03.md` | Número de self-service mudou entre junho e julho sem aviso aos consumidores | 2026-08-06 | Analytics lead (não nomeado) |
| `data/ops-extract/extract-manifest.yaml` | Metadados do último extract: fonte, taken_at, taken_by, method, row_counts, cobertura | 2026-08-28T09:14:00Z | Declan Byrne |
| `data/ops-extract/account.csv` | 10 contas: account_id, name, tier, region, seats, modules, pilot | UNKNOWN | UNKNOWN |
| `data/ops-extract/tier_commitment.csv` | Compromissos de SLA por tier: first_response_mins, resolution_hours, human_review_areas | UNKNOWN | UNKNOWN |
| `data/ops-extract/ticket.csv` | 1.234 tickets de suporte (row count do manifest) | UNKNOWN | UNKNOWN |
| `data/ops-extract/interaction.csv` | 2.468 interações de suporte | UNKNOWN | UNKNOWN |
| `data/ops-extract/suggestion.csv` | 533 sugestões do portal | UNKNOWN | UNKNOWN |
| `project/models/staging/stg_accounts.sql` | Modelo staging: lê de ops.account, cast pilot para BOOLEAN | UNKNOWN | UNKNOWN |
| `project/models/staging/stg_extract_metadata.sql` | Modelo staging: registra source, extracted_at, source_tickets | UNKNOWN | UNKNOWN |
| `project/models/staging/stg_interactions.sql` | Modelo staging: interações | UNKNOWN | UNKNOWN |
| `project/models/staging/stg_suggestions.sql` | Modelo staging: sugestões | UNKNOWN | UNKNOWN |
| `project/models/staging/stg_tickets.sql` | Modelo staging: tickets | UNKNOWN | UNKNOWN |
| `project/models/staging/stg_tier_commitments.sql` | Modelo staging: tier commitments | UNKNOWN | UNKNOWN |
| `project/models/marts/self_service.sql` | Mart: self_service_rate por account-month; usa `is_self_served` (lógica v2) | UNKNOWN | UNKNOWN |
| `project/models/marts/first_response.sql` | Mart: first_response_minutes por ticket e mediana por account-month (p50) | UNKNOWN | UNKNOWN |
| `project/models/marts/sla_attainment.sql` | Mart: SLA attainment por account-month vs tier commitment | UNKNOWN | UNKNOWN |
| `project/tests/accepted_values_tier.sql` | Teste de forma: tier pertence a {standard, business, enterprise} | UNKNOWN | UNKNOWN |
| `project/tests/first_response_positive.sql` | Teste de forma: first_response_minutes >= 0 | UNKNOWN | UNKNOWN |
| `project/tests/no_null_self-service_for_pilot.sql` | Teste de forma: contas pilot têm self_service_rate não-nulo a partir de 2026-07 | UNKNOWN | UNKNOWN |
| `project/tests/not_null_self-service_account.sql` | Teste de forma: rows de self_service têm account_id | UNKNOWN | UNKNOWN |
| `project/tests/referential_ticket_account.sql` | Teste de forma: todo ticket aponta para account existente | UNKNOWN | UNKNOWN |
| `project/tests/self_service_rate_in_range.sql` | Teste de forma: self_service_rate em [0,1] para contas pilot a partir de 2026-07 | UNKNOWN | UNKNOWN |
| `project/metrics/metric-definitions.yaml` | 4 métricas: self_service_rate v2 (superseded) e v3 (current), first_response_minutes_p50 v1, suggestion_acceptance_rate v1 | 2026-08-20 | Sofia Marques |
| `data/requests/inbox.csv` | 11 requests: id, from_team, requester, received, needed_by, status, summary | UNKNOWN | UNKNOWN |
| `data/requests/REQUEST-007.docx` | Request de Lucia Ferreira (Reporting): self-service por conta para agosto; não especifica versão da definição | 2026-08-11 | Lucia Ferreira |
| `data/requests/REQUEST-011.docx` | Request de Henrik Sole (Reporting): "automation rate" por conta Enterprise para agosto; possível duplicata de REQUEST-007 não investigada | 2026-08-18 | Henrik Sole |
| `data/requests/REQUEST-005.docx` | Request de Product (Ana Fialho): pilot accounts resolvem mais rápido que não-pilot | UNKNOWN (received 2026-07-30) | Ana Fialho |
| `data/requests/REQUEST-009.docx` | Request de Product (Gabriela Rocha): número para conversa de renovação Nordkai | UNKNOWN (received 2026-08-14) | Gabriela Rocha |
| `docs/data-dictionary.xlsx` | Dicionário de dados, lido como zip: 10 colunas descritas na aba 1 e lacunas conhecidas na aba 2; divergências registradas em C12 | 2026-05-12 (última revisão completa, aba 2) | UNKNOWN ("Kept by hand") |
| `docs/dependencies.md` | O que o track consome (banco operacional) e publica (definições, três marts sem contrato); a lista de consumidores que não existe | UNKNOWN | UNKNOWN |
| `docs/architecture-rules.md` | Seis regras, uma só com enforcement; tabela de blast radius | UNKNOWN | UNKNOWN |
| `docs/backlog.md` | ISSUE-30 a ISSUE-39, com owner e notas; ISSUE-34 e ISSUE-38 sem owner | UNKNOWN | UNKNOWN |
| `data/README.md` | Descrição genérica dos dados, com o bloco SEED não preenchido | UNKNOWN | UNKNOWN |
| `docs/pr-notes/0088-self-service-v3.md` | Nota de mudança: self_service v3 merged 2026-06-27, effective 2026-07-01; mart não atualizado | 2026-06-27 (merged) | Sofia Marques (autor); Declan Byrne (reviewer) |
| `docs/policies.md` | 4 políticas formais (POLICY-03, 05, 06, 13) + regras de hábito; nenhuma é enforced pelo código | UNKNOWN | UNKNOWN |
| `docs/identifiers.md` | Esquema de identificadores: owned (REQUEST-NNN, metric name+version) e borrowed (ACCOUNT, TICKET, SUGGESTION) | UNKNOWN | UNKNOWN |

**Nota:** `docs/interviews/` contém arquivo .docx não legível diretamente pelo Read tool; conteúdo extraído via zip/XML parsing. `docs/data-dictionary.xlsx` foi lido da mesma forma (zip/XML).

## Fontes de outros tracks

Lidas sem alteração em 2026-09-29, para registrar dependências e testar figuras publicadas.

| Fonte | O que contém | Data | Autor |
|-------|-------------|------|-------|
| `../portwell-knowledge/data/figures/warehouse-export-2026-08-01.csv` | Julho, "first cut": três contas Enterprise, SLA, self-service e p50 | 2026-08-01 (`# sent:`) | Declan Byrne (`# from:`) |
| `../portwell-knowledge/data/figures/warehouse-export-2026-08-06.csv` | Julho de novo, "A late batch of tickets landed after the first cut. Use this one." | 2026-08-06 (`# sent:`) | Declan Byrne (`# from:`) |
| `../portwell-knowledge/data/figures/warehouse-export-2026-08-29.csv` | Agosto, "August figures for the packs" | 2026-08-29 (`# sent:`) | Declan Byrne (`# from:`) |
| `../portwell-knowledge/data/packs/2026-07/ACCOUNT-1008-2026-07.xlsx` e `.docx` | Pack de julho da Sunder: attainment 0.2696, p50 70, self-service 0.3478, self-service anterior 0, "automation rate" 41 por cento, ESCALATION-0421 | UNKNOWN | Lucia Ferreira ("Prepared by") |
| `../portwell-knowledge/docs/dependencies.md` | Como knowledge recebe as figuras: CSV ou mensagem, sem versão, sem registro de qual export gerou cada pack | UNKNOWN | UNKNOWN |
| `../portwell-knowledge/docs/backlog.md` | ISSUE-52, self-service contra automation rate | UNKNOWN | UNKNOWN |
| `../portwell-engineering/docs/dependencies.md` | O banco operacional publicado para analytics sem contrato; definições de métrica lidas sem fixar versão | UNKNOWN | UNKNOWN |
| `../portwell-engineering/docs/backlog.md` | ISSUE-13, "No link between an escalation and its issue" (C13) | UNKNOWN | UNKNOWN |
| `../portwell-product/docs/Policies.docx` | POLICY-11, citado pelo REQUEST-009 e ausente de `docs/policies.md` deste track (C14) | 2026-06-02 ("Last reviewed") | Ana Fialho ("Maintained by") |
