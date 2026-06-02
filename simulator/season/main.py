import team
import pandas as pd
import random
import time as tempo
import json
import threading
import simulator
import player

"""
COISAS PARA FAZER NO FUTURO
    ADICIONAR ATRIBUIÇÕES AOS PONTOS (1.2X PARA WIN \ -X POR FALTA)
"""

NUMERO_TIMES = 2

"""
SIMULADOR DE UMA TEMPORADA DA NBA
"""

def escolher_jogador_valido(jogador_draft, prompt):
    while True:
        nome = input(prompt)
        jogador = teams[0].retornar_jogador(nome)

        if not jogador:
            jogador = teams[1].retornar_jogador(nome)

        if jogador and jogador_draft.add_jogador(jogador):
            break

        print('Escolha inválida. Tente novamente.')

#ESCOLHA DOS TIMES PARA O SIMULADOR
csv=pd.read_csv("simulator/data/list_nba_players.csv")

csv = csv.drop(columns=csv.columns[0])

teams = team.escolher_times(csv, NUMERO_TIMES)

matches = team.gerar_confrontos(NUMERO_TIMES)



#simulator.simulator(teams[0], teams[1])

## PROCESSO DE DRAFT DE JOGADORES
p1 = player.Player(1)
p2 = player.Player(2)

team.Time.exibir_time(teams[0])
team.Time.exibir_time(teams[1])

for i in range(3):
    print('SELEÇÃO', i)

    ##PLAYER 1 SELECIONA UM JOGADOR
    escolher_jogador_valido(p1, 'P1: seleciona: ')

    escolher_jogador_valido(p2, 'P2: seleciona: ')

p1.exibir_draft()
p2.exibir_draft()

##DRAFT FEITO


##COMEÇAR AS SIMULAÇÕES
for i in range(2):
    simulator.simulator(teams[0], teams[1])

    ##ATUALIZAR A PONTUAÇÃO DOS JOGADORES NOS DRAFTS
    for jogador_draft in p1.draft:
        p1.atribuir_points(jogador_draft)

    for jogador_draft in p2.draft:
        p2.atribuir_points(jogador_draft)

    p1.exibir_draft()
    p2.exibir_draft()



##RODANDO TODOS OS JOGOS DA TEMPORADA

"""for rodada in range(matches.shape[0]):
    print("INICIANDO A RODADA:", rodada)

    threads = []

    for time_a, time_b in (matches[rodada]):
        jogo_thread = threading.Thread(
            target=simulator.simulator, 
            args=(teams[time_a], teams[time_b]) # Passa os times como argumentos
        )
        
        threads.append(jogo_thread)
        jogo_thread.start()

    for jogo_thread in threads:
        jogo_thread.join()
        
    print(f"--- TODOS OS JOGOS DA RODADA {rodada} ACABARAM ---")"""








#team.exibir_simples(teams[0], teams[1])

key = f"Game_{random.randrange(100,199)}"

#CRIANDO JSON
match = {
    'tipo': "INICIO",
    'match': f"{teams[0].nome} X {teams[1].nome}",
    teams[0].nome:{
        'titulares': teams[0].exibir_titulares(),
        'reservas': teams[0].exibir_resevas()
    },
    teams[1].nome:{
        'titulares': teams[1].exibir_titulares(),
        'reservas': teams[1].exibir_resevas()
    }
}

match_event = json.dumps(match, ensure_ascii=False)
#print(match_event)