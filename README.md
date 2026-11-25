# IA no jogo do dinossauro do Chrome

Trabalho da AV2 de Tópicos Avançados (FAETERJ-Rio, 2026.2)
Dupla: Renan Dias e Davy Andrade

A ideia é fazer uma IA aprender sozinha a jogar o jogo do dinossauro que aparece no Chrome quando cai a internet (`chrome://dino`). A gente não programou a hora de pular. Ela aprende jogando, batendo e tentando de novo, com Q-Learning.

Nessa primeira versão a IA só tem duas ações, não fazer nada ou pular. Agachar fica pra próxima etapa.

## Como rodar

Precisa de Python 3 e do Google Chrome instalado (o Selenium baixa o driver sozinho).

```
pip install -r requirements.txt

python treinar.py exp1 60        # treina o experimento 1 por 60 partidas (sem abrir janela)
python jogar.py exp1 10 teste    # testa a IA treinada em 10 partidas e salva o resultado
python jogar.py exp1             # abre o Chrome e mostra a IA jogando
python grafico.py                # gera os gráficos na pasta graficos/
```

Trocando `exp1` por `exp2` ou `exp3` roda os outros experimentos. As tabelas que treinamos já estão em `resultados/`, então dá pra rodar o `jogar.py` direto.

## Como funciona

O jogo é o do próprio Chrome, a gente não fez cópia dele. O Selenium abre o `chrome://dino` e, algumas dezenas de vezes por segundo, roda um JavaScript na página que pega as informações do jogo pelo objeto `Runner` do Chrome: distância até o próximo obstáculo, velocidade, tipo do obstáculo e se o dino bateu. Pra pular ele aperta a barra de espaço, igual uma pessoa.

A IA fica no `agente.py` e usa Q-Learning, que é um tipo de aprendizado por reforço:

- Estado (entrada): o que a IA enxerga do jogo, separado em faixas (`estados.py`). A distância, por exemplo, vai em faixas de 20 px.
- Ação (saída): 0 = não fazer nada, 1 = pular.
- Recompensa: +1 a cada decisão em que ele continua vivo, -5 quando pula (pra ele não sair pulando sem precisar) e -100 quando bate.
- Tabela Q: guarda uma nota pra cada ação em cada estado. Começa zerada e, depois de cada decisão, a nota é atualizada com a fórmula do Q-Learning:

```
Q(s,a) = Q(s,a) + alpha * (recompensa + gamma * maior Q(s') - Q(s,a))
```

Usamos alpha = 0.2, gamma = 0.9 e epsilon começando em 0.02 e caindo 5% a cada partida.

O dino só decide quando está no chão. No ar, apertar espaço não faz nada, então o programa espera ele cair e só aí avalia como foi o pulo.

Não tem base de dados pronta. Os dados são as próprias partidas: cada decisão vira uma experiência (estado, ação, recompensa, próximo estado) que atualiza a tabela. A tabela final fica salva em `resultados/expN/q_table.json` e o histórico das partidas em `treino.csv` e `teste.csv`.

## Experimentos

O código é o mesmo nos três, só muda o que a IA enxerga (`estados.py`):

| Experimento | O que a IA enxerga | Estados na tabela | Partidas de treino |
|---|---|---|---|
| exp1 | distância | 16 | 60 |
| exp2 | distância + velocidade | 80 | 58 |
| exp3 | distância + velocidade + tipo do obstáculo | 207 | 53 |

Os três treinaram ao mesmo tempo, uns 36 minutos de jogo cada. O exp2 e o exp3 pararam antes das 60 partidas porque o PC suspendeu e fechou os navegadores, mas a tabela é salva a cada partida e deu pra usar o que tinha.

Depois testamos cada tabela em 10 partidas, sem aprender e sem ação aleatória (`python jogar.py expN 10 teste`):

