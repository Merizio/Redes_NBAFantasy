import team
import pandas as pd
import random
import time as tempo
import json
import threading
import simulator
import player

NUMERO_TIMES = 2

"""
SIMULADOR DE UMA TEMPORADA DA NBA
"""

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

for i in range(5):
    print('SELEÇÃO', i)

    nome = input('P1: seleciona')
    

#CRIAR OS DOIS PLAYERS
#MOSTRAR OS JOGADORES
#ADICIONAR O JOGADOR NO DRAFT DO PLAYER




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