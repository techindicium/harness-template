# Findings

Generated during Phase 1 reading. Every claim cites its source. Unknown facts are marked UNKNOWN.
Contradictions are registered in full, not resolved.

---

## Processo descrito

Source: `docs/how-we-work-today.md`

1. Um request chega de outro time — geralmente via mensagem, às vezes em reunião.
2. É registrado em `data/requests/inbox.csv`. Alguns requests nunca chegam lá.
3. Alguém descobre o que o request realmente significa. "Isso é a parte difícil e não deixa registro."
4. Essa pessoa escreve ou estende um modelo em `project/models/`, roda `project/run.py` e lê o número.
5. O número é enviado de volta, geralmente colado em mensagem ou planilha.
6. Se uma definição mudou, quem consumia o número antigo descobre quando um cliente pergunta.

**Refresh mensal:** `project/run.py` deveria rodar no início de cada mês. Não há schedule. Roda quando alguém lembra, ou quando Reporting pergunta por que o número parece do mês passado. (`docs/how-we-work-today.md`)

---

## Processo praticado

Source principal: `docs/interviews/2026-08-12 Declan Byrne, where the numbers come from.docx`
Fontes secundárias: `docs/incidents/`, `docs/pr-notes/0088-self-service-v3.md`

1. **Extract (entrada manual):** O banco operacional fica em um servidor que Declan não acessa diretamente. Alguém do suporte — "geralmente Joao", mas variou entre 3 pessoas em 2 anos — roda uma query em um documento e exporta CSVs para uma pasta compartilhada. Há um documento com a query que pode estar desatualizado: "eu mudei duas vezes e não sei se os dois têm a versão nova" (Declan Byrne, entrevista).
2. **Verificação do extract:** Declan verifica o manifest de olho. "O load cair é o check" — se as colunas forem diferentes (query velha), o pipeline quebra. Isso já falhou uma vez: em uma ocasião, o build foi feito com o extract do mês anterior porque a pasta não havia sido atualizada. "Os números pareciam plausíveis, que é o problema. Lucia pegou porque uma conta que ela sabia que tinha tido um mês ruim estava parecendo bem." (entrevista)
3. **Build:** Um comando (run.py): carrega extract → tabelas de staging → marts → testes. "Essa parte está boa." (Declan, entrevista)
4. **Testes:** São testes de forma. "Eles verificam os shapes. Contagens de linhas não são zero, sem chaves duplicadas, percentuais entre zero e um. Eles não verificam se o número está certo, só se é do tipo que um número deveria ser." (entrevista)
5. **Handoff (saída manual):** Declan entrega CSV para Lucia Ferreira (Reporting). Se ela precisar rápido, cola em mensagem. "Eu sei que isso é pior. Porque aí não tem arquivo. Se alguém perguntar em três meses de onde veio um número, eu tenho uma mensagem e uma memória." (entrevista)
6. **Downstream:** O mart não carrega a versão da definição que usou. POLICY-13 exige que figuras em packs citem a versão; marts emitem números sem versão. (`docs/policies.md`)

---

## Divergências

Onde o processo descrito e o praticado não batem.

| # | Descrito (`how-we-work-today.md`) | Praticado (entrevista + incidentes) |
|---|----------------------------------|--------------------------------------|
| D1 | "Alguém trabalha o que o request significa" — sem dizer quem | Declan faz essa interpretação sozinho, sem registro. "O que um request realmente significa não existe em nenhum lugar." (`how-we-work-today.md`) |
| D2 | O processo começa com o request chegando e sendo registrado | O extract precede e independe do request; é disparado pelo calendário (mês fechando), não pelo request. A entrevista não menciona o tracker como disparador. |
| D3 | O processo descrito omite completamente o extract como etapa explícita | A entrevista descreve o extract como a etapa mais frágil: pessoa variável, query possivelmente desatualizada, verificação manual do manifest |
| D4 | Implica um artefato único de entrega ("o número é enviado") | Na prática: às vezes CSV (rastreável), às vezes mensagem (não rastreável). Declan reconhece que mensagem "é pior". |
| D5 | "Se uma definição mudou, quem consumia o número antigo descobre quando um cliente pergunta" — enquadrado como problema | O processo descrito não apresenta nenhum mecanismo para evitar isso; INCIDENT-03 confirma que o problema se materializou |

---

## Contradições

Formato: `CONTRADICTION: <fonte A> diz X; <fonte B> diz Y.`

**C1 — Mart vs. definição vigente:**
CONTRADICTION: `docs/pr-notes/0088-self-service-v3.md` diz que a intenção era atualizar `marts/self_service.sql` após junho fechar; `project/models/marts/self_service.sql` usa `is_self_served` (lógica da definição v2); `project/metrics/metric-definitions.yaml` (published_at 2026-08-20) tem `self_service_rate` v3 como current desde 2026-07-01. O mart está implementando uma definição supersedida há pelo menos 2 meses.

