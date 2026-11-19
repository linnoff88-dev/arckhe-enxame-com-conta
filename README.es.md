# enxame-com-conta

[![La cuenta del enjambre](guia/assets/banner-es.jpg)](https://inematds.github.io/enxame-com-conta/guia/es/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## Qué es

Un enjambre de agentes es cuando varias IA trabajan juntas en la misma tarea, cada una en una parte. Funciona, pero
consume mucho más: la propia Anthropic midió unas 15 veces más texto procesado que en un chat común. La Ficha de la
Cuenta es una hoja breve para quienes piensan usar enjambres en el trabajo: pregunta si la tarea lo requiere, compara el
costo con el de un solo agente y establece un límite y un freno antes de ejecutarlo. El kit incluye la ficha y dos scripts en Python que
calculan el costo y limitan el gasto. Para entenderlo, basta con leer; para usar el kit, se necesita Python 3.

## 📖 Guía de uso

Guía completa (landing + paso a paso): **https://inematds.github.io/enxame-com-conta/guia/es/**

---

**Viste el enjambre de agentes viral y pensaste en montar uno. La idea es genial. La cuenta, no.**

Este kit muestra cuánto costará un enjambre **antes** de ejecutarlo, lo compara con un solo agente haciendo la misma
tarea y pone un freno para no alcanzar el límite mil veces. Solo Python (biblioteca estándar), sin llamar a modelos
ni a API.

> La propia Anthropic midió: los agentes consumen unas 4× más tokens que un chat, y los sistemas multiagente unas
> **15×** más. Y advierte: solo compensan cuando el valor de la tarea cubre el rendimiento adicional. (Fuentes al final.)

## Qué incluye

| Pieza | Para qué sirve |
|---|---|
| `FICHA-CONTA.md` (en portugués) | 4 preguntas antes de montar el enjambre + presupuesto y freno |
| `conta.py estimar` | estima tokens y costo del enjambre × un agente, y dónde se va el costo (trabajo, coordinación, revisión, retrabajo) |
| `conta.py comparar` | con ejecuciones reales de la misma tarea, calcula el **CRU — costo por resultado útil** — y da el veredicto |
| `trava.py` | freno para cualquier llamada de agente: se detiene en el 1.er límite, tiene un presupuesto de llamadas y se detiene después de N fallos |
| `casos/lote-135.md` (en portugués) | caso real de INEMA: 12.619 rechazos por límite en ~34 h por falta de freno |

## El proceso, de principio a fin

Quién hace qué: 🧠 tú (decisión) · ⚙️ script de este kit · 🤖 tu agente (`claude -p`, `codex exec` u otro)

1. 🧠 **Responde la parte 1 de la `FICHA-CONTA.md`.** Menos de dos marcadas → un solo agente y detente aquí.
2. 🧠 **Describe el enjambre en `plano.json`** (copia `exemplos/plano-enxame.json`): agentes, rondas, tamaño del
   contexto, conversación entre ellos, revisores, retrabajo y el precio de tu modelo por millón de tokens.
3. ⚙️ **Estima:** `python3 conta.py estimar plano.json` → costo de las dos opciones, multiplicador y dónde se va el costo.
4. 🧠 **Decide el presupuesto** (parte 3 de la ficha): máximo de agentes, llamadas y fallos consecutivos.
5. 🤖 **Ejecuta cada llamada de agente mediante el freno**, todas con el mismo archivo de estado:
   `python3 trava.py rodar --estado .trava.json --max-chamadas 40 --max-falhas 3 -- claude -p "…"`
   Salidas: `75` bloqueada por límite (no se llamó a nada), `76` presupuesto agotado, `77` fallos consecutivos.
6. ⚙️ **Haz seguimiento:** `python3 trava.py status`. Después de revisar lo ocurrido: `python3 trava.py liberar`.
7. 🧠 **Anota las ejecuciones reales** de la misma tarea, con un agente y con el enjambre, en `execucoes.json`
   (`custo`, `aprovada`, `retrabalho`, `minutos`).
8. ⚙️ **Compara:** `python3 conta.py comparar execucoes.json` → CRU de cada opción y veredicto.
9. 🧠 **Decide según el veredicto:** el enjambre solo se queda si el resultado adicional (o el plazo) compensa el costo adicional.

## Ejemplo (números ilustrativos)

```
$ python3 conta.py estimar exemplos/plano-enxame.json
  enxame:     custo 3.42   um agente: custo 0.38   multiplicador_tokens: 8.3
  onde_vai:   trabalho 63%  coordenação 9%  revisão 5%  retrabalho 23%

$ python3 conta.py comparar exemplos/execucoes.json
  veredito: o enxame custa 5.2× mais por entrega aprovada e acerta 1.5× mais: só vale se cada entrega
  aprovada valer mais que 5.2× o custo de um agente só (mas foi 2.5× mais rápido: decida se o prazo vale isso)
```

El modelo de costos de `estimar` es simple a propósito: cada agente vuelve a leer el contexto y todo lo que recibió en
cada ronda, el coordinador lee las entregas, el revisor lo lee todo y el retrabajo multiplica el costo. Sirve para comparar
arquitecturas, no para predecir la factura al centavo. El costo real se obtiene en el paso 8.

## Probar

```
python3 -m unittest discover -s tests -v
```

## Fuentes

- Anthropic, *How we built our multi-agent research system* (jun/2025):
  https://www.anthropic.com/engineering/multi-agent-research-system — "los sistemas multiagente usan unas 15× más
  tokens que los chats"; "los sistemas multiagente requieren tareas cuyo valor sea lo bastante alto como para cubrir
  el rendimiento adicional".
- Caso lote-135: registro interno de INEMA, 15–17/11/2026 (`casos/lote-135.md` (en portugués)).

## Relacionado

- [enxame-antigravity](https://inematds.github.io/enxame-antigravity/guia/): la Ficha del Enjambre para el /swarm de
  Google (responsable de cada parte, quién revisa, cuándo detenerse).

Licencia MIT · INEMA.CLUB — contenido abierto y gratuito.