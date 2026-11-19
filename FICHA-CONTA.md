# Ficha da Conta — preencha antes de montar um enxame

Copie este arquivo para a pasta da sua tarefa e responda. Se não conseguir responder a parte 1, não monte o enxame.

## 1. Vale a pena chamar mais de um agente?

- [ ] A tarefa se divide em pedaços **independentes** (um não espera o outro)?
- [ ] O trabalho é **largo** (muitas fontes, muitos arquivos, muitas variações) e não só fundo?
- [ ] O **prazo** importa mais que o custo?
- [ ] Cada entrega aprovada **vale** bem mais que o custo de rodar (anote quanto): `________`

Menos de duas marcadas → **um agente só**. A própria Anthropic diz que sistema multiagente só compensa
quando o valor da tarefa paga o desempenho a mais (ver README, Fontes).

## 2. A conta antes de rodar

Rode `python3 conta.py estimar plano.json` com os números da sua tarefa e anote:

| | um agente | enxame |
|---|---|---|
| tokens estimados | | |
| custo estimado | | |
| multiplicador | 1× | |

Onde o custo vai (trabalho / coordenação / revisão / retrabalho): `________`

## 3. Orçamento e freio (obrigatório)

- Máximo de agentes: `___`
- Máximo de chamadas na tarefa (`trava.py --max-chamadas`): `___`
- Para depois de quantas falhas seguidas (`--max-falhas`): `___` (padrão 3)
- Bateu no limite de uso → **para tudo** e espera (a `trava.py` faz isso sozinha)
- Quem confere o resultado, e de preferência em outro modelo: `________`
- Quando está pronto (um comando que prova: `npm test`, um arquivo, uma checagem): `________`
- Nada de laço rodando sem alguém olhando.

## 4. Depois de rodar: a conta de verdade

Anote cada execução em `execucoes.json` (mesma tarefa, um agente × enxame) e rode
`python3 conta.py comparar execucoes.json`. A pergunta não é "o enxame funcionou?", é:

> O enxame entregou um resultado X vezes melhor gastando Y vezes mais? Se Y > X e o prazo não salva, ficou caro.

Métrica: **CRU, custo por resultado útil** = custo total ÷ entregas aprovadas.
