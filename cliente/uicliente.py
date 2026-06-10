import socket
import threading
import json
import sys
import time
from rich.live import Live
from layout import TelaDoJogo
from rich.console import Console
import os

os.system('')
console_grafico = Console()

# --- CLASSE PRINCIPAL DO CLIENTE ---
class ClienteFantasy:
    def __init__(self, host, port):
        # Configurações de conexão
        self.host = host
        self.port = port
        self.tela = TelaDoJogo()
        self.historico_chat = []

        # Flags
        self.nick_confirmado = False
        
        # Estado Local do Cliente
        self.meu_id = None          # Será preenchido quando o servidor nos disser quem somos
        self.e_minha_vez = False    # Controla se o teclado está liberado para o Draft
        self.cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def exibir_draft(self, times):
        retorno = json.loads(times)

        print("\nATLETAS DISPONÍVEIS:")
        for chave_time, time_info in retorno["dados"].items():
            print(f"--- {time_info['nome']} ---")
            print("Elenco:")
            for jogador in time_info["elenco"]:
                # Se a vaga estiver vazia (None no Python, null no JSON), exibe Vaga Livre
                print(f"  {jogador if jogador is not None else '[Vaga Livre]'}")
                self.tela.atualizar_draft(f"  {jogador if jogador is not None else '[Vaga Livre]'}")
            print()

    def exibir_resultados(self, lista):
        #lista = json.loads(drafts)

        for  chave, jogadores in lista.items():
            print(f"---{chave}---")
            for jogador in jogadores:
                print(jogador)

    def atualizar_status_servidor(self, texto):
        self.tela.atualizar_servidor(texto)

    def ouvir_servidor(self):
        buffer = ""
        try:
            while True:
                dados = self.cliente_socket.recv(4096)
                if not dados:
                    print("\n[AVISO] O servidor encerrou a conexão.")
                    break

                buffer += dados.decode('utf-8')
                while '\n' in buffer:
                    linha, buffer = buffer.split('\n', 1)
                    if not linha.strip():
                        continue
                    try:
                        pacote = json.loads(linha)
                    except json.JSONDecodeError as e:
                        print(f"\n[ERRO] JSON inválido do servidor: {e}")
                        continue
                    
                    tipo = pacote.get("tipo")

                    ## IDENTIFICAÇÃO DO SERVIDOR
                    if tipo == "SERVIDOR":
                        self.atualizar_status_servidor(pacote.get('dados'))
                        # Se o servidor enviou o ID atribuído a este cliente
                        if "Você é o" in pacote.get('dados'):
                            # Extrai o ID do texto (Ex: "Player_1")
                            self.meu_id = pacote.get('dados').split("Você é o ")[1].replace(".", "").strip()

                    ## (Coloque isso junto com os outros if/elif)
                    elif tipo == "SOLICITAR_NICK":
                        self.atualizar_status_servidor("Conectado. Digite seu nickname.")

                        ## FUNÇÕES DE DRAFT
                    ## TIMES DA TEMPORADA
                    elif tipo == "DRAFT_LISTA":
                        self.exibir_draft(pacote.get('jogadores_disponiveis'))
                        self.atualizar_status_servidor("Lista de atletas atualizada.")

                    ## ATUALIZAÇÃO DE TURNOS
                    elif tipo == "TURNO_INFO":
                        jogador_da_vez = pacote.get("jogador_da_vez")
                        
                        # Compara se o jogador da vez anunciado pelo servidor é este cliente
                        if jogador_da_vez == self.meu_id:
                            self.e_minha_vez = True
                            self.atualizar_status_servidor("Sua vez no draft.")
                        else:
                            self.e_minha_vez = False
                            self.atualizar_status_servidor(f"Turno de {jogador_da_vez}.")

                    elif tipo == "DRAFT_SUCESSO":
                        self.atualizar_status_servidor(f"{pacote.get('quem_escolheu')} escolheu {pacote.get('jogador_escolhido')}.")

                    elif tipo == "FIM_DRAFT":
                        self.exibir_resultados(pacote.get('lista'))
                        self.atualizar_status_servidor("Draft encerrado.")

                    elif tipo == "INICIO_SEASON":
                        self.atualizar_status_servidor("Temporada iniciando.")
                        time.sleep(1)
                        time.sleep(1)
                        time.sleep(1)
                        time.sleep(1)

                    elif tipo == "FINAL_RODADA":
                        self.atualizar_status_servidor(f"Rodada {pacote.get('rodada')} finalizada.")


                    elif tipo == "RESULTADO_FINAL":
                        self.atualizar_status_servidor("Resultados finais disponíveis.")

                        lista_podio = list(pacote.get('lista').items())
                        total_jogadores = len(lista_podio)

                        for  i, (chave, resultado) in enumerate(reversed(lista_podio)):
                            time.sleep(1)
                            time.sleep(2)


                    ## MENSAGENS DO CHAT
                    elif tipo == "CHAT_BROADCAST":
                        self.historico_chat.append(f"MENSAGEM {pacote.get('remetente')}: {pacote.get('mensagem')}")
                        if len(self.historico_chat) > 18:
                            self.historico_chat = self.historico_chat[-18:]
                        self.tela.atualizar_chat(self.historico_chat)
                        self.atualizar_status_servidor(f"Chat: {pacote.get('remetente')}")
                    
                    # Feedback se uma escolha deu erro (ex: jogador indisponível)
                    elif tipo == "ERRO":
                        self.atualizar_status_servidor(f"Erro: {pacote.get('msg')}")

        except Exception as e:
            self.atualizar_status_servidor(f"Erro na conexão: {e}")
        finally:
            import os
            os._exit(0)

                
        sys.exit(0)

    def iniciar_cliente(self):
        try:
            self.cliente_socket.connect((self.host, self.port))
            print("=== BEM-VINDO AO FANTASY NBA ===")
            
            # Como a função ouvir_servidor agora faz parte da classe, chamamos com self
            thread_escuta = threading.Thread(target=self.ouvir_servidor)
            thread_escuta.daemon = True 
            thread_escuta.start()

            self.tela.atualizar_servidor("Conectando ao servidor...")
            with Live(self.tela.layout_principal, console=console_grafico, refresh_per_second=10, screen=False):
                while True:
                    mensagem_texto = input("CLIENTE: ").strip()

                    if mensagem_texto.lower() == 'sair':
                        break

                    if not mensagem_texto:
                        continue

                    # definição do apelido
                    if not self.nick_confirmado:
                        pacote_envio = {
                            "tipo": "REGISTRAR_NICK",
                            "nick": mensagem_texto
                        }
                        self.cliente_socket.sendall((json.dumps(pacote_envio) + '\n').encode('utf-8'))
                        self.nick_confirmado = True
                        self.meu_id = mensagem_texto
                        self.atualizar_status_servidor(f"Nickname definido: {mensagem_texto}")

                    # Se for a vez dele, constrói o pacote de escolha
                    elif self.e_minha_vez:
                        pacote_envio = {
                            "tipo": "DRAFT_ESCOLHA",
                            "jogador": mensagem_texto
                        }
                        self.cliente_socket.sendall((json.dumps(pacote_envio) + '\n').encode('utf-8'))
                        self.e_minha_vez = False
                        self.atualizar_status_servidor("Escolha enviada ao draft.")
                    
                    # Se o cliente tentar digitar algo mas NÃO for a vez dele
                    else:
                        pacote_envio = {
                            "tipo": "CHAT",
                            "mensagem": mensagem_texto
                        }
                        self.cliente_socket.sendall((json.dumps(pacote_envio) + '\n').encode('utf-8'))
                        self.atualizar_status_servidor(f"Mensagem enviada: {mensagem_texto}")

                    ## FIM DO DRAFT

                

        except ConnectionRefusedError:
            print("[ERRO] Não foi possível ligar ao servidor.")
        finally:
            #print("\nDesconectado do Fantasy NBA.")
            import os
            os._exit(0)

if __name__ == "__main__":
    # Constantes definidas na inicialização
    HOST = '127.0.0.1' 
    PORT = 6789
    
    # Instanciamos o objeto do cliente e iniciamos a conexão
    cliente_ativo = ClienteFantasy(HOST, PORT)
    cliente_ativo.iniciar_cliente()