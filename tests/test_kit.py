import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
import conta  # noqa: E402
import trava  # noqa: E402


class Conta(unittest.TestCase):
    def plano(self, **k):
        p = {"agentes": 1, "rodadas": 1, "contexto": 1000, "tarefa": 0, "saida_por_agente": 100,
             "um_agente": {"rodadas": 1, "saida": 100}, "preco": {"entrada": 1.0, "saida": 1.0}}
        p.update(k)
        return p

    def test_enxame_custa_mais_que_um_agente(self):
        r = conta.estimar(self.plano(agentes=6, rodadas=3, mensagens_por_rodada=2, tamanho_mensagem=500,
                                     revisores=1, retrabalho=0.3))
        self.assertGreater(r["multiplicador_tokens"], 3)
        self.assertGreater(r["enxame"]["custo"], r["um_agente"]["custo"])
        self.assertAlmostEqual(sum(r["onde_vai"].values()), 100, delta=0.5)

    def test_conversa_entre_agentes_cresce_o_custo(self):
        sem = conta.estimar(self.plano(agentes=4, rodadas=4))
        com = conta.estimar(self.plano(agentes=4, rodadas=4, mensagens_por_rodada=3, tamanho_mensagem=800))
        self.assertGreater(com["enxame"]["entrada"], sem["enxame"]["entrada"])

    def test_limites_invalidos(self):
        with self.assertRaises(ValueError):
            conta.estimar(self.plano(agentes=0))
        with self.assertRaises(ValueError):
            conta.estimar(self.plano(retrabalho=1.5))

    def test_comparar_cru_e_veredito(self):
        ex = [{"arquitetura": "um_agente", "custo": 1, "aprovada": True},
              {"arquitetura": "um_agente", "custo": 1, "aprovada": False},
              {"arquitetura": "enxame", "custo": 4, "aprovada": True},
              {"arquitetura": "enxame", "custo": 4, "aprovada": True}]
        r = conta.comparar(ex)
        self.assertEqual(r["um_agente"]["cru"], 2.0)
        self.assertEqual(r["enxame"]["cru"], 4.0)
        self.assertIn("2.0× mais", r["veredito"])

    def test_enxame_sem_aprovacao_nao_vale(self):
        r = conta.comparar([{"arquitetura": "um_agente", "custo": 1, "aprovada": True},
                            {"arquitetura": "enxame", "custo": 9, "aprovada": False}])
        self.assertIn("não vale", r["veredito"])

    def test_falta_comparacao(self):
        r = conta.comparar([{"arquitetura": "enxame", "custo": 9, "aprovada": True}])
        self.assertIn("faltam", r["veredito"])

    def test_cli_exemplos(self):
        for cmd, arq in (("estimar", "plano-enxame.json"), ("comparar", "execucoes.json")):
            p = subprocess.run([sys.executable, str(RAIZ / "conta.py"), cmd, str(RAIZ / "exemplos" / arq)],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            json.loads(p.stdout)


class Trava(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.est = os.path.join(self.d, "t.json")

    def rodar(self, *cmd, extra=()):
        return subprocess.run([sys.executable, str(RAIZ / "trava.py"), "rodar", "--estado", self.est, *extra,
                               "--", *cmd], capture_output=True, text=True)

    def ler(self):
        with open(self.est) as f:
            return json.load(f)

    def test_ok_passa_e_conta(self):
        p = self.rodar("echo", "oi")
        self.assertEqual(p.returncode, 0)
        self.assertEqual(p.stdout.strip(), "oi")
        self.assertEqual(self.ler()["chamadas"], 1)

    def test_limite_bloqueia_e_nao_chama_de_novo(self):
        p = self.rodar("sh", "-c", "echo \"You've hit your weekly limit\"; exit 1")
        self.assertEqual(p.returncode, trava.SAI_BLOQUEADA)
        marca = os.path.join(self.d, "chamou")
        p = self.rodar("touch", marca)
        self.assertEqual(p.returncode, trava.SAI_BLOQUEADA)
        self.assertFalse(os.path.exists(marca), "a trava chamou o comando mesmo bloqueada")
        self.assertEqual(self.ler()["chamadas"], 1)

    def test_429_bloqueia(self):
        p = self.rodar("sh", "-c", "echo 'api_error_status: 429' >&2; exit 1")
        self.assertEqual(p.returncode, trava.SAI_BLOQUEADA)

    def test_orcamento(self):
        for _ in range(2):
            self.assertEqual(self.rodar("true", extra=("--max-chamadas", "2")).returncode, 0)
        self.assertEqual(self.rodar("true", extra=("--max-chamadas", "2")).returncode, trava.SAI_ORCAMENTO)

    def test_falhas_seguidas_param(self):
        for _ in range(2):
            self.assertEqual(self.rodar("false", extra=("--max-falhas", "2")).returncode, 1)
        self.assertEqual(self.rodar("true", extra=("--max-falhas", "2")).returncode, trava.SAI_FALHAS)

    def test_sucesso_zera_falhas(self):
        self.rodar("false", extra=("--max-falhas", "2"))
        self.rodar("true", extra=("--max-falhas", "2"))
        self.assertEqual(self.ler()["falhas_seguidas"], 0)

    def test_liberar(self):
        self.rodar("sh", "-c", "echo 'rate_limit_error'")
        subprocess.run([sys.executable, str(RAIZ / "trava.py"), "liberar", "--estado", self.est], capture_output=True)
        self.assertEqual(self.rodar("true").returncode, 0)

    def test_sinais(self):
        for t in ["HTTP 429", "rate limit reached", "You've hit your usage limit", "Quota exceeded"]:
            self.assertTrue(trava.sinal_de_limite(t), t)
        for t in ["tudo certo", "4290 linhas", "limitado a 3 itens"]:
            self.assertFalse(trava.sinal_de_limite(t), t)


if __name__ == "__main__":
    unittest.main()
