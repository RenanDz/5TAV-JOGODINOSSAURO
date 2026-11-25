# Parte que conversa com o jogo do dinossauro do Chrome (chrome://dino).
# O Selenium abre o Chrome, le as informacoes do jogo pelo JavaScript da
# pagina e aperta as teclas igual uma pessoa faria.

import time

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# Esse JavaScript roda dentro da pagina do jogo. O Runner e o objeto do
# proprio jogo do Chrome, dele da pra pegar o dino, os obstaculos, a
# velocidade e os pontos.
LER_JOGO = """
var jogo = Runner.getInstance();
var dino = jogo.tRex;

// se o jogo pausou sozinho (janela minimizada, por exemplo) volta a jogar
if (jogo.paused && !jogo.crashed) {
    jogo.play();
}

var frente_dino = dino.xPos + dino.config.width;

// pega o primeiro obstaculo que ainda nao passou do dino
var obst = null;
for (var i = 0; i < jogo.horizon.obstacles.length; i++) {
    var o = jogo.horizon.obstacles[i];
    if (o.xPos + o.width > dino.xPos) {
        obst = o;
        break;
    }
}

return {
    bateu: jogo.crashed,
    pontos: jogo.distanceMeter.getActualDistance(jogo.distanceRan),
    velocidade: jogo.currentSpeed,
    pulando: dino.jumping,
    tem_obstaculo: obst != null,
    distancia: obst ? obst.xPos - frente_dino : 999,
    largura: obst ? obst.width : 0,
    altura: obst ? obst.yPos : 0,
    tipo: obst ? obst.typeConfig.type : ""
};
"""

ESCREVER_TEXTO = """
var div = document.getElementById('texto-ia');
if (!div) {
    div = document.createElement('div');
    div.id = 'texto-ia';
    div.style = 'position:fixed; top:10px; left:10px; padding:6px 10px; background:#fff;'
        + 'color:#222; border:1px solid #bbb; font:15px monospace; white-space:pre;';
    document.body.appendChild(div);
}
div.innerText = arguments[0];
"""


class JogoDino:

    def __init__(self, mostrar_tela=True):
        opcoes = webdriver.ChromeOptions()
        if not mostrar_tela:
            opcoes.add_argument("--headless=new")  # sem janela, usado no treino
        opcoes.add_argument("--window-size=1000,500")
        opcoes.add_argument("--mute-audio")
        self.driver = webdriver.Chrome(options=opcoes)

        if mostrar_tela:
            # sem isso o jogo pausa quando a janela do Chrome perde o foco
            self.driver.execute_cdp_cmd("Emulation.setFocusEmulationEnabled", {"enabled": True})

        try:
            self.driver.get("chrome://dino")
        except WebDriverException:
            # o chrome://dino sempre da erro de "sem internet", mas o jogo abre normal
            pass
        time.sleep(1)

        # aperta espaco pra comecar e espera a animacao do comeco
        self.apertar(Keys.SPACE)
        time.sleep(2)

        # Na primeira partida do chrome://dino o jogo fica atualizando 2 vezes
        # por frame e a velocidade sobe em dobro. A gente descobriu isso nos
        # testes, entao forca um game over e reinicia, dai fica normal.
        self.reiniciar()

    def apertar(self, tecla):
        ActionChains(self.driver).send_keys(tecla).perform()

    def ler(self):
        info = self.driver.execute_script(LER_JOGO)
        # as vezes a pagina ainda nao respondeu (ex: recarregando), tenta de novo
        while info is None:
            time.sleep(0.1)
            info = self.driver.execute_script(LER_JOGO)
        return info

    def pular(self):
        self.apertar(Keys.SPACE)

    def reiniciar(self):
        # reinicia pelo proprio jogo, sem esperar a tela de game over
        if not self.driver.execute_script("return Runner.getInstance().crashed"):
            self.driver.execute_script("Runner.getInstance().gameOver()")
        time.sleep(0.3)
        self.driver.execute_script("Runner.getInstance().restart()")

    def mostrar_texto(self, texto):
        # escreve um quadrinho em cima do jogo (usado na demonstracao)
        self.driver.execute_script(ESCREVER_TEXTO, texto)

    def fechar(self):
        self.driver.quit()
