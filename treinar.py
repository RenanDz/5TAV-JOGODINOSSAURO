# Treina a IA jogando o chrome://dino de verdade (em tempo real, sem janela).
# Como usar:
#   python treinar.py exp1 100
#   (nome do experimento e quantas partidas jogar)
#   python treinar.py exp1 10 tela
#   (abre o Chrome pra ver aprendendo do zero, salva em resultados/exp1_ao_vivo)

import csv
import os
import sys
import time

from agente import ACOES, AgenteQ
from dino import JogoDino
from estados import EXPERIMENTOS, nome_obstaculo

RECOMPENSA_VIVO = 1      # a cada decisao em que ele continua vivo
CUSTO_PULO = 5           # pular custa um pouco, senao ele fica pulando a toa
RECOMPENSA_BATEU = -100
TEMPO_MAXIMO = 120       # segundos (em 2 min o jogo ja ta perto da velocidade maxima)

experimento = "exp1"
total_partidas = 100
if len(sys.argv) > 1:
    experimento = sys.argv[1]
if len(sys.argv) > 2:
    total_partidas = int(sys.argv[2])

# "tela" abre o Chrome pra ver ele aprendendo do zero (usado na apresentacao).
# Salva em outra pasta pra nao apagar o treino de verdade.
modo_tela = "tela" in sys.argv

pegar_estado = EXPERIMENTOS[experimento]
pasta = os.path.join("resultados", experimento)
if modo_tela:
    pasta = os.path.join("resultados", experimento + "_ao_vivo")
os.makedirs(pasta, exist_ok=True)

agente = AgenteQ()
jogo = JogoDino(mostrar_tela=modo_tela)

arquivo = open(os.path.join(pasta, "treino.csv"), "w", newline="")
csv_treino = csv.writer(arquivo)
csv_treino.writerow(["partida", "pontos", "velocidade", "bateu_em", "pulos", "epsilon", "segundos"])
arquivo.flush()

print(f"Treinando {experimento} por {total_partidas} partidas")

for partida in range(1, total_partidas + 1):
    inicio = time.time()
    estado = None
    acao = None
    pulos = 0

    while True:
        time.sleep(0.02)
        info = jogo.ler()

        if info["bateu"]:
            if estado is not None:
                agente.aprender(estado, acao, RECOMPENSA_BATEU, None, True)
            break

        if time.time() - inicio > TEMPO_MAXIMO:
            break

        # no ar nao tem o que decidir, so espera cair
        if info["pulando"]:
            continue

        novo_estado = pegar_estado(info)

        # agora que viu o resultado, aprende com a decisao anterior
        if estado is not None:
            recompensa = RECOMPENSA_VIVO
            if acao == 1:
                recompensa -= CUSTO_PULO
            agente.aprender(estado, acao, recompensa, novo_estado, False)

        acao = agente.escolher_acao(novo_estado)
        if acao == 1:
            jogo.pular()
            pulos += 1
        estado = novo_estado

        if modo_tela:
            notas = agente.notas(estado)
            jogo.mostrar_texto(f"TREINANDO  partida {partida}  |  estados aprendidos: {len(agente.q)}\n"
                               f"estado {estado}  distancia: {info['distancia']:.0f} px\n"
                               f"nota nada: {notas[0]:.1f}  nota pular: {notas[1]:.1f}\n"
                               f"acao: {ACOES[acao].upper()}")

    if info["bateu"]:
        bateu_em = nome_obstaculo(info)
    else:
        bateu_em = "nao bateu"
    segundos = round(time.time() - inicio, 1)

    csv_treino.writerow([partida, info["pontos"], round(info["velocidade"], 2), bateu_em,
                         pulos, round(agente.epsilon, 4), segundos])
    arquivo.flush()
    print(f"partida {partida:3d} | pontos {info['pontos']:5d} | velocidade {info['velocidade']:5.2f} | bateu em: {bateu_em}")

    agente.epsilon = agente.epsilon * 0.95
    agente.salvar(os.path.join(pasta, "q_table.json"))
    if modo_tela:
        time.sleep(1.5)  # da tempo de ver onde ele bateu
    jogo.reiniciar()

arquivo.close()
jogo.fechar()
print("Fim do treino")
