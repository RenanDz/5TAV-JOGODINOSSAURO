# Coloca a IA ja treinada pra jogar, sem aprender e sem acao aleatoria.
# Como usar:
#   python jogar.py exp1              -> abre o Chrome e joga 3 partidas (demonstracao)
#   python jogar.py exp1 10 teste     -> joga 10 partidas sem janela e salva em teste.csv

import csv
import os
import sys
import time

from agente import ACOES, AgenteQ
from dino import JogoDino
from estados import EXPERIMENTOS, nome_obstaculo

TEMPO_MAXIMO = 120  # mesmo limite do treino (2 min)

experimento = "exp1"
partidas = 3
if len(sys.argv) > 1:
    experimento = sys.argv[1]
if len(sys.argv) > 2:
    partidas = int(sys.argv[2])
modo_teste = "teste" in sys.argv

pegar_estado = EXPERIMENTOS[experimento]
pasta = os.path.join("resultados", experimento)

agente = AgenteQ(epsilon=0)
agente.carregar(os.path.join(pasta, "q_table.json"))

jogo = JogoDino(mostrar_tela=not modo_teste)
linhas = []

if modo_teste:
    # salva cada partida assim que acaba, pra nao perder tudo se parar no meio
    arquivo = open(os.path.join(pasta, "teste.csv"), "w", newline="")
    saida = csv.writer(arquivo)
    saida.writerow(["partida", "pontos", "velocidade", "bateu_em", "segundos"])

for partida in range(1, partidas + 1):
    inicio = time.time()

    while True:
        time.sleep(0.02)
        info = jogo.ler()

        if info["bateu"] or time.time() - inicio > TEMPO_MAXIMO:
            break
        if info["pulando"]:
            continue

        estado = pegar_estado(info)
        acao = agente.escolher_acao(estado)
        if acao == 1:
            jogo.pular()

        if not modo_teste:
            notas = agente.notas(estado)
            jogo.mostrar_texto(f"{experimento}  |  estado {estado}\n"
                               f"distancia: {info['distancia']:.0f} px  velocidade: {info['velocidade']:.1f}\n"
                               f"nota nada: {notas[0]:.1f}  nota pular: {notas[1]:.1f}\n"
                               f"acao: {ACOES[acao].upper()}")

    if info["bateu"]:
        bateu_em = nome_obstaculo(info)
    else:
        bateu_em = "nao bateu"
    segundos = round(time.time() - inicio, 1)
    linha = [partida, info["pontos"], round(info["velocidade"], 2), bateu_em, segundos]
    linhas.append(linha)
    if modo_teste:
        saida.writerow(linha)
        arquivo.flush()
    print(f"partida {partida} | pontos {info['pontos']} | bateu em: {bateu_em}")

    if not modo_teste:
        time.sleep(2)  # da tempo de ver onde ele bateu
    jogo.reiniciar()

jogo.fechar()

pontos = [l[1] for l in linhas]
print(f"media: {sum(pontos) / len(pontos):.0f} | maior: {max(pontos)} | menor: {min(pontos)}")

if modo_teste:
    arquivo.close()
