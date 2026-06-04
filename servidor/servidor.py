import socket
import json
import threading
import time
import season.team as team
import season.simulator as simulator
import season.player as player
import pandas as pd

# Configurações do Servidor
HOST = 'localhost'
PORT = 8080
MAX_CLIENTES = 2
NUMERO_TIMES = 4

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
        self.clientes_conectados = []  # Agora guardará tuplas: (socket_conexao, id_do_jogador)
        self.lock_jogo = threading.Lock() # Protege as variáveis globais contra race conditions
        self.turno_atual_index = 0
        self.draft, self.matches = escolha_times()

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
            "jogador_da_vez": cliente.id
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

    # --- OUVIR O CLIENTE ---
    def lidar_com_cliente(self, player , endereco_cliente):
        print(f"\n[INÍCIO] Thread iniciada para {player.id} ({endereco_cliente})")
        
        try:
            # Loop Persistente
            buffer = ""
            while True:
                dados = player.conexao.recv(4096)
                if not dados:
                    print(f"[DESCONECTADO] {player.id} desconectou-se.")
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
                                "remetente": player.id,
                                "mensagem": pacote.get("mensagem")
                            }
                            self.broadcast(msg_chat)
                        
                        # --- LÓGICA DE TURNO E DRAFT ---
                        elif tipo_evento == "DRAFT_ESCOLHA":
                            jogador_escolhido = pacote.get("jogador")
                            print(jogador_escolhido)
                            
                            with self.lock_jogo: # Adquire o Lock antes de checar e alterar o estado
                                ## VALIDA TURNO
                                cliente = self.clientes_conectados[self.turno_atual_index]
                                id_vez_atual = cliente.id
                                
                                if player.id != id_vez_atual:
                                    player.conexao.sendall((json.dumps({"tipo": "ERRO", "msg": "Não é o seu turno!"}) + '\n').encode('utf-8'))
                                    continue

                                ## ENCONTRA JOGADOR
                                encontrado = self.escolher_jogador_valido(jogador_escolhido, player)
                                if not encontrado: 
                                    player.conexao.sendall((json.dumps({"tipo": "ERRO", "msg": "Jogador indisponível ou inexistente."}) + '\n').encode('utf-8'))
                                    continue
                                
                                # PROCESSAMENTO DA ESCOLHA
                                #if encontrado:
                                #    self.jogadores_nba.remove(jogador_escolhido)
                                    
                                print(f"[DRAFT] {player.id} escolheu {encontrado.Player}!")
                                
                                # Avisa todo mundo da escolha
                                self.broadcast({
                                    "tipo": "DRAFT_SUCESSO",
                                    "quem_escolheu": player.id,
                                    "jogador_escolhido": jogador_escolhido,
                                })
                                
                                # 4. Passa o turno
                                self.turno_atual_index = (self.turno_atual_index + 1) % MAX_CLIENTES
                            
                            # Anuncia o novo turno (fora do lock para não segurar outras operações atoa)
                            self.anunciar_turno()

                    except json.JSONDecodeError:
                        print(f"[ERRO JSON] Falha ao decodificar pacote de {player.id}")
                        continue

        except Exception as e:
            print(f"[ERRO] Falha na comunicação com {player.id}: {e}")
        finally:
            player.conexao.close()
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
            id_jogador = f"Player_{contador_ids}"

            novo_Player = player.Player(id_jogador, conexao)
            self.clientes_conectados.append(novo_Player)

            contador_ids += 1
            
            print(f"[NOVA CONEXÃO] {id_jogador} entrou. ({len(self.clientes_conectados)}/{MAX_CLIENTES})")
            
            conexao.sendall((json.dumps({
                "tipo": "SERVIDOR", 
                "dados": f"Na sala de espera ({len(self.clientes_conectados)}/{MAX_CLIENTES}). Você é o {novo_Player.id}."
            }) + '\n').encode('utf-8'))


        # --- FASE 2: O JOGO COMEÇA ---
        print("\n[SALA CHEIA] A iniciar o jogo!")

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

        while True:
            time.sleep(1)

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