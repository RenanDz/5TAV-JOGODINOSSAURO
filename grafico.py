# Gera os graficos dos experimentos pra usar na apresentacao.
# Como usar (depois de treinar e testar):  python grafico.py
# As imagens vao pra pasta graficos/

import csv
import json
import os
import sys

import matplotlib.pyplot as plt

NOMES = {
    "exp1": "Exp 1: distância",
    "exp2": "Exp 2: distância + velocidade",
    "exp3": "Exp 3: distância + velocidade + tipo",
}
CORES = {"exp1": "tab:blue", "exp2": "tab:orange", "exp3": "tab:green"}
JANELA = 10  # media das ultimas 10 partidas


def ler_csv(caminho):
    if not os.path.exists(caminho):
        return []
    with open(caminho) as f:
        return list(csv.DictReader(f))


def media_movel(valores, janela):
    medias = []
    for i in range(len(valores)):
        pedaco = valores[max(0, i - janela + 1):i + 1]
        medias.append(sum(pedaco) / len(pedaco))
    return medias


treinos = {}
testes = {}
for exp in NOMES:
    linhas = ler_csv(os.path.join("resultados", exp, "treino.csv"))
    if linhas:
        treinos[exp] = linhas
    linhas = ler_csv(os.path.join("resultados", exp, "teste.csv"))
    if linhas:
        testes[exp] = linhas

if not treinos:
    print("nao achei resultados/expN/treino.csv, roda na pasta do projeto depois de treinar")
    sys.exit()

os.makedirs("graficos", exist_ok=True)

# 1) pontos por partida no treino
plt.figure(figsize=(10, 5.5))
for exp, linhas in treinos.items():
    partidas = [int(l["partida"]) for l in linhas]
    pontos = [int(l["pontos"]) for l in linhas]
    plt.plot(partidas, pontos, color=CORES[exp], alpha=0.25, linewidth=1)
    plt.plot(partidas, media_movel(pontos, JANELA), color=CORES[exp], linewidth=2, label=NOMES[exp])

plt.title("Pontos por partida no treino (linha fina = partida, linha grossa = média de 10)")
plt.xlabel("partida")
plt.ylabel("pontos")
plt.grid(alpha=0.3)
plt.legend(loc="upper left")
plt.tight_layout()
plt.savefig("graficos/treino.png", dpi=150)
plt.close()
print("salvou graficos/treino.png")

# 2) como terminou cada partida de teste (sem aprender e sem acao aleatoria)
if testes:
    causas = ["cacto", "passaro baixo", "passaro meio", "passaro alto", "nao bateu"]
    rotulos = ["cacto", "pássaro baixo", "pássaro no meio", "pássaro alto", "não bateu\n(2 min sem bater)"]
    largura = 0.8 / len(testes)

    plt.figure(figsize=(10, 5.5))
    for i, (exp, linhas) in enumerate(testes.items()):
        contagem = [sum(1 for l in linhas if l["bateu_em"] == c) for c in causas]
        posicoes = [x - 0.4 + largura * i + largura / 2 for x in range(len(causas))]
        media = sum(int(l["pontos"]) for l in linhas) / len(linhas)
        plt.bar(posicoes, contagem, width=largura, color=CORES[exp],
                label=f"{NOMES[exp]} ({len(linhas)} partidas, média {media:.0f} pontos)")

    plt.xticks(range(len(causas)), rotulos)
    plt.yticks(range(0, 11))
    plt.ylabel("partidas")
    plt.title("Como terminaram as partidas de teste")
    plt.grid(axis="y", alpha=0.3)
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig("graficos/testes.png", dpi=150)
    plt.close()
    print("salvou graficos/testes.png")

# 3) o que a IA aprendeu no exp1: as duas notas da tabela Q pra cada distancia
caminho_q = os.path.join("resultados", "exp1", "q_table.json")
if os.path.exists(caminho_q):
    with open(caminho_q) as f:
        tabela = json.load(f)
    faixas = list(range(16))
    nada = [tabela.get(str(fx), [0, 0])[0] for fx in faixas]
    pular = [tabela.get(str(fx), [0, 0])[1] for fx in faixas]
    nomes_faixas = ["< 20"] + [f"{fx * 20}-{fx * 20 + 19}" for fx in faixas[1:-1]] + ["300+ ou\nnenhum"]

    plt.figure(figsize=(11, 5.5))
    plt.bar([x - 0.2 for x in faixas], nada, width=0.4, color="tab:gray", label="nota de não fazer nada")
    plt.bar([x + 0.2 for x in faixas], pular, width=0.4, color="tab:blue", label="nota de pular")
    plt.axhline(0, color="black", linewidth=0.8)
    plt.xticks(faixas, nomes_faixas, rotation=45)
    plt.xlabel("distância até o próximo obstáculo (px)")
    plt.ylabel("nota na tabela Q")
    plt.title("Tabela Q do Exp 1: em cada distância a IA escolhe a ação com a maior nota")
    plt.grid(axis="y", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("graficos/tabela_q_exp1.png", dpi=150)
    plt.close()
    print("salvou graficos/tabela_q_exp1.png")
