import socket
import threading
import json
import sys

# Configurações de Conexão
HOST = '127.0.0.1' # Localhost
PORT = 8080

def ouvir_servidor(cliente_socket):
    """
    Recebe mensagens do servidor
    """
    buffer = ""
    while True:
        try:
            dados = cliente_socket.recv(4096)
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
                print(f"\n[MENSAGEM DO SERVIDOR]: {pacote}")

        except Exception as e:
            print(f"\n[ERRO NA ESCUTA] A conexão foi perdida: {e}")
            break
            
    # Se o loop quebrar, fechamos o programa
    sys.exit(0)

def iniciar_cliente():
    """
    Envia Mensagens para o servidor
    """
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        cliente_socket.connect((HOST, PORT))
        print("=== BEM-VINDO AO FANTASY NBA ===")
        print("Escreve a tua mensagem ou comando e prime ENTER (ou 'sair' para fechar).\n")
        

        # Criamos a Thread de Escuta
        thread_escuta = threading.Thread(target=ouvir_servidor, args=(cliente_socket,))
        thread_escuta.daemon = True 
        thread_escuta.start()
        
        # --- LOOP DO TECLADO (Thread Principal) ---
        while True:
            # O programa fica parado aqui à espera que escrevas
            mensagem_texto = input()
            
            if mensagem_texto.lower() == 'sair':
                break
                
            # Constrói o pacote JSON para enviar ao servidor
            # Vamos assumir que tudo o que digitas agora é chat, só para testar
            pacote_envio = {
                "tipo": "CHAT",
                "conteudo": mensagem_texto
            }
            
            # Converte para string JSON, adiciona a quebra de linha e envia
            cliente_socket.sendall((json.dumps(pacote_envio) + '\n').encode('utf-8'))
            
    except ConnectionRefusedError:
        print("[ERRO] Não foi possível ligar ao servidor. Verifica se ele está a correr.")
    finally:
        cliente_socket.close()
        print("Desconectado do Fantasy NBA.")

if __name__ == "__main__":
    iniciar_cliente()