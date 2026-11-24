# enxame-com-conta

<div align="center">
  <img src="capa/logo.svg" alt="Arckhé AI" height="48" />
  <p><strong>Arckhé AI</strong></p>
</div>


[![A conta do enxame](guia/assets/banner.jpg)](https://linnoff88-dev.github.io/

**ðŸ‡§ðŸ‡· [PortuguÃªs](README.md) Â· ðŸ‡ºðŸ‡¸ [English](README.en.md) Â· ðŸ‡ªðŸ‡¸ [EspaÃ±ol](README.es.md)**

## O que Ã©

Um enxame de agentes Ã© quando vÃ¡rias IAs trabalham juntas na mesma tarefa, cada uma num pedaÃ§o. Funciona, mas
gasta muito mais: a prÃ³pria Anthropic mediu cerca de 15 vezes mais texto processado que um chat comum. A Ficha da
Conta Ã© uma folha curta para quem pensa em usar enxames no trabalho: ela pergunta se a tarefa pede isso, compara o
custo com um agente sÃ³ e pÃµe um teto e um freio antes de rodar. O kit traz a ficha e dois scripts em Python que
fazem a conta e seguram o gasto. Para entender, Ã© sÃ³ ler; para usar o kit, precisa de Python 3.

## ðŸ“– Guia de uso

Guia completo (landing + passo a passo): **https://linnoff88-dev.github.io/

---

**VocÃª viu o enxame de agentes viral e pensou em montar um. A ideia Ã© genial. A conta, nÃ£o.**

Este kit mostra quanto um enxame vai custar **antes** de rodar, compara com um agente sÃ³ fazendo a mesma
tarefa e pÃµe um freio para nÃ£o bater no limite mil vezes. SÃ³ Python (biblioteca padrÃ£o), sem chamar modelo
nem API.

> A prÃ³pria Anthropic mediu: agentes gastam cerca de 4Ã— mais tokens que um chat, e sistemas multiagente cerca de
> **15Ã—**. E avisa: sÃ³ compensam quando o valor da tarefa paga o desempenho a mais. (Fontes no fim.)

## O que tem aqui

| PeÃ§a | Para quÃª |
|---|---|
| `FICHA-CONTA.md` | 4 perguntas antes de montar o enxame + orÃ§amento e freio |
| `conta.py estimar` | estima tokens e custo do enxame Ã— um agente, e onde o custo vai (trabalho, coordenaÃ§Ã£o, revisÃ£o, retrabalho) |
| `conta.py comparar` | com execuÃ§Ãµes reais da mesma tarefa, calcula o **CRU â€” custo por resultado Ãºtil** â€” e dÃ¡ o veredito |
| `trava.py` | freio para qualquer chamada de agente: para no 1Âº limite, tem orÃ§amento de chamadas e para depois de N falhas |
| `casos/lote-135.md` | caso real ARCKHÉ: 12.619 recusas por limite em ~34 h por falta de trava |

## O processo, do inÃ­cio ao fim

Quem faz: ðŸ§  vocÃª (decisÃ£o) Â· âš™ï¸ script deste kit Â· ðŸ¤– seu agente (`claude -p`, `codex exec` ou outro)

1. ðŸ§  **Responda a parte 1 da `FICHA-CONTA.md`.** Menos de duas marcadas â†’ um agente sÃ³ e pare aqui.
2. ðŸ§  **Descreva o enxame em `plano.json`** (copie `exemplos/plano-enxame.json`): agentes, rodadas, tamanho do
   contexto, conversa entre eles, revisores, retrabalho e o preÃ§o do seu modelo por milhÃ£o de tokens.
3. âš™ï¸ **Estime:** `python3 conta.py estimar plano.json` â†’ custo dos dois jeitos, multiplicador e onde o custo vai.
4. ðŸ§  **Decida o orÃ§amento** (parte 3 da ficha): mÃ¡ximo de agentes, de chamadas e de falhas seguidas.
5. ðŸ¤– **Rode cada chamada de agente pela trava**, todas com o mesmo arquivo de estado:
   `python3 trava.py rodar --estado .trava.json --max-chamadas 40 --max-falhas 3 -- claude -p "â€¦"`
   SaÃ­das: `75` bloqueada por limite (nada foi chamado), `76` orÃ§amento esgotado, `77` falhas seguidas.
6. âš™ï¸ **Acompanhe:** `python3 trava.py status`. Depois de olhar o que houve: `python3 trava.py liberar`.
7. ðŸ§  **Anote as execuÃ§Ãµes reais** da mesma tarefa, com um agente e com o enxame, em `execucoes.json`
   (`custo`, `aprovada`, `retrabalho`, `minutos`).
8. âš™ï¸ **Compare:** `python3 conta.py comparar execucoes.json` â†’ CRU de cada um e o veredito.
9. ðŸ§  **Decida pelo veredito:** o enxame sÃ³ fica se o resultado a mais (ou o prazo) paga o custo a mais.

## Exemplo (nÃºmeros ilustrativos)

```
$ python3 conta.py estimar exemplos/plano-enxame.json
  enxame:     custo 3.42   um agente: custo 0.38   multiplicador_tokens: 8.3
  onde_vai:   trabalho 63%  coordenaÃ§Ã£o 9%  revisÃ£o 5%  retrabalho 23%

$ python3 conta.py comparar exemplos/execucoes.json
  veredito: o enxame custa 5.2Ã— mais por entrega aprovada e acerta 1.5Ã— mais: sÃ³ vale se cada entrega
  aprovada valer mais que 5.2Ã— o custo de um agente sÃ³ (mas foi 2.5Ã— mais rÃ¡pido: decida se o prazo vale isso)
```

O modelo de custo do `estimar` Ã© simples e de propÃ³sito: cada agente relÃª o contexto e tudo o que recebeu a
cada rodada, o coordenador lÃª as entregas, o revisor lÃª tudo, e o retrabalho multiplica. Serve para comparar
arquiteturas, nÃ£o para prever a fatura ao centavo. A conta de verdade vem do passo 8.

## Testar

```
python3 -m unittest discover -s tests -v
```

## Fontes

- Anthropic, *How we built our multi-agent research system* (jun/2025):
  https://www.anthropic.com/engineering/multi-agent-research-system â€” "multi-agent systems use about 15Ã— more
  tokens than chats"; "multi-agent systems require tasks where the value of the task is high enough to pay for
  the increased performance".
- Caso lote-135: registro interno ARCKHÉ, 15â€“17/11/2026 (`casos/lote-135.md`).

## Relacionado

- [enxame-antigravity](https://linnoff88-dev.github.io/ a Ficha do Enxame para o /swarm do
  Google (dono por pedaÃ§o, quem confere, quando parar).

LicenÃ§a MIT Â· ARCKHÉ AI â€” conteÃºdo aberto e gratuito.

---

<div align="center">
  <img src="capa/logo.svg" alt="Arckhé AI" height="32" />
  <p><strong>Arckhé AI</strong></p>
</div>