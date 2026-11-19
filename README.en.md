# enxame-com-conta

[![The swarm’s bill](guia/assets/banner-en.jpg)](https://inematds.github.io/enxame-com-conta/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## What it is

An agent swarm is when several AIs work together on the same task, each handling a piece. It works, but costs
much more: Anthropic itself measured about 15 times more text processed than a regular chat. The Cost Sheet is
a short worksheet for anyone considering using swarms at work: it asks whether the task calls for one, compares
the cost with a single agent, and sets a ceiling and a brake before you run it. The kit includes the sheet and
two Python scripts that calculate the cost and keep spending in check. You can read it to understand the idea;
using the kit requires Python 3.

## 📖 User guide

Complete guide (landing page + step-by-step instructions): **https://inematds.github.io/enxame-com-conta/guia/en/**

---

**You saw the agent swarm go viral and thought about building one. The idea is brilliant. The bill, not so much.**

This kit shows how much a swarm will cost **before** you run it, compares it with a single agent doing the same
task, and adds a brake so you don’t hit the limit a thousand times. Just Python (standard library), with no model
or API calls.

> Anthropic itself measured this: agents use about 4× more tokens than a chat, and multi-agent systems about
> **15×**. It also warns that they only pay off when the value of the task justifies the extra performance. (Sources at the end.)

## What’s included

| Component | What it does |
|---|---|
| `FICHA-CONTA.md` (in Portuguese) | 4 questions to answer before building the swarm + budget and brake |
| `conta.py estimar` | estimates tokens and cost for a swarm × a single agent, and where the cost goes (work, coordination, review, rework) |
| `conta.py comparar` | using real runs of the same task, calculates the **CRU — cost per useful result** — and gives a verdict |
| `trava.py` | brake for any agent call: stops at the first limit, has a call budget, and stops after N consecutive failures |
| `casos/lote-135.md` (in Portuguese) | real INEMA case: 12,619 limit rejections in ~34 h due to a missing brake |

## The process, from start to finish

Who does what: 🧠 you (decision) · ⚙️ kit script · 🤖 your agent (`claude -p`, `codex exec`, or another)

1. 🧠 **Answer part 1 of `FICHA-CONTA.md` (in Portuguese).** Fewer than two checked → use a single agent and stop here.
2. 🧠 **Describe the swarm in `plano.json`** (copy `exemplos/plano-enxame.json`): agents, rounds, context size,
   conversation between agents, reviewers, rework, and your model’s price per million tokens.
3. ⚙️ **Estimate:** `python3 conta.py estimar plano.json` → cost for both approaches, multiplier, and where the cost goes.
4. 🧠 **Set the budget** (part 3 of the sheet): maximum number of agents, calls, and consecutive failures.
5. 🤖 **Run each agent call through the brake**, all using the same state file:
   `python3 trava.py rodar --estado .trava.json --max-chamadas 40 --max-falhas 3 -- claude -p "…"`
   Exit codes: `75` blocked by a limit (nothing was called), `76` budget exhausted, `77` consecutive failures.
6. ⚙️ **Monitor:** `python3 trava.py status`. After reviewing what happened: `python3 trava.py liberar`.
7. 🧠 **Record the actual runs** of the same task, with a single agent and with the swarm, in `execucoes.json`
   (`custo`, `aprovada`, `retrabalho`, `minutos`).
8. ⚙️ **Compare:** `python3 conta.py comparar execucoes.json` → CRU for each and the verdict.
9. 🧠 **Decide based on the verdict:** use the swarm only if the additional result (or faster turnaround) justifies the additional cost.

## Example (illustrative numbers)

```
$ python3 conta.py estimar exemplos/plano-enxame.json
  enxame:     custo 3.42   um agente: custo 0.38   multiplicador_tokens: 8.3
  onde_vai:   trabalho 63%  coordenação 9%  revisão 5%  retrabalho 23%

$ python3 conta.py comparar exemplos/execucoes.json
  veredito: o enxame custa 5.2× mais por entrega aprovada e acerta 1.5× mais: só vale se cada entrega
  aprovada valer mais que 5.2× o custo de um agente só (mas foi 2.5× mais rápido: decida se o prazo vale isso)
```

The cost model used by `estimar` is intentionally simple: each agent rereads the context and everything it
received in each round, the coordinator reads the deliverables, the reviewer reads everything, and rework
multiplies the cost. It is meant for comparing architectures, not predicting the bill to the penny. The actual
cost comes from step 8.

## Test

```
python3 -m unittest discover -s tests -v
```

## Sources

- Anthropic, *How we built our multi-agent research system* (Jun 2025):
  https://www.anthropic.com/engineering/multi-agent-research-system — “multi-agent systems use about 15× more
  tokens than chats”; “multi-agent systems require tasks where the value of the task is high enough to pay for
  the increased performance”.
- Batch-135 case: internal INEMA record, 15–17/11/2026 (`casos/lote-135.md` (in Portuguese)).

## Related

- [enxame-antigravity](https://inematds.github.io/enxame-antigravity/guia/): the Swarm Cost Sheet for Google’s /swarm (ownership by component, who checks, when to stop).

MIT License · INEMA.CLUB — open and free content.