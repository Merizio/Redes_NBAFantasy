import team
import pandas as pd
import random
import time as tempo
import json
import threading
import simulator
import player

#COISAS PARA FAZER NO FUTURO = ADICIONAR ATRIBUIÇÕES AOS PONTOS (1.2X PARA WIN \ -X POR FALTA)

NUMERO_TIMES = 4
NUMERO_PLAYERS = 3

"""
SIMULADOR DE UMA TEMPORADA DA NBA
"""

def escolher_jogador_valido(jogador_draft, prompt):
    while True:
        nome = input(prompt)
        jogador = None
        for i in range(NUMERO_TIMES):
            if not jogador:
                jogador = teams[i].retornar_jogador(nome)

        if jogador and jogador_draft.add_jogador(jogador):
            break

        print('Escolha inválida. Tente novamente.')


#ESCOLHA DOS TIMES PARA O SIMULADOR
csv=pd.read_csv("simulator/data/list_nba_players.csv")

csv = csv.drop(columns=csv.columns[0])

teams = team.escolher_times(csv, NUMERO_TIMES)

matches = team.gerar_confrontos(NUMERO_TIMES)



## PROCESSO DE DRAFT DE JOGADORES
players = list()
[players.append(player.Player(i+1)) for i in range(NUMERO_PLAYERS)]

[teams[i].exibir_time() for i in range(NUMERO_TIMES)]

for i in range(2): # 5 NO JOGO NORMAL, 3 PARA TESTE RAPIDO
    print('SELEÇÃO', i)

    for i in range(NUMERO_PLAYERS):
        escolher_jogador_valido(players[i], f'P{i+1}: seleciona: ')

[players[i].exibir_draft() for i in range(NUMERO_PLAYERS)]
##DRAFT FEITO


##INICIO DA TEMPORADA
for rodada in range(matches.shape[0]):
    print("INICIANDO A RODADA:", rodada+1)

    threads = []

    for time_a, time_b in (matches[rodada]):
        jogo_thread = threading.Thread(
            target=simulator.simulator, 
            args=(teams[time_a], teams[time_b]) # Passa os times como argumentos
        )
        
        threads.append((jogo_thread, time_a, time_b))
        #[simulator.reset_team(teams[i]) for i in range(NUMERO_TIMES)]
        jogo_thread.start()

    for jogo_thread, time_a, time_b in threads:
        jogo_thread.join()

    
    for i in range(NUMERO_PLAYERS):
        for jogador_draft in players[i].draft:
            players[i].atribuir_points(jogador_draft)
    [simulator.reset_team(teams[i]) for i in range(NUMERO_TIMES)]
        
    print(f"--- TODOS OS JOGOS DA RODADA {rodada+1} ACABARAM ---")
    [players[i].exibir_draft() for i in range(NUMERO_PLAYERS)]
##FINAL DA TEMPORADA

##RESULTAODS
player.gerar_resultados(players, NUMERO_PLAYERS, matches.shape[0])