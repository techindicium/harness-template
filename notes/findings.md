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

**C6 — Causa-raiz de INCIDENT-03: três fontes que não fecham:**
CONTRADICTION: `docs/incidents/INCIDENT-03.md` (2026-08-06) diz que o número mudou "because the `self_service_rate` definition went from version 2 to version 3 on 2026-07-01"; `docs/pr-notes/0088-self-service-v3.md` diz "The mart was not updated. `marts/self_service.sql` still sums `is_self_served`, which is the version 2 rule", e `project/models/staging/stg_suggestions.sql` computa `is_self_served = CAST(sent AS BOOLEAN)`; o pack de julho da Sunder (`../portwell-knowledge/data/packs/2026-07/ACCOUNT-1008-2026-07.xlsx`) mostra "Self-service, prior" = 0 (B19) e julho = 0.3478 (B15).

Fatos medidos no extract atual: a primeira sugestão é de 2026-07-01T08:01 (`data/ops-extract/suggestion.csv`); `marts.self_service` dá 0.0 em junho para as seis contas piloto; `project/tests/self_service_rate_in_range.sql` exclui meses anteriores a 2026-07 porque "the portal was never enabled for them". O campo `human_edit_material`, exigido pela v3, não existe no extract nem no staging.

Limite do que se pode afirmar: o extract no repositório é o de agosto (`taken_at: 2026-08-28T09:14:00Z`); as colunas do extract usado em julho são UNKNOWN. O que se sustenta é que o mart implementa a regra v2 (0088 e o SQL), não que a v3 fosse impossível em julho. A mudança que o cliente viu foi de 0 para 0.3478. Se ela vem da definição, da entrada do portal em julho ou de outra coisa é UNKNOWN, e a contradição fica aberta.

**C8 — `self_service_rate` v2 contra o mart, campo a campo:**
CONTRADICTION: `project/metrics/metric-definitions.yaml` v2 define grain `account-day`, numerador "tickets where proposal_sent is true" e denominador "tickets closed in the period"; `project/models/marts/self_service.sql` agrupa por `account_id, month`, soma `is_self_served` (de `suggestion.sent`) e divide por `count(*)` de todos os tickets abertos no mês, incluindo os de status `open`.

Medido: o numerador é equivalente neste extract (296 `sent` verdadeiros, 296 interações `proposal_sent`). O denominador inclui os 10 tickets `open`, todos de agosto: ACCOUNT-1001 0.433 no mart contra 0.4421 só com fechados, ACCOUNT-1003 0.359 contra 0.3636, ACCOUNT-1008 0.4569 contra 0.4609. Julho não é afetado. "Closed in the period" não é computável: `ticket.csv` não tem data de fechamento, então o mart usa o mês de abertura. "Alinhado com v2" vale pelo nome da regra, não campo a campo.

**C9 — O que a entrevista diz que os testes checam:**
CONTRADICTION: Declan Byrne, na entrevista, diz que os testes checam "Row counts are not zero, no duplicate keys, percentages between zero and one"; nenhum dos 6 testes em `project/tests/` checa contagem de linhas ou chave duplicada. Medido: os 6 testes passam contra `staging` e `marts` vazios (mesmas colunas, zero linhas), porque cada teste procura linhas que violam uma regra e uma tabela vazia não tem nenhuma.

**C10 — `staging.extract_metadata` não registra a idade do extract:**
CONTRADICTION: `project/models/staging/stg_extract_metadata.sql` se descreve como "When this snapshot was taken"; `docs/how-we-work-today.md` diz que `staging.extract_metadata` registra quando o warehouse foi construído; o SQL grava `strftime(now(), '%Y-%m-%dT%H:%M:%SZ')`. Medido em 2026-09-29: um build às 15:04:50 UTC gravou `2026-09-29T12:04:50Z`, que é a hora local (-03:00) com sufixo `Z`. O manifest diz `taken_at: 2026-08-28T09:14:00Z`. Dentro do warehouse, a data do extract não existe.

