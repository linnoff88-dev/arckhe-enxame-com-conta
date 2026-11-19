#!/usr/bin/env python3
"""enxame-com-conta: mede se um enxame de agentes vale o que custa.

Dois comandos, só biblioteca padrão, nenhuma chamada a modelo ou API:

  python3 conta.py estimar <plano.json>     estima o custo de um enxame antes de rodar
  python3 conta.py comparar <execucoes.json> compara execuções reais (um agente × enxame)

A métrica central é o CRU, custo por resultado útil: custo total ÷ entregas aprovadas.
"""
import json
import sys

VERSAO = "1.0.1"


def _tokens_agente(contexto, tarefa, rodadas, mensagens, tam_msg):
    """tokens de entrada que um agente lê ao longo das rodadas.

    A cada rodada ele relê o contexto, a tarefa e tudo o que recebeu dos outros até ali
    (é por isso que conversa entre agentes cresce rápido).
    """
    total = 0
    recebido = 0
    for _ in range(rodadas):
        total += contexto + tarefa + recebido
        recebido += mensagens * tam_msg
    return total


def estimar(plano):
    """estima tokens e custo de um enxame e de um agente só para a mesma tarefa.

    plano: {
      "agentes": 6, "rodadas": 3, "contexto": 20000, "tarefa": 2000, "saida_por_agente": 3000,
      "mensagens_por_rodada": 2, "tamanho_mensagem": 1500,
      "revisores": 1, "retrabalho": 0.3,
      "um_agente": {"rodadas": 4, "saida": 8000},
      "preco": {"entrada": 3.0, "saida": 15.0}        # por milhão de tokens, na moeda que você usar
    }
    """
    n = int(plano["agentes"])
    rod = int(plano.get("rodadas", 1))
    ctx = int(plano["contexto"])
    tarefa = int(plano.get("tarefa", 0))
    said = int(plano.get("saida_por_agente", 0))
    msgs = int(plano.get("mensagens_por_rodada", 0))
    tmsg = int(plano.get("tamanho_mensagem", 0))
    rev = int(plano.get("revisores", 0))
    retr = float(plano.get("retrabalho", 0.0))
    preco = plano.get("preco", {"entrada": 0.0, "saida": 0.0})
    if n < 1 or rod < 1:
        raise ValueError("agentes e rodadas têm de ser pelo menos 1")
    if not 0 <= retr <= 1:
        raise ValueError("retrabalho é uma fração entre 0 e 1 (0.3 = 30% refeito)")

    trab_ent = n * _tokens_agente(ctx, tarefa, rod, msgs, tmsg)
    trab_sai = n * rod * said
    coord_ent = rod * (tarefa + n * said)          # o coordenador lê o que cada um entrega
    coord_sai = rod * said
    rev_ent = rev * (ctx + n * said)               # revisor lê o contexto e todas as entregas
    rev_sai = rev * said
    ent = (trab_ent + coord_ent + rev_ent) * (1 + retr)
    sai = (trab_sai + coord_sai + rev_sai) * (1 + retr)

    um = plano.get("um_agente", {})
    um_rod = int(um.get("rodadas", rod))
    um_ent = _tokens_agente(ctx, tarefa, um_rod, 0, 0)
    um_sai = int(um.get("saida", said * n))

    def custo(e, s):
        return e / 1e6 * float(preco.get("entrada", 0)) + s / 1e6 * float(preco.get("saida", 0))

    enx = {"entrada": round(ent), "saida": round(sai), "custo": round(custo(ent, sai), 4)}
    so = {"entrada": um_ent, "saida": um_sai, "custo": round(custo(um_ent, um_sai), 4)}
    tot_enx = ent + sai
    tot_um = um_ent + um_sai
    partes = {
        "trabalho": trab_ent + trab_sai,
        "coordenacao": coord_ent + coord_sai,
        "revisao": rev_ent + rev_sai,
        "retrabalho": (trab_ent + coord_ent + rev_ent + trab_sai + coord_sai + rev_sai) * retr,
    }
    return {
        "enxame": enx,
        "um_agente": so,
        "multiplicador_tokens": round(tot_enx / tot_um, 1) if tot_um else None,
        "onde_vai": {k: round(v / tot_enx * 100, 1) for k, v in partes.items()},
    }


def comparar(execucoes):
    """compara execuções reais. execucoes: lista de
    {"arquitetura": "um_agente"|"enxame", "custo": 1.2, "aprovada": true, "retrabalho": 0.1, "minutos": 12}

    Para cada arquitetura: custo total, taxa de sucesso, CRU (custo por entrega aprovada) e tempo médio.
    Veredito: o enxame vale quando o ganho de qualidade (taxa de sucesso) ou de tempo paga o aumento do CRU.
    """
    grupos = {}
    for e in execucoes:
        a = e["arquitetura"]
        if a not in ("um_agente", "enxame"):
            raise ValueError(f"arquitetura desconhecida: {a}")
        g = grupos.setdefault(a, {"n": 0, "aprovadas": 0, "custo": 0.0, "retrabalho": 0.0, "minutos": 0.0})
        g["n"] += 1
        g["aprovadas"] += 1 if e.get("aprovada") else 0
        g["custo"] += float(e["custo"])
        g["retrabalho"] += float(e.get("custo", 0)) * float(e.get("retrabalho", 0))
        g["minutos"] += float(e.get("minutos", 0))
    res = {}
    for a, g in grupos.items():
        res[a] = {
            "execucoes": g["n"],
            "aprovadas": g["aprovadas"],
            "custo_total": round(g["custo"], 4),
            "taxa_sucesso": round(g["aprovadas"] / g["n"], 3),
            "cru": round(g["custo"] / g["aprovadas"], 4) if g["aprovadas"] else None,
            "custo_retrabalho": round(g["retrabalho"], 4),
            "minutos_medio": round(g["minutos"] / g["n"], 1),
        }
    res["veredito"] = veredito(res.get("um_agente"), res.get("enxame"))
    return res


def veredito(um, enx):
    if not um or not enx:
        return "faltam execuções das duas arquiteturas para comparar (rode a mesma tarefa com um agente e com o enxame)"
    if enx["cru"] is None:
        return "o enxame não entregou nada aprovado: não vale"
    if um["cru"] is None:
        return "um agente só não entregou nada aprovado; o enxame entregou: vale, se o resultado paga o custo total"
    vezes_custo = enx["cru"] / um["cru"] if um["cru"] else float("inf")
    vezes_sucesso = enx["taxa_sucesso"] / um["taxa_sucesso"] if um["taxa_sucesso"] else float("inf")
    if vezes_custo <= 1:
        return f"o enxame custa {vezes_custo:.1f}× por entrega aprovada: vale"
    tempo = ""
    if enx["minutos_medio"] and um["minutos_medio"] and enx["minutos_medio"] < um["minutos_medio"]:
        tempo = f" (mas foi {um['minutos_medio'] / enx['minutos_medio']:.1f}× mais rápido: decida se o prazo vale isso)"
    return (f"o enxame custa {vezes_custo:.1f}× mais por entrega aprovada e acerta {vezes_sucesso:.1f}× mais: "
            f"só vale se cada entrega aprovada valer mais que {vezes_custo:.1f}× o custo de um agente só{tempo}")


def _ler(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def main(argv):
    if len(argv) != 2 or argv[0] not in ("estimar", "comparar"):
        print(__doc__.strip())
        return 2
    cmd, caminho = argv
    dados = _ler(caminho)
    out = estimar(dados) if cmd == "estimar" else comparar(dados)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
