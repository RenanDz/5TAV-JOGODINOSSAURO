# O que a IA "enxerga" do jogo em cada experimento.
# O jogo devolve valores soltos (distancia 137, velocidade 7.83...)
# e a tabela Q precisa de estados que da pra contar, entao a gente
# separa os valores em faixas.


def faixa_distancia(info):
    # faixas de 20 px. Acima de 300 px (ou sem obstaculo) vira tudo "longe"
    if not info["tem_obstaculo"] or info["distancia"] >= 300:
        return 15
    if info["distancia"] < 0:
        return 0
    return int(info["distancia"] // 20)


def faixa_velocidade(info):
    # a velocidade do jogo comeca em 6 e vai ate 13
    return int(info["velocidade"]) - 6


def tipo_obstaculo(info):
    # 0 = cacto, 1 = passaro baixo, 2 = passaro no meio, 3 = passaro alto
    # "altura" e o yPos do jogo, que cresce pra baixo (100 = baixo, 50 = alto)
    if info["tipo"] != "pterodactyl":
        return 0
    if info["altura"] >= 100:
        return 1
    if info["altura"] >= 75:
        return 2
    return 3


def estado_exp1(info):
    # experimento 1: so a distancia ate o proximo obstaculo
    return (faixa_distancia(info),)


def estado_exp2(info):
    # experimento 2: distancia + velocidade
    return (faixa_distancia(info), faixa_velocidade(info))


def estado_exp3(info):
    # experimento 3: distancia + velocidade + tipo do obstaculo
    return (faixa_distancia(info), faixa_velocidade(info), tipo_obstaculo(info))


EXPERIMENTOS = {
    "exp1": estado_exp1,
    "exp2": estado_exp2,
    "exp3": estado_exp3,
}


def nome_obstaculo(info):
    # so pra deixar o log mais facil de ler
    nomes = ["cacto", "passaro baixo", "passaro meio", "passaro alto"]
    return nomes[tipo_obstaculo(info)]