**C2 — Registro de incidentes incompleto:**
CONTRADICTION: `docs/incidents/README.md` lista apenas INCIDENT-01 e INCIDENT-02 como incidentes existentes; `docs/incidents/INCIDENT-03.md` existe no mesmo diretório com data 2026-08-06.

**C3 — REQUEST-007 vs. REQUEST-011:**
CONTRADICTION: `data/tracker.csv` (nota de ISSUE-36) diz "REQUEST-007 e REQUEST-011 podem ser o mesmo número"; `data/requests/REQUEST-011.docx` diz que Henrik chama de "automation rate" e Lucia chama de "self-service" e que "ninguém perguntou se eles querem o mesmo número"; os dois têm deadline 2026-09-04 e ambos estão abertos. Não há registro de verificação.

**C4 — Período do extract vs. período de reporte:**
CONTRADICTION: `data/ops-extract/extract-manifest.yaml` descreve o extract como "Covers tickets opened before 2026-08-28" (sem limite inferior); a entrevista (Declan Byrne) relata que em uma ocasião o build foi feito com o extract do mês anterior sem que ninguém percebesse antes do número parecer errado. Nenhum mecanismo no pipeline compara o período do extract com o período de reporte.

**C6 — Causa-raiz de INCIDENT-03 estruturalmente impossível:**
CONTRADICTION: `docs/incidents/INCIDENT-03.md` (2026-08-06) atribui a mudança do número de self-service à transição v2→v3 da definição em 2026-07-01; `project/models/staging/stg_suggestions.sql` computa `is_self_served = CAST(sent AS BOOLEAN)` (lógica v2 pura); `data/ops-extract/suggestion.csv` tem colunas `suggestion_id, ticket_id, created_at, article_ids, confidence, route, route_reason, sent` — o campo `human_edit_material` exigido pela definição v3 não existe no extract nem no staging model. V3 **nunca pôde ser computado** com o extract atual. A equipe investigou durante dois dias uma causa que o pipeline não tem condições de produzir. A razão real da mudança do número de Sunder Retail Supply permanece UNKNOWN.

**C5 — POLICY-13 vs. output dos marts:**
CONTRADICTION: `docs/policies.md` POLICY-13 exige que "toda figura em pack voltado ao cliente nomeie a definição de métrica e a versão com que foi calculada"; `project/models/marts/self_service.sql` emite `self_service_rate` sem qualquer campo de versão; `docs/policies.md` confirma: "Marts emitem números sem versão."

**C7 — First response descarta o actor `assist`, e os números publicados não se reproduzem:**
CONTRADICTION: `project/metrics/metric-definitions.yaml` define `first_response_minutes_p50` v1 como "minutes between ticket creation and the first outbound interaction"; `project/models/marts/first_response.sql:10` conta como saída apenas `actor IN ('agent', 'portal')`; `data/ops-extract/interaction.csv` tem os actors `customer` (1234), `agent` (938) e `assist` (296), e nenhum `portal`. As 296 interações `assist` são as `proposal_sent` do portal. Os 296 tickets cuja única resposta é `assist` (145 em julho, 151 em agosto) saem de `marts.first_response` e, por consequência, de `marts.sla_attainment`, que é "the figure the service review packs quote" (`sla_attainment.sql:3`).

Medido em 2026-09-29 com `make build` (6 de 6 testes passam) contra os números que Reporting recebeu em `../portwell-knowledge/data/figures/`:

| Export | Conta | Campo | Publicado | Build de hoje |
| :- | :- | :- | -: | -: |
| `warehouse-export-2026-08-06.csv` (julho) | ACCOUNT-1008 | tickets | 115 | 75 |
| `warehouse-export-2026-08-06.csv` (julho) | ACCOUNT-1008 | attainment | 0.2696 | 0.08 |
| `warehouse-export-2026-08-06.csv` (julho) | ACCOUNT-1008 | first_response_p50 | 70 | 103 |
| `warehouse-export-2026-08-29.csv` (agosto) | ACCOUNT-1008 | attainment | 0.3966 | 0.0952 |
| `warehouse-export-2026-08-29.csv` (agosto) | ACCOUNT-1008 | first_response_p50 | 38 | 101 |

Nas três contas dos dois exports (ACCOUNT-1001, 1003, 1008): `self_service_rate` bate em 6 de 6; `tickets`, `attainment` e `first_response_p50` diferem em 18 de 18. Recalculado em memória com `actor IN ('agent', 'assist')`, os 18 valores publicados se reproduzem exatamente. O pack de julho da Sunder (`../portwell-knowledge/data/packs/2026-07/ACCOUNT-1008-2026-07.xlsx`, B13 e B14) cita 0.2696 e 70.

