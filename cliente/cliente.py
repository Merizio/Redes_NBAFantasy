import socket
import threading
import json
import sys

# --- CLASSE PRINCIPAL DO CLIENTE ---
class ClienteFantasy:
    def __init__(self, host, port):
        # Configurações de conexão
        self.host = host
        self.port = port
        
        # Estado Local do Cliente
        self.meu_id = None          # Será preenchido quando o servidor nos disser quem somos
        self.e_minha_vez = False    # Controla se o teclado está liberado para o Draft
        self.cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def exibir_draft(self, times):
        retorno = json.loads(times)

        for chave_time, time_info in retorno["dados"].items():
            print(f"\n--- {time_info['nome']} ---")
            print("Elenco:")
            for jogador in time_info["elenco"]:
                # Se a vaga estiver vazia (None no Python, null no JSON), exibe Vaga Livre
                print(f"  {jogador if jogador is not None else '[Vaga Livre]'}")

    def exibir_resultados(self, lista):
        #lista = json.loads(drafts)

        for  chave, jogadores in lista.items():
            print(f"---{chave}---")
            for jogador in jogadores:
                print(jogador)


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
                        print(f"SERVIDOR: {pacote.get('dados')}")
                        # Se o servidor enviou o ID atribuído a este cliente
                        if "Você é o" in pacote.get('dados'):
                            # Extrai o ID do texto (Ex: "Player_1")
                            self.meu_id = pacote.get('dados').split("Você é o ")[1].replace(".", "").strip()



                        ## FUNÇÕES DE DRAFT
                    ## TIMES DA TEMPORADA
                    elif tipo == "DRAFT_LISTA":
                        self.exibir_draft(pacote.get('jogadores_disponiveis'))

                    ## ATUALIZAÇÃO DE TURNOS
                    elif tipo == "TURNO_INFO":
                        jogador_da_vez = pacote.get("jogador_da_vez")
                        
                        # Compara se o jogador da vez anunciado pelo servidor é este cliente
                        if jogador_da_vez == self.meu_id:
                            self.e_minha_vez = True
                            print("\n🚨 É A SUA VEZ! Digite o nome do jogador para draftar: ")
                        else:
                            self.e_minha_vez = False
                            print(f"\n⌛ Aguardando o turno de {jogador_da_vez}...")

                    elif tipo == "DRAFT_SUCESSO":
                        print(f"O {pacote.get('quem_escolheu')} escolheu o {pacote.get('jogador_escolhido')}")

                    elif tipo == "FIM_DRAFT":
                        print(f"Fim do Draft!\n")
                        self.exibir_resultados(pacote.get('lista'))


                    elif tipo == "RESULTADO_FINAL":
                        for  chave, resultado in pacote.get('lista').items():
                            print(f"---{chave}º Lugar---")
                            print(resultado)



                    ## MENSAGENS DO CHAT
                    elif tipo == "CHAT_BROADCAST":
                        print(f"MENSAGEM {pacote.get('remetente')}: {pacote.get('mensagem')}")
                    
                    # Feedback se uma escolha deu erro (ex: jogador indisponível)
                    elif tipo == "ERRO":
                        print(f"\n[X] ERRO: {pacote.get('msg')}")

        except Exception as e:
            print(f"\n[ERRO NA ESCUTA] A conexão foi perdida: {e}")
        finally:
            print("\nDesconectado do Fantasy NBA.")
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
            
            # --- LOOP DO TECLADO (Thread Principal) ---
            while True:
                mensagem_texto = input().strip()
                
                if mensagem_texto.lower() == 'sair':
                    break
                    
                if not mensagem_texto:
                    continue

                #if self.rodadas>0:
                    # Se for a vez dele, constrói o pacote de escolha
                if self.e_minha_vez:
                    pacote_envio = {
                        "tipo": "DRAFT_ESCOLHA",
                        "jogador": mensagem_texto
                    }
                    self.cliente_socket.sendall((json.dumps(pacote_envio) + '\n').encode('utf-8'))
                    
                    # Reseta temporariamente a flag local até que o servidor valide e mude o turno
                    self.e_minha_vez = False
                
                # Se o cliente tentar digitar algo mas NÃO for a vez dele
                else:
                    pacote_envio = {
                        "tipo": "CHAT",
                        "mensagem": mensagem_texto
                    }
                    self.cliente_socket.sendall((json.dumps(pacote_envio) + '\n').encode('utf-8'))

                ## FIM DO DRAFT

                

        except ConnectionRefusedError:
            print("[ERRO] Não foi possível ligar ao servidor.")
        finally:
            print("\nDesconectado do Fantasy NBA.")
            import os
            os._exit(0)

if __name__ == "__main__":
    # Constantes definidas na inicialização
    HOST = '127.0.0.1' 
    PORT = 6789
    
    # Instanciamos o objeto do cliente e iniciamos a conexão
    cliente_ativo = ClienteFantasy(HOST, PORT)
    cliente_ativo.iniciar_cliente()