| Experimento | Média no teste | Menor | Maior | Média das últimas 10 do treino |
|---|---|---|---|---|
| exp1 | 849 | 41 | 1729 | 442 |
| exp2 | 694 | 495 | 969 | 573 |
| exp3 | 573 | 482 | 607 | 640 |

Gráficos em `graficos/`: `treino.png` (pontos por partida), `testes.png` (como terminou cada partida de teste) e `tabela_q_exp1.png` (as notas que o exp1 aprendeu).

O que deu pra ver:

- No treino, mais informação deu resultado melhor, como a gente esperava. No teste a ordem inverteu.
- O exp1 aprendeu basicamente uma regra: pular quando o obstáculo está entre 60 e 99 px. Nas velocidades altas funcionou bem e numa partida ele aguentou os 2 minutos. Mas foi o mais irregular: 4 das 10 partidas de teste acabaram antes de 235 pontos, ainda devagar.
- O exp1 não sabe a altura do obstáculo, então pula no pássaro alto (que passa por cima do dino) e bate. No treino morreu 15 vezes assim. O exp3, que sabe o tipo do obstáculo, morreu só 2.
- O exp3 nunca testou pular em 151 das 207 situações da tabela (o exp1 testou nas 16). Na velocidade 9 com cacto, a tabela final dele não manda pular em nenhuma distância, então no teste 9 das 10 partidas acabaram no primeiro cacto depois da velocidade 9. A nossa hipótese é que, com mais situações, o mesmo tempo de treino não foi suficiente.
- O cacto é o que mais mata nos três. Depois dele, o que mais matou o exp3 no treino foi o pássaro no meio (11 vezes), que dá pra passar agachando.

Foi um treino de cada versão e só 10 partidas de teste, então ainda não dá pra cravar qual é a melhor.

## Problemas que apareceram no caminho

- O `chrome://dino` sempre dá erro de "sem internet" no Selenium. É só ignorar o erro que o jogo abre normal.
- Nos tutoriais antigos o jogo é acessado por `Runner.instance_`, mas no Chrome 157 isso não existe mais. Agora é `Runner.getInstance()`.
- A velocidade às vezes sobe duas vezes mais rápido (o jogo roda duas atualizações por frame). Na primeira partida depois de abrir a página isso sempre acontece, e resolvemos forçando um game over logo no começo. Mas voltou em algumas partidas quando o PC suspendeu e quando abrimos outra janela do Chrome. A gente só percebeu calculando quantas atualizações por segundo cada partida teve (o normal é 60) e refez os testes do exp2 e do exp3.
- O jogo pausa sozinho quando a janela perde o foco. Por isso o treino roda com o Chrome sem janela (headless). Na demonstração usamos um comando do DevTools que faz a página achar que está sempre em foco.
- A chance de ação aleatória (epsilon) é sorteada em cada decisão, várias vezes por segundo. É provável que parte das mortes do treino tenha sido ação aleatória, por isso comparamos as versões pelo teste.
- O treino é em tempo real, então demora. Limitamos cada partida a 2 minutos (quando o jogo já está perto da velocidade máxima) e rodamos os três experimentos ao mesmo tempo.

## Arquivos

- `dino.py`: abre o Chrome, lê o jogo e aperta as teclas
- `agente.py`: a IA (tabela Q, escolher ação, aprender)
- `estados.py`: o que a IA enxerga em cada experimento
- `treinar.py`: treina e salva a tabela e o histórico
- `jogar.py`: coloca a IA treinada pra jogar (demonstração ou teste)
- `grafico.py`: gera os gráficos

## Próximos passos

- Agachar, pra passar por baixo do pássaro no meio
- Salvar no CSV as atualizações por segundo de cada partida e descartar as que dobraram
- Salvar se a ação que matou foi aleatória e explorar menos
- Treinar mais o exp3, ou usar o tempo até o obstáculo chegar (distância dividida pela velocidade) no lugar das duas coisas separadas
- Testar com mais partidas
