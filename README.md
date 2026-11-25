# enxame-com-conta

<div align="center">
  <img src="capa/logo.svg" alt="Arckhé AI" height="48" />
  <p><strong>Arckhé AI</strong></p>
</div>


[![A conta do enxame](guia/assets/banner.jpg)](https://linnoff88-dev.github.io/

**ê°Å¸â¡Â§ê°Å¸â¡Â· [PortuguêÂªs](README.md) êÂ· ê°Å¸â¡Âºê°Å¸â¡Â¸ [English](README.en.md) êÂ· ê°Å¸â¡Âªê°Å¸â¡Â¸ [EspaêÂ±ol](README.es.md)**

## O que êÂ©

Um enxame de agentes êÂ© quando vêÂ¡rias IAs trabalham juntas na mesma tarefa, cada uma num pedaêÂ§o. Funciona, mas
gasta muito mais: a prêÂ³pria Anthropic mediu cerca de 15 vezes mais texto processado que um chat comum. A Ficha da
Conta êÂ© uma folha curta para quem pensa em usar enxames no trabalho: ela pergunta se a tarefa pede isso, compara o
custo com um agente sêÂ³ e pêÂµe um teto e um freio antes de rodar. O kit traz a ficha e dois scripts em Python que
fazem a conta e seguram o gasto. Para entender, êÂ© sêÂ³ ler; para usar o kit, precisa de Python 3.

## ê°Å¸ââ Guia de uso

Guia completo (landing + passo a passo): **https://linnoff88-dev.github.io/

---

**VocêÂª viu o enxame de agentes viral e pensou em montar um. A ideia êÂ© genial. A conta, nêÂ£o.**

Este kit mostra quanto um enxame vai custar **antes** de rodar, compara com um agente sêÂ³ fazendo a mesma
tarefa e pêÂµe um freio para nêÂ£o bater no limite mil vezes. SêÂ³ Python (biblioteca padrêÂ£o), sem chamar modelo
nem API.

> A prêÂ³pria Anthropic mediu: agentes gastam cerca de 4êâ mais tokens que um chat, e sistemas multiagente cerca de
> **15êâ**. E avisa: sêÂ³ compensam quando o valor da tarefa paga o desempenho a mais. (Fontes no fim.)

## O que tem aqui

| PeêÂ§a | Para quêÂª |
|---|---|
| `FICHA-CONTA.md` | 4 perguntas antes de montar o enxame + orêÂ§amento e freio |
| `conta.py estimar` | estima tokens e custo do enxame êâ um agente, e onde o custo vai (trabalho, coordenaêÂ§êÂ£o, revisêÂ£o, retrabalho) |
| `conta.py comparar` | com execuêÂ§êÂµes reais da mesma tarefa, calcula o **CRU ê¢â¬â custo por resultado êÂºtil** ê¢â¬â e dêÂ¡ o veredito |
| `trava.py` | freio para qualquer chamada de agente: para no 1êÂº limite, tem orêÂ§amento de chamadas e para depois de N falhas |
| `casos/lote-135.md` | caso real ARCKHê: 12.619 recusas por limite em ~34 h por falta de trava |

## O processo, do inêÂ­cio ao fim

Quem faz: ê°Å¸Â§Â  vocêÂª (decisêÂ£o) êÂ· ê¢Å¡â¢ê¯Â¸Â script deste kit êÂ· ê°Å¸Â¤â seu agente (`claude -p`, `codex exec` ou outro)

1. ê°Å¸Â§Â  **Responda a parte 1 da `FICHA-CONTA.md`.** Menos de duas marcadas ê¢â â um agente sêÂ³ e pare aqui.
2. ê°Å¸Â§Â  **Descreva o enxame em `plano.json`** (copie `exemplos/plano-enxame.json`): agentes, rodadas, tamanho do
   contexto, conversa entre eles, revisores, retrabalho e o preêÂ§o do seu modelo por milhêÂ£o de tokens.
3. ê¢Å¡â¢ê¯Â¸Â **Estime:** `python3 conta.py estimar plano.json` ê¢â â custo dos dois jeitos, multiplicador e onde o custo vai.
4. ê°Å¸Â§Â  **Decida o orêÂ§amento** (parte 3 da ficha): mêÂ¡ximo de agentes, de chamadas e de falhas seguidas.
5. ê°Å¸Â¤â **Rode cada chamada de agente pela trava**, todas com o mesmo arquivo de estado:
   `python3 trava.py rodar --estado .trava.json --max-chamadas 40 --max-falhas 3 -- claude -p "ê¢â¬Â¦"`
   SaêÂ­das: `75` bloqueada por limite (nada foi chamado), `76` orêÂ§amento esgotado, `77` falhas seguidas.
6. ê¢Å¡â¢ê¯Â¸Â **Acompanhe:** `python3 trava.py status`. Depois de olhar o que houve: `python3 trava.py liberar`.
7. ê°Å¸Â§Â  **Anote as execuêÂ§êÂµes reais** da mesma tarefa, com um agente e com o enxame, em `execucoes.json`
   (`custo`, `aprovada`, `retrabalho`, `minutos`).
8. ê¢Å¡â¢ê¯Â¸Â **Compare:** `python3 conta.py comparar execucoes.json` ê¢â â CRU de cada um e o veredito.
9. ê°Å¸Â§Â  **Decida pelo veredito:** o enxame sêÂ³ fica se o resultado a mais (ou o prazo) paga o custo a mais.

## Exemplo (nêÂºmeros ilustrativos)

```
$ python3 conta.py estimar exemplos/plano-enxame.json
  enxame:     custo 3.42   um agente: custo 0.38   multiplicador_tokens: 8.3
  onde_vai:   trabalho 63%  coordenaêÂ§êÂ£o 9%  revisêÂ£o 5%  retrabalho 23%

$ python3 conta.py comparar exemplos/execucoes.json
  veredito: o enxame custa 5.2êâ mais por entrega aprovada e acerta 1.5êâ mais: sêÂ³ vale se cada entrega
  aprovada valer mais que 5.2êâ o custo de um agente sêÂ³ (mas foi 2.5êâ mais rêÂ¡pido: decida se o prazo vale isso)
```

O modelo de custo do `estimar` êÂ© simples e de propêÂ³sito: cada agente relêÂª o contexto e tudo o que recebeu a
cada rodada, o coordenador lêÂª as entregas, o revisor lêÂª tudo, e o retrabalho multiplica. Serve para comparar
arquiteturas, nêÂ£o para prever a fatura ao centavo. A conta de verdade vem do passo 8.

## Testar

```
python3 -m unittest discover -s tests -v
```

## Fontes

- Anthropic, *How we built our multi-agent research system* (jun/2025):
  https://www.anthropic.com/engineering/multi-agent-research-system ê¢â¬â "multi-agent systems use about 15êâ more
  tokens than chats"; "multi-agent systems require tasks where the value of the task is high enough to pay for
  the increased performance".
- Caso lote-135: registro interno ARCKHê, 15ê¢â¬â17/11/2026 (`casos/lote-135.md`).

## Relacionado

- [enxame-antigravity](https://linnoff88-dev.github.io/ a Ficha do Enxame para o /swarm do
  Google (dono por pedaêÂ§o, quem confere, quando parar).

LicenêÂ§a MIT êÂ· ARCKHê AI ê¢â¬â conteêÂºdo aberto e gratuito.

---

<div align="center">
  <img src="capa/logo.svg" alt="Arckhé AI" height="32" />
  <p><strong>Arckhé AI</strong></p>
</div>