Não registrado em lugar nenhum: quando o actor deixou de se chamar `portal`, e se os exports foram gerados com outro filtro ou com outro extract. Consequência: a figura contratual do pack não pode ser reconstruída a partir do repositório hoje, e um rebuild do mês publicaria outro número sem nenhum teste falhar.

---

## Inconsistências no tracker

Source: `data/tracker.csv`

| Linha | Inconsistência |
|-------|---------------|
| ISSUE-34 | `status` = "In Progress", `owner` = vazio — quem está fazendo o progresso? |
| ISSUE-38 | `opened` = 2026-07-02; notes diz "Carried over from the old warehouse. Current build is under two seconds." — o problema descrito no issue já não existe, mas o issue permanece aberto |
| REQUEST-011 | `owner` = vazio — sem responsável definido |
| ISSUE-30, ISSUE-32, REQUEST-011 | `last_touched` = vazio — não há registro de quando foram atualizados |
| Coluna `status` | Valores livres: "open", "Open", "In Progress", "done", "DONE", "closed" — 6 variantes para ~3 estados. Confirmado em `docs/incidents/README.md`: "o campo status é texto livre e tem várias grafias do mesmo estado" |
| REQUEST-007 e REQUEST-011 | Notas nos dois arquivos (tracker e docx) apontam possível duplicação; nenhum registro de investigação |

---

## O que os 6 testes de forma verificam e o que não conseguem ver

Source: `project/tests/*.sql`, `docs/interviews/2026-08-12 Declan Byrne...`

| Teste | O que verifica | O que não enxerga |
|-------|---------------|-------------------|
| `accepted_values_tier.sql` | Tier é um de {standard, business, enterprise} | Se os compromissos de SLA são os que foram contratados com cada conta |
| `first_response_positive.sql` | first_response_minutes >= 0 (resposta não precede ticket) | Se o período do extract corresponde ao período de reporte |
| `no_null_self-service_for_pilot.sql` | Contas pilot têm self_service_rate não-nulo a partir de 2026-07 | Qual versão da definição foi usada para calcular a taxa |
| `not_null_self-service_account.sql` | Rows de self_service têm account_id | Se o mart implementa a definição vigente (v3) ou a supersedida (v2) |
| `referential_ticket_account.sql` | Todo ticket aponta para account existente | Se o extract é do mês correto |
| `self_service_rate_in_range.sql` | self_service_rate em [0,1] para contas pilot a partir de 2026-07 | Se o número é correto; apenas se está no range de um número válido |

**O que nenhum dos 6 testes verifica:**
- Se a definição implementada no mart corresponde à versão vigente em `metric-definitions.yaml`
- Se o extract foi extraído do período correto de reporte
- Se houve aprovação humana antes de publicar (POLICY-06)
- Se consumidores de métricas foram notificados sobre mudanças de definição (POLICY-05)
- Se o número publicado cita a versão da definição usada (POLICY-13)
- Se a query de extração usada pelo time de suporte corresponde ao schema atual

Declan Byrne, na entrevista: "Eles não verificam se um número está certo, só se é do tipo que um número deveria ser."

---

## Métricas versionadas

Source: `project/metrics/metric-definitions.yaml` (published_at 2026-08-20, owner: Sofia Marques), `docs/pr-notes/0088-self-service-v3.md`, `project/models/marts/self_service.sql`

| Métrica | Versão | Status | Effective from | Alinhamento com mart |
|---------|--------|--------|---------------|----------------------|
| `self_service_rate` | v2 | superseded | 2026-04-01 | **mart ainda implementa v2**: `is_self_served` sem filtro `human_edit_material` |
| `self_service_rate` | v3 | current | 2026-07-01 | **mart NÃO implementa v3**: deveria excluir edições materiais e tickets reopened em 48h |
| `first_response_minutes_p50` | v1 | current | 2026-02-01 | **Não alinhado** (C7): mediana e minimum_denominator de 20 estão implementados, mas "first outbound interaction" filtra `actor IN ('agent', 'portal')` e o extract chama a resposta do portal de `assist`; 296 tickets ficam fora |
| `suggestion_acceptance_rate` | v1 | current | 2026-06-15 | **Nenhum mart correspondente encontrado** |

**Data dictionary:** `docs/data-dictionary.xlsx` não foi lido (arquivo binário). Alinhamento com os modelos não verificado.

**Desalinhamento crítico:** o mart `self_service.sql` foi atualizado para refletir a intenção do autor mas a implementação ainda é v2. Conforme `docs/pr-notes/0088-self-service-v3.md`: "A intenção era atualizar o mart assim que junho fechasse. Isso não aconteceu." O mart está produzindo números com uma definição supersedida enquanto `metric-definitions.yaml` declara v3 como vigente.

---

## Handoffs manuais

