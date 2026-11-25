# Agente de Q-Learning (aprendizado por reforco).
# A tabela Q guarda, pra cada estado do jogo, uma nota pra cada acao.
# Quanto maior a nota, melhor a IA acha que e fazer aquela acao naquele estado.
# Ela comeca zerada e vai sendo preenchida conforme o dino joga e bate.

import json
import random

ACOES = ["nada", "pular"]


class AgenteQ:

    def __init__(self, n_acoes=2, alpha=0.2, gamma=0.9, epsilon=0.02):
        self.n_acoes = n_acoes
        self.alpha = alpha      # taxa de aprendizado (o quanto cada jogada muda a nota)
        self.gamma = gamma      # o quanto a IA leva em conta o que vem depois
        self.epsilon = epsilon  # chance de fazer uma acao aleatoria pra explorar
        self.q = {}

    def notas(self, estado):
        # estado que a IA nunca viu comeca com nota 0 em todas as acoes
        if estado not in self.q:
            self.q[estado] = [0.0] * self.n_acoes
        return self.q[estado]

    def escolher_acao(self, estado):
        if random.random() < self.epsilon:
            return random.randrange(self.n_acoes)
        notas = self.notas(estado)
        # se empatar fica com a primeira (nada)
        return notas.index(max(notas))

    def aprender(self, estado, acao, recompensa, prox_estado, acabou):
        # Q(s,a) = Q(s,a) + alpha * (recompensa + gamma * maior Q(s') - Q(s,a))
        atual = self.notas(estado)[acao]
        if acabou:
            alvo = recompensa
        else:
            alvo = recompensa + self.gamma * max(self.notas(prox_estado))
        self.q[estado][acao] = atual + self.alpha * (alvo - atual)

    def salvar(self, arquivo):
        # o json nao aceita tupla como chave, entao o estado vira texto tipo "3,1"
        dados = {}
        for estado in sorted(self.q):
            chave = ",".join(str(x) for x in estado)
            dados[chave] = [round(n, 3) for n in self.q[estado]]
        with open(arquivo, "w") as f:
            json.dump(dados, f, indent=1)

    def carregar(self, arquivo):
        with open(arquivo) as f:
            dados = json.load(f)
        self.q = {}
        for chave, notas in dados.items():
            estado = tuple(int(x) for x in chave.split(","))
            self.q[estado] = notas
