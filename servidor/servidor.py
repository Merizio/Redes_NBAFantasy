import socket
import json
import threading
import time
import season.team as team
import season.simulator as simulator
import season.player as player
import pandas as pd
import random

# Configurações do Servidor
HOST = 'localhost'
PORT = 6789
MAX_CLIENTES = 3
NUMERO_TIMES = 4
MAX_RODADAS = 2

# --- FUNÇÕES PARA SUPORTE ---
def escolha_times():
    # ESCOLHA DOS TIMES PARA O SIMULADOR
    csv = pd.read_csv("data/list_nba_players.csv")
    csv = csv.drop(columns=csv.columns[0])
    teams = team.escolher_times(csv, NUMERO_TIMES)
    matches = team.gerar_confrontos(NUMERO_TIMES)
    return teams, matches

# --- CLASSE PRINCIPAL DO SERVIDOR ---
class ServidorFantasy:
    def __init__(self):
        
        # --- ESTADO GLOBAL DO JOGO (Agora protegido na classe) ---
        self.clientes_conectados = []
        self.lock_jogo = threading.Lock() # Protege as variáveis globais contra race conditions
        self.turno_atual_index = 0
        self.draft, self.matches = escolha_times()
        self.n_rodadas = MAX_CLIENTES*MAX_RODADAS
        self.draft_concluido = threading.Event()

    def broadcast(self, mensagem_dict):
        """Envia uma mensagem JSON para todos os clientes conectados."""
        pacote = (json.dumps(mensagem_dict) + '\n').encode('utf-8')
        for cliente in self.clientes_conectados:
            conexao = cliente.conexao
            try:
                conexao.sendall(pacote)
            except:
                pass # Lidar com erro de envio se necessário

    def anunciar_turno(self):
        """Avisa a todos de quem é a vez no momento."""
        cliente = self.clientes_conectados[self.turno_atual_index]
        msg = {
            "tipo": "TURNO_INFO",
            "jogador_da_vez": cliente.nick
        }
        self.broadcast(msg)


    def escolher_jogador_valido(self, nome_jogador, player):
        jogador = None
        while True:
            for i in range(NUMERO_TIMES):
                if not jogador:
                    jogador = self.draft[i].retornar_jogador(nome_jogador)

            if jogador and player.add_jogador(jogador):
                return jogador

            return None    
        
    def resultado_parcial(self):
        dados_finais = {
            manager.nick: [
                f"{jogador.Player:>25} | {jogador.Pos:<2} | {manager.pointlist[idx]:.2f}"
                for idx, jogador in enumerate(manager.draft)
            ]
            for manager in self.clientes_conectados
        }
        self.broadcast({
            "tipo": "FIM_DRAFT",
            "lista": dados_finais
            })
        
    def resultados_finais(self):
        resultado = list()
        for i in range(len(self.clientes_conectados)):
            resultado.append(self.clientes_conectados[i])

        resultado.sort(key=lambda Player: Player.points, reverse=True)
        for i in range(len(self.clientes_conectados)):
            print(f"{i+1}º Lugar!\n{resultado[i].nick} = {(resultado[i].points/MAX_RODADAS):.1f} pontos")

        resultados = {
            jogador.nick: f"{(jogador.points/MAX_RODADAS):.1f} pontos"
            for jogador in resultado
        }

        self.broadcast({
            'tipo': 'RESULTADO_FINAL',
            'lista': resultados
        })


    def simulator(self, time_A, time_B):
        match = {
            'tipo': "INICIO",
            'match': f"{time_A.nome} X {time_B.nome}",
            time_A.nome:{
                'titulares': time_A.exibir_titulares(),
                'reservas': time_A.exibir_resevas()
            },
            time_B.nome:{
                'titulares': time_B.exibir_titulares(),
                'reservas': time_B.exibir_resevas()
            }
        }

        match_event = json.dumps(match, ensure_ascii=False)

        print(match_event) #PRODUCE EVENT

        time_ataque, time_defesa = time_A, time_B

        #COMEÇAR O JOGO
        print("\nComeça a Partida")
        for i in range(4):    
            print(f"\n\nInício do {i+1}o quarto!  {time_A.nome} {time_A.pontos} X {time_B.pontos} {time_B.nome}")
            posses = random.randint(60, 80)

            for n in range(posses):
                model = {
                    'tipo': "EVENTO",
                    'time': time_ataque.nome,
                    'quarto': i+1,
                    'placar': f"{time_A.nome} {time_A.pontos} X {time_B.pontos} {time_B.nome}",
                    'detalhes': {}
                }
                event = model.copy()

                #ALEATORIZACAO DA JOGADA
                jogada = random.random()

                #SUBTITUICAO
                if(0.236<jogada<0.316):
                    jogador1 = team.escolher_jogador(time_ataque.titulares, 'min')
                    jogador2 = team.escolher_jogador(time_ataque.reservas, 'max')
                    #print(f"Mudança do {time_ataque.nome}: Sai {jogador1.Player} e entra {jogador2.Player}!")
                    
                    time_ataque.titulares.remove(jogador1)
                    time_ataque.reservas.remove(jogador2)
                    time_ataque.titulares.append(jogador2)
                    time_ataque.reservas.append(jogador1)

                    event_subs=model.copy()
                    event_subs['detalhes'] = {
                        'ação': "SUBSTITUTION",
                        'jogador_out': jogador1.Player,
                        'jogador_in': jogador2.Player,
                    }
                    event_subs_json = json.dumps(event_subs, ensure_ascii=False)
                    print(event_subs_json)

                #TURNOVER
                if(jogada<0.136):
                    jogador = team.escolher_jogador(time_ataque.titulares, 'max')
                    #print(f"O jogador {jogador.Player} do {time_ataque.nome} acaba de cometer um Turnover!")
                    event['detalhes'] = {
                        'ação': "TURNOVER",
                        'jogador': jogador.Player,
                    }
                
                #FALTA
                elif(0.136<jogada<0.236):
                    jogador1 = team.escolher_jogador(time_ataque.titulares, 'equal')
                    jogador2 = team.escolher_jogador(time_defesa.titulares, 'equal')
                    jogador1.fouls+=1
                    #print(f"Falta cometida pelo {jogador1.Player} no {jogador2.Player}! Bola pro {time_defesa.nome}!")
                    event['detalhes'] = {
                        'ação': "FOUL",
                        'jogador_commit': jogador1.Player,
                        'jogador_receive': jogador2.Player,
                    }

                #TENTATIVA DE ARREMESSO
                else:
                    jogador = team.escolher_jogador(time_ataque.titulares, 'max')
                    chance = random.random()
                    if(chance<0.585):
                        #2 PONTOS
                        chance = random.random()
                        if(chance <= jogador.FG):
                            #print(f"Jogador {jogador.Player} do {time_ataque.nome} fez uma cesta de 2 Pontos!")
                            time_ataque.pontos+=2
                            jogador.pts+=2
                            event['detalhes'] = {
                                'ação': "POINT",
                                'jogador': jogador.Player,
                                'valor': 2
                            }
                    else:
                        #3 PONTOS
                        chance = random.random()
                        if(chance <= jogador.P3):
                            #print(f"Jogador {jogador.Player} do {time_ataque.nome} fez uma cesta de 3 Pontos!")
                            time_ataque.pontos+=3
                            jogador.pts+=3
                            event['detalhes'] = {
                                'ação': "POINT",
                                'jogador': jogador.Player,
                                'valor': 3
                            }

                #INVERSAO DA POSSE
                time_ataque, time_defesa = time_defesa, time_ataque

                if(event!=model):
                    event_json = json.dumps(event, ensure_ascii=False)
                    print(event_json)

                #IDEIA DE TEMPO REAL
                time.sleep(0.05)

        if time_A.pontos <time_B.pontos:
            for jogador in (time_B.titulares + time_B.reservas):
                jogador.win = True
        else:
            for jogador in (time_A.titulares + time_A.reservas):
                jogador.win = True

        #CRIANDO JSON
        match_end = {
            'tipo': "FINAL_RODADA",
            'match': f"{time_A.nome} {time_A.pontos} X {time_B.pontos} {time_B.nome}",
        }

        match_event_end = json.dumps(match_end, ensure_ascii=False)

        #self.broadcast(match_event_end)

        print(match_event_end) #PRODUCE EVENT

        #STATUS FINAL DA PARTIDA
        print("\nFinal de Partida!\nEstatísticas Finais:\n")
        team.exibir_partida(time_A, time_B)

        #print(f" RETORNO DA FUNÇÃO SIMULADOR{time_A.nome} {time_A.pontos} X {time_B.pontos} {time_B.nome}")
        return f"{time_A.nome} {time_A.pontos} X {time_B.pontos} {time_B.nome}"


    def reset_team(self, time):
        time.pontos = 0
        for jogador in (time.titulares + time.reservas):
            jogador.pts = 0
            jogador.win = False
            jogador.fouls = 0
        


    # --- OUVIR O CLIENTE ---
    def lidar_com_cliente(self, cliente , endereco_cliente):
        print(f"\n[INÍCIO] Thread iniciada para {cliente.id} ({endereco_cliente})")
        
        try:
            # Loop Persistente
            buffer = ""
            while True:
                dados = cliente.conexao.recv(4096)
                if not dados:
                    print(f"[DESCONECTADO] {cliente.nick} desconectou-se.")
                    break

                buffer += dados.decode('utf-8')
                while '\n' in buffer:
                    linha, buffer = buffer.split('\n', 1)
                    if not linha.strip():
                        continue
                    try:
                        pacote = json.loads(linha)

                        ##RECEBEU A MENSAGEM
                        tipo_evento = pacote.get("tipo")
                        
                        # --- LÓGICA DE CHAT ---
                        if tipo_evento == "CHAT":
                            msg_chat = {
                                "tipo": "CHAT_BROADCAST",
                                "remetente": cliente.nick,
                                "mensagem": pacote.get("mensagem")
                            }
                            self.broadcast(msg_chat)
                            print(pacote.get('mensagem'))
                        
                        # --- LÓGICA DE TURNO E DRAFT ---
                        elif tipo_evento == "DRAFT_ESCOLHA":
                            jogador_escolhido = pacote.get("jogador")
                            print(jogador_escolhido)
                            
                            with self.lock_jogo: # Adquire o Lock antes de checar e alterar o estado
                                ## VALIDA TURNO
                                aux = self.clientes_conectados[self.turno_atual_index]
                                id_vez_atual = aux.id
                                
                                if cliente.id != id_vez_atual:
                                    cliente.conexao.sendall((json.dumps({"tipo": "ERRO", "msg": "Não é o seu turno!"}) + '\n').encode('utf-8'))
                                    continue

                                ## ENCONTRA JOGADOR
                                encontrado = self.escolher_jogador_valido(jogador_escolhido, cliente)
                                if not encontrado: 
                                    cliente.conexao.sendall((json.dumps({"tipo": "ERRO", "msg": "Jogador indisponível ou inexistente."}) + '\n').encode('utf-8'))
                                    self.anunciar_turno()
                                    continue

                                # PROCESSAMENTO DA ESCOLHA
                                #if encontrado:
                                #    self.jogadores_nba.remove(jogador_escolhido)
                                else: 
                                    print(f"[DRAFT] {cliente.id} escolheu {encontrado.Player}!")
                                    
                                    # Avisa todo mundo da escolha
                                    self.broadcast({
                                        "tipo": "DRAFT_SUCESSO",
                                        "quem_escolheu": cliente.nick,
                                        "jogador_escolhido": encontrado.Player,
                                    })
                                    
                                    # 4. Passa o turno
                                    self.turno_atual_index = (self.turno_atual_index + 1) % len(self.clientes_conectados)
                            
                            # Anuncia o novo turno (fora do lock para não segurar outras operações atoa)
                            if self.n_rodadas>1 and encontrado:
                                self.anunciar_turno()
                                self.n_rodadas-=1
                                print(self.n_rodadas)
                            elif encontrado:
                                self.resultado_parcial()
                                self.draft_concluido.set()

                        ## --- LOGICA DA SIMULAÇÃO ---

                    except json.JSONDecodeError:
                        print(f"[ERRO JSON] Falha ao decodificar pacote de {cliente.id}")
                        continue

        except Exception as e:
            print(f"[ERRO] Falha na comunicação com {cliente.id}: {e}")
        finally:
            cliente.conexao.close()
            # Idealmente, aqui você lida com a remoção do cliente da lista e recalcula o turno

    # --- ESCREVER PARA O CLIENTE ---
    def iniciar_servidor(self):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PORT))
        servidor.listen()
        print(f"[SERVIDOR INICIADO] A ouvir na porta {PORT}...")

        # --- FASE 1: SALA DE ESPERA ---
        contador_ids = 1
        while len(self.clientes_conectados) < MAX_CLIENTES:
            conexao, endereco = servidor.accept()

            conexao.sendall((json.dumps({"tipo": "SOLICITAR_NICK"}) + '\n').encode('utf-8'))

            dados = conexao.recv(1024)
            if dados:
                pacote = json.loads(dados.decode('utf-8').strip())
                nick_escolhido = pacote.get("nick", f"Player_{len(self.clientes_conectados)+1}")
            else:
                continue

            novo_Player = player.Player(contador_ids, nick_escolhido, conexao)
            self.clientes_conectados.append(novo_Player)
            
            print(f"[NOVA CONEXÃO] ({contador_ids}) {nick_escolhido} entrou. ({len(self.clientes_conectados)}/{MAX_CLIENTES})")
            contador_ids += 1

            conexao.sendall((json.dumps({
                "tipo": "SERVIDOR", 
                "dados": f"Na sala de espera ({len(self.clientes_conectados)}/{MAX_CLIENTES}). Você é o {novo_Player.nick}."
            }) + '\n').encode('utf-8'))


        # --- FASE 2: O JOGO COMEÇA ---
        while 1:
            if input("\n[SALA CHEIA] start para iniciar o jogo!: ")=="start":
                break

        times_season = {
            f"Time_{i}": {
                "nome": self.draft[i].nome,
                "elenco": [f"{jogador.Player} | {jogador.Pos} | {jogador.FG*100:.2f} FG% | {jogador.P3*100:.2f} 3P%" for jogador in self.draft[i].titulares]
            } 
            for i in range(NUMERO_TIMES)
        }

        # Serializa para JSON
        json_times = json.dumps({"tipo": "TIMES", "dados": times_season})
        
        self.broadcast({
            "tipo": "DRAFT_LISTA",
            "jogadores_disponiveis": json_times
        })

        # Cria as Threads
        for player_cliente in self.clientes_conectados:
            endereco = player_cliente.conexao.getpeername() 
            thread_cliente = threading.Thread(target=self.lidar_com_cliente, args=(player_cliente, endereco))
            thread_cliente.daemon = True 
            thread_cliente.start()

        # O servidor dispara o primeiro turno logo após iniciar as threads
        time.sleep(0.5) # Um pequeno delay para garantir que as threads do cliente já estão ouvindo
        self.anunciar_turno()

        print("\n[SERVIDOR] Aguardando os clientes finalizarem o Draft...")
        
        # O main loop fica pausado aqui até alguém chamar self.draft_concluido.set()
        self.draft_concluido.wait() 
        
        print("\n[SERVIDOR] Draft finalizado!")
        while 1:
            if input("\n[SERVIDOR] Digite play para iniciar a simulação!: ")=="play":
                self.broadcast({'tipo': "INICIO_SEASON"})
                break
        
        print("Iniciando as simulações dos confrontos...")
        time.sleep(1)
        print("\nEm 3..")
        time.sleep(1)
        print("\nEm 2..")
        time.sleep(1)
        print("\nEm 1..")
        time.sleep(1)

        ## --- FASE 3: SIMULAÇÃO DA TEMPORADA ---
        ##INICIO DA TEMPORADA
        for rodada in range(self.matches.shape[0]):
            print("INICIANDO A RODADA:", rodada+1)

            resultados_jogos = list()
            def rodar_e_salvar(ta, tb):
                # Roda a sua função matemática original
                res = self.simulator(ta, tb)
                # Salva o retorno diretamente na lista do escopo pai
                resultados_jogos.append({
                    "resultado": res
                })

            threads = []

            for time_a, time_b in (self.matches[rodada]):
                jogo_thread = threading.Thread(
                    target=rodar_e_salvar, 
                    args=(self.draft[time_a], self.draft[time_b]) # Passa os times como argumentos
                )
                
                threads.append((jogo_thread, time_a, time_b))
                #[simulator.reset_team(teams[i]) for i in range(NUMERO_TIMES)]
                jogo_thread.start()

            for jogo_thread, time_a, time_b in threads:
                jogo_thread.join()

            
            for i in range(len(self.clientes_conectados)):
                for jogador_draft in self.clientes_conectados[i].draft:
                    self.clientes_conectados[i].atribuir_points(jogador_draft)
            [self.reset_team(self.draft[i]) for i in range(NUMERO_TIMES)]
                
            print(f"--- TODOS OS JOGOS DA RODADA {rodada+1} ACABARAM ---")
            [self.clientes_conectados[i].exibir_draft() for i in range(len(self.clientes_conectados))]

            time.sleep(3)
            
            #CRIANDO JSON
            match_end = {
                'tipo': "FINAL_RODADA",
                'rodada': rodada+1,
                'match': resultados_jogos
            }
            self.broadcast(match_end)

            self.resultado_parcial()

            time.sleep(5)
        ##FINAL DA TEMPORADA

        self.resultados_finais()

        time.sleep(1)
        self.broadcast({
            'tipo': "SERVIDOR",
            'dados': "OBRIGADO POR JOGAR!"
        })

# A função de testes pode continuar fora da classe, 
# já que é apenas para você debugar o seu código de dataframes localmente.
def testes():
    draft, matches = escolha_times()

    times_season = {
        f"Time_{i}": {
            "nome": draft[i].nome,
            "elenco": [f"{jogador.Player} | {jogador.Pos} | {jogador.FG*100:.2f} FG% | {jogador.P3*100:.2f} 3P%" for jogador in draft[i].titulares]
        } 
        for i in range(NUMERO_TIMES)
    }

    # Serializa para JSON
    json_times = json.dumps({"tipo": "TIMES", "dados": times_season})

    retorno = json.loads(json_times)

    for chave_time, time_info in retorno["dados"].items():
        print(f"\n--- {time_info['nome']} ---")
        print("Elenco:")
        for jogador in time_info["elenco"]:
            # Se a vaga estiver vazia (None no Python, null no JSON), exibe Vaga Livre
            print(f"  {jogador if jogador is not None else '[Vaga Livre]'}")

if __name__ == "__main__":
    servidor_ativo = ServidorFantasy()
    servidor_ativo.iniciar_servidor()
    # testes()