**C11 — Onde o harness é construído (camada do curso):**
CONTRADICTION: `README.md` do `portwell-analytics` diz "Four groups build one system here", descreve `scripts/lifecycle.py`, `state/`, `skills/`, `hooks/` e `evidence/<item>/` dentro do track, e manda rodar `make verify`; nada disso existe, e `make verify` falha com "No rule to make target 'verify'" (medido em 2026-09-29). O `STUDENT-GUIDE.md` do track diz "Anything the group builds is new. There is no prescribed place for it". O `README.md` do `harness-template` diz "do not change the track repository as part of this assignment". Este PR segue o `harness-template`, que é o enunciado mais recente (commit de 2026-09-10 contra 2026-09-09 do track).

**C12 — Dicionário de dados contra os modelos:**
CONTRADICTION: `docs/data-dictionary.xlsx` (legível como zip; última revisão completa 2026-05-12, na aba 2) lista `staging.suggestions.was_self-served`, `marts.response_times.p50_minutes`, `marts.inventory_accuracy.stock_count_variance` e descreve `marts.self_service.closed_tickets` como "Tickets closed in the month"; os modelos têm `was_sent` e `is_self_served`, `marts.first_response_p50.first_response_minutes_p50`, nenhum mart `inventory_accuracy`, e `closed_tickets` conta todos os tickets do mês (C8). A própria aba 2 registra: "the module was renamed to Cycle Count in 2024 and the column name here was not changed with it". `docs/backlog.md` (ISSUE-35) fala em duas colunas; há pelo menos quatro divergências.

**C13 — O ISSUE-13 que o INCIDENT-03 cita é outro problema:**
CONTRADICTION: `docs/incidents/INCIDENT-03.md` diz "`ISSUE-13` in the Portal engineering backlog reports the same problem from the consumer end" (a falta de lista de consumidores); em `../portwell-engineering/docs/backlog.md:13` e `data/tracker.csv:5`, `ISSUE-13` é "No link between an escalation and its issue", sem relação com consumidores de métricas. A dependência cruzada que o incidente declara não existe no outro track com esse identificador.

**C14 — REQUEST-009 e o POLICY-11:**
CONTRADICTION: `data/requests/REQUEST-009.docx` diz "`POLICY-11` allows quoting an observed p50 where the account has more than 20 closed tickets" e que o que foi enviado foi "a first-response median for August only", e ainda que a janela "is not something the policy addresses". O `POLICY-11` não está em `docs/policies.md` deste track; ele existe em `../portwell-product/docs/Policies.docx`: "Support may quote a resolution time from the tier commitment table, or from the trailing ninety day observed median where the account has more than twenty closed tickets. Owner: Gabriela Rocha. Current since 2026-07-01." O policy fala de tempo de resolução, não de primeira resposta, e fixa a janela em noventa dias. Além disso, o p50 de agosto da Nordkai publicado (41, `warehouse-export-2026-08-29.csv`) não se reproduz hoje (100, C7).

**C15 — TICKET-004424 não é a pergunta que o INCIDENT-03 descreve:**
CONTRADICTION: `docs/incidents/INCIDENT-03.md`, escrito em 2026-08-06, diz que a Sunder "saw their self-service figure change between the June and July service review packs" e que "`TICKET-004424` is that question", e que "The customer was given an explanation two days later"; em `data/ops-extract/ticket.csv`, `TICKET-004424` foi aberto em 2026-08-20, catorze dias depois do incidente, com o texto "The self-service figure on our dashboard dropped by six points this month with no change on our side", e segue com status `open`. O ticket fala do dashboard, não do pack, e de uma queda; o pack de julho mostra uma alta de 0 para 0.3478 (C6). `docs/dependencies.md` diz que o portal "serves an unpinned latest". Qual número o cliente viu cair, e se a explicação chegou a ser dada, é UNKNOWN.

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

## Dependências com outros tracks

Fontes: `docs/dependencies.md` deste track e dos tracks vizinhos, lidos sem alteração em 2026-09-29.

| Direção | Track | O quê | Como chega | O que alguém verifica | Fonte |
| :- | :- | :- | :- | :- | :- |
| Consome | Engineering (`portwell-engineering`) | O banco operacional, lido como schema `ops` | Extract manual em CSV. `run.py --live` aponta para `../portwell-portal/data/portwell_ops.db`, que não existe neste workspace | Nada sobre schema ou significado das colunas. O C7 é uma mudança de valor que nada detectou | `docs/dependencies.md`; `../portwell-engineering/docs/dependencies.md`; `project/run.py` |
| Publica | Knowledge e Reporting (`portwell-knowledge`) | Figuras mensais por conta e volumes por área | CSV com cabeçalho `# from:` e `# sent:`, ou números colados em mensagem. Três exports para dois meses em `data/figures/` | Que as contas são as três esperadas. Nada sobre período, extract ou versão | `../portwell-knowledge/docs/dependencies.md` |
| Publica | Portal engineering | `project/metrics/metric-definitions.yaml` | Lido sem fixar versão | Nada | `docs/dependencies.md`; `../portwell-engineering/docs/dependencies.md` |
| Publica | Product (`portwell-product`) | Números sob pedido: REQUEST-005, 009, 010 e 014 | Mensagem e slide | Nada. O slide do REQUEST-005 saiu sem a ressalva | `data/requests/inbox.csv`; `data/requests/REQUEST-005.docx`; `data/requests/REQUEST-009.docx` |

O que os tracks vizinhos mostram sobre as nossas figuras:

- Os packs são contratuais: "Five business days after month end" (`../portwell-knowledge/docs/dependencies.md`). Finance lê três células do pack sem contrato.
- `../portwell-knowledge/data/figures/` tem dois exports de julho: 2026-08-01, "July figures, first cut", e 2026-08-06, "A late batch of tickets landed after the first cut. Use this one." A ACCOUNT-1001 passou de 91 para 95 tickets entre os dois. O extract atual reproduz o segundo.
- O pack de julho da Sunder (`../portwell-knowledge/data/packs/2026-07/ACCOUNT-1008-2026-07.docx`) diz "Automation rate for the quarter to date is 41 per cent". Nenhum dos três exports tem essa coluna. `ISSUE-52` no backlog de knowledge ("Self-service and automation rate may be the same number", owner Henrik Sole) e o REQUEST-011 aqui são o mesmo problema visto dos dois lados, e nenhum tem resposta.
- O mesmo pack lista `ESCALATION-0421`, "Reporting figure differs from the portal", aberta há 4 dias no fim de julho.
- A identidade da empresa diverge entre tracks: o `CLAUDE.md` deste track descreve a Portwell Software, que vende um WMS; `../portwell-engineering/CLAUDE.md:3` descreve uma empresa que oferece contas correntes empresariais. Registrado, não resolvido.

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
- Se existe algum dado: os 6 testes passam contra tabelas vazias (C9)
- Se um valor filtrado ainda existe na origem: `first_response.sql` filtra um actor que o extract não tem, e nada falha (C7)

Declan Byrne, na entrevista: "Eles não verificam se um número está certo, só se é do tipo que um número deveria ser."

---

## Métricas versionadas

Source: `project/metrics/metric-definitions.yaml` (published_at 2026-08-20, owner: Sofia Marques), `docs/pr-notes/0088-self-service-v3.md`, `project/models/marts/self_service.sql`

| Métrica | Versão | Status | Effective from | Alinhamento com mart |
|---------|--------|--------|---------------|----------------------|
| `self_service_rate` | v2 | superseded | 2026-04-01 | **mart ainda implementa a regra v2**: `is_self_served` sem filtro `human_edit_material`. Campo a campo há desvios de grain e de denominador (C8) |
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
