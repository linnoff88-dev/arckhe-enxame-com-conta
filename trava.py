#!/usr/bin/env python3
"""trava: põe teto e freio em qualquer chamada de agente (claude -p, codex exec, script seu).

Nasceu do caso lote-135 (casos/lote-135.md): um processo sem trava bateu no limite 12.619 vezes
em ~34 h porque nada o fazia parar no primeiro "limite atingido".

  python3 trava.py rodar [opções] -- <comando ...>    roda o comando se a trava deixar
  python3 trava.py status  [--estado arq]              mostra o estado
  python3 trava.py liberar [--estado arq]              zera o bloqueio (você decidiu continuar)

Regras (todas no arquivo de estado, que vários processos podem compartilhar):
  1. bloqueada por limite → não roda nada até a hora de liberar (sai com 75, sem chamar o comando);
  2. no 1º sinal de limite na saída (429, rate limit, "hit your ... limit") → bloqueia e sai com 75;
  3. --max-chamadas atingido → para (sai com 76): é o orçamento da tarefa;
  4. --max-falhas seguidas → para (sai com 77): falha repetida não é motivo para tentar de novo.
Só biblioteca padrão. A trava não chama modelo nenhum: ela só decide se o SEU comando roda.
"""
import argparse
import fcntl
import json
import os
import re
import subprocess
import sys
import time
from contextlib import contextmanager

SINAIS_LIMITE = [
    r"\b429\b",
    r"rate[_ ]?limit",
    r"hit your (weekly |daily |usage )?limit",
    r"usage limit",
    r"quota (exceeded|exhausted)",
    r"limite (de uso|semanal|atingido)",
]
SAI_BLOQUEADA, SAI_ORCAMENTO, SAI_FALHAS = 75, 76, 77


def estado_vazio():
    return {"chamadas": 0, "falhas_seguidas": 0, "bloqueada_ate": 0, "motivo": "", "historico": []}


@contextmanager
def aberto(caminho):
    """lê e grava o estado com trava de arquivo (vários processos, uma conta só)."""
    fd = os.open(caminho, os.O_RDWR | os.O_CREAT, 0o644)
    with os.fdopen(fd, "r+", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        txt = f.read()
        est = json.loads(txt) if txt.strip() else estado_vazio()
        yield est
        est["historico"] = est.get("historico", [])[-50:]
        f.seek(0)
        f.truncate()
        json.dump(est, f, ensure_ascii=False, indent=2)


def sinal_de_limite(texto):
    return any(re.search(p, texto, re.I) for p in SINAIS_LIMITE)


def rodar(args, agora=time.time):
    with aberto(args.estado) as est:
        t = agora()
        if est.get("bloqueada_ate", 0) > t:
            falta = int(est["bloqueada_ate"] - t)
            print(f"[trava] bloqueada ({est.get('motivo')}); libera em {falta // 60} min. Nada foi chamado.", file=sys.stderr)
            return SAI_BLOQUEADA
        if args.max_chamadas and est["chamadas"] >= args.max_chamadas:
            print(f"[trava] orçamento de {args.max_chamadas} chamadas esgotado. Pare e avalie o resultado.", file=sys.stderr)
            return SAI_ORCAMENTO
        if args.max_falhas and est["falhas_seguidas"] >= args.max_falhas:
            print(f"[trava] {est['falhas_seguidas']} falhas seguidas. Parado até você olhar (trava.py liberar).", file=sys.stderr)
            return SAI_FALHAS
        est["chamadas"] += 1

    p = subprocess.run(args.comando, capture_output=True, text=True, timeout=args.timeout)
    sys.stdout.write(p.stdout)
    sys.stderr.write(p.stderr)
    saida = (p.stdout or "") + (p.stderr or "")

    with aberto(args.estado) as est:
        t = agora()
        reg = {"t": int(t), "rc": p.returncode}
        if sinal_de_limite(saida):
            est["bloqueada_ate"] = t + args.pausa_min * 60
            est["motivo"] = "limite de uso"
            reg["evento"] = "limite"
            est["historico"].append(reg)
            print(f"[trava] limite detectado: bloqueada por {args.pausa_min} min para todos que usam {args.estado}.", file=sys.stderr)
            return SAI_BLOQUEADA
        if p.returncode != 0:
            est["falhas_seguidas"] += 1
            reg["evento"] = "falha"
            if args.max_falhas and est["falhas_seguidas"] >= args.max_falhas:
                est["motivo"] = "falhas seguidas"
        else:
            est["falhas_seguidas"] = 0
            reg["evento"] = "ok"
        est["historico"].append(reg)
    return p.returncode


def status(args):
    with aberto(args.estado) as est:
        vis = {k: v for k, v in est.items() if k != "historico"}
        vis["ultimos"] = est.get("historico", [])[-5:]
    print(json.dumps(vis, ensure_ascii=False, indent=2))
    return 0


def liberar(args):
    with aberto(args.estado) as est:
        est.update({"bloqueada_ate": 0, "falhas_seguidas": 0, "motivo": ""})
        if args.zerar_chamadas:
            est["chamadas"] = 0
    print("[trava] liberada.", file=sys.stderr)
    return 0


def main(argv):
    ap = argparse.ArgumentParser(prog="trava.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("rodar")
    r.add_argument("--estado", default=".trava.json")
    r.add_argument("--max-chamadas", type=int, default=0, help="orçamento de chamadas da tarefa (0 = sem teto)")
    r.add_argument("--max-falhas", type=int, default=3)
    r.add_argument("--pausa-min", type=int, default=60, help="quanto tempo bloquear depois de um limite")
    r.add_argument("--timeout", type=int, default=1800)
    r.add_argument("comando", nargs=argparse.REMAINDER)
    s = sub.add_parser("status")
    s.add_argument("--estado", default=".trava.json")
    lb = sub.add_parser("liberar")
    lb.add_argument("--estado", default=".trava.json")
    lb.add_argument("--zerar-chamadas", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "rodar":
        if a.comando and a.comando[0] == "--":
            a.comando = a.comando[1:]
        if not a.comando:
            ap.error("faltou o comando depois de --")
        return rodar(a)
    return status(a) if a.cmd == "status" else liberar(a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
