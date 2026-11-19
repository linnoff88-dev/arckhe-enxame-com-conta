# Caso real INEMA: o processo que bateu no limite 12.619 vezes (15–16/11/2026)

**O que aconteceu.** Um agendador automático de revisão de vídeos (o lote-135) chamava `claude -p` direto, sem
passar pela camada que controla cota. Quando o limite semanal da assinatura acabou, ele não parou: de 15/11 10:45
a 16/11 20:56 recebeu **12.619 recusas por limite (429)**, cerca de **400 por hora**, por ~34 horas.

**Quanto custou.** Dinheiro, quase nada: cada recusa voltava na porta, em ~4,7 s. O estrago foi outro:
- **34 horas sem revisão** de vídeo — o trabalho útil parou e ninguém viu;
- **4,9 GB** em 13 mil sessões de log inúteis no disco;
- o laço testava ~33 vídeos por ciclo sem parar no primeiro erro, então cada ciclo repetia o mesmo fracasso 33 vezes;
- o processo rodava fora da lista de timers e crons conhecida, então a correção feita no resto do sistema não chegou nele.

**A menor correção.** Não era reescrever o sistema. Faltavam três proteções:
1. parar no **primeiro** sinal de limite e gravar até quando esperar (todos os processos da conta leem a mesma trava);
2. erro encerra o ciclo, em vez de tentar o próximo item;
3. todo processo automático passa pela mesma camada de chamada — nada de `claude -p` fixo num script avulso.

A `trava.py` deste kit é a versão mínima das proteções 1 e 2. Corrigido no INEMA em 17/11/2026.

**A lição para enxames.** Um enxame é N processos chamando a IA ao mesmo tempo. Sem trava compartilhada,
o mesmo erro acontece N vezes mais rápido.