**Entrada — Extract:**
- Quem faz: pessoa do suporte (variou: "geralmente Joao", 3 pessoas diferentes em 2 anos). Source: entrevista Declan Byrne.
- Como: cola query de um documento em uma ferramenta de banco de dados e exporta CSV para pasta compartilhada.
- Risco documentado: a query no documento pode estar desatualizada; Declan a mudou duas vezes e não sabe se os executores têm a versão atual. A única verificação é o load falhar se as colunas forem diferentes.
- Artefato: CSV na pasta compartilhada + `data/ops-extract/extract-manifest.yaml` (preenchido por quem faz o extract; `taken_by: Declan Byrne` no último).
- Verificação do período: manual, por Declan, olhando o manifest.

**Saída — Envio dos números:**
- Quem faz: Declan Byrne. Source: entrevista.
- Para quem: Lucia Ferreira (Reporting). Source: entrevista + `data/requests/inbox.csv`.
- Como: CSV (rastreável) ou colagem em mensagem (não rastreável, sem artefato persistente).
- O número não carrega a versão da definição. Source: `project/models/marts/self_service.sql` (nenhum campo de versão), `docs/policies.md` (POLICY-13 não enforced).

---

## Candidatos a item para o trace

### Candidato 1 — REQUEST-007 (self-service por conta para os packs de agosto)

Source: `data/tracker.csv`, `data/requests/REQUEST-007.docx`, `data/requests/inbox.csv`

- **O que é:** Lucia Ferreira (Reporting) pediu o mesmo número de self-service por conta que teve em julho, para os packs de agosto. Due: 2026-09-04.
- **Prós:**
  - Exemplifica o processo mensal completo ponta a ponta: extract → build → handoff → pack.
  - Liga-se diretamente ao INCIDENT-03: a definição mudou em julho, o pack de julho foi construído sem avisar ninguém, Sunder Retail Supply questionou a mudança.
  - Expõe a contradição C1 (mart v2 vs. definição v3 vigente).
  - Item ativo com deadline real (2026-09-04): o trace é prospectivo.
  - REQUEST-007 é explícito: "não diz qual versão da definição usar, e a definição mudou em 2026-07-01".
- **Contras:**
  - REQUEST-011 pode ser duplicata (C3) e a duplicação nunca foi resolvida. O trace de REQUEST-007 pode ser bloqueado no estágio de Route enquanto a duplicação não for esclarecida.

### Candidato 2 — INCIDENT-03 (o número de self-service mudou entre junho e julho)

Source: `docs/incidents/INCIDENT-03.md`, `docs/pr-notes/0088-self-service-v3.md`

- **O que é:** Sunder Retail Supply percebeu que seu número de self-service mudou entre os packs de junho e julho. A causa foi a transição de v2 para v3 da definição (2026-07-01), sem aviso.
- **Prós:**
  - É o "red state" mais documentado do repositório: testes passaram, número foi publicado, número estava usando definição diferente, cliente foi impactado.
  - Evidência de saída rica: o incidente foi escrito por quem investigou, com causa-raiz clara.
  - Liga-se a POLICY-05 (não anunciado), POLICY-13 (versão não declarada), ISSUE-30 (lista de consumidores).
  - Melhor para demonstrar red → green: o ciclo proposto teria bloqueado em Approve (sem evidência de qual versão).
- **Contras:**
  - Trace retrospectivo — é uma reconstrução do que aconteceu, não um item ativo sendo processado.
  - O item não está no tracker (o tracker tem ISSUE-30 como consequência, não o incidente em si).

### Candidato 3 — REQUEST-013 (escalations open at month end por conta Enterprise)

Source: `data/tracker.csv`, `data/requests/inbox.csv`

- **O que é:** Lucia Ferreira pediu escalations por conta Enterprise no fim do mês. Status: In Progress, Owner: Declan Byrne. Due: 2026-09-04.
- **Prós:**
  - Item ativo com owner definido.
  - Mostra o processo corrente sendo executado.
- **Contras:**
  - A métrica "escalations open at month end" não está definida em `project/metrics/metric-definitions.yaml` — seria necessário inventar a definição, o que viola a Regra 2.
  - Caso mais simples, menos rico em evidência sobre o que o ciclo precisa proteger.

### Recomendação

**Trace principal: INCIDENT-03** — é o caso com o maior número de evidências, o red state mais claro (testes passaram, número errado publicado, cliente impactado), e a ligação mais direta com as lacunas que o ciclo proposto deve cobrir (versão de definição, lista de consumidores, POLICY-05 e POLICY-13).

**Held-out (segundo item): REQUEST-007** — item ativo, mesmo domínio, exercita o ciclo prospectivamente e expõe a contradição ainda não resolvida (mart v2 + definição v3 + possible duplicate REQUEST-011).
