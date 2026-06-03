import socket
import json
import threading

# Configurações do Servidor
HOST = 'localhost' # IP local para testes
PORT = 8080        # Porta de comunicação

# Simulando o seu banco de dados de jogadores (que virá do Pandas depois)
jogadores_disponiveis = [
    {"id": 1, "nome": "Luka Doncic", "posicao": "PG"},
    {"id": 2, "nome": "Nikola Jokic", "posicao": "C"},
    {"id": 3, "nome": "Stephen Curry", "posicao": "PG"}
]

def lidar_com_cliente(conexao_cliente, endereco_cliente):
    print(f"[NOVA CONEXÃO] Cliente conectado: {endereco_cliente}")
    
    try:
        # 1. Envia a lista inicial do Draft (como fazíamos antes)
        mensagem_inicial = {
            "tipo": "DRAFT_LISTA",
            "dados": jogadores_disponiveis
        }
        conexao_cliente.sendall((json.dumps(mensagem_inicial) + '\n').encode('utf-8'))
        print(f"[ENVIADO] Lista de jogadores enviada para {endereco_cliente}")

        # --- O PULO DO GATO: LOOP PERSISTENTE DA CONEXÃO ---
        buffer = ""
        while True:
            # O servidor fica travado aqui esperando este cliente específico mandar alguma coisa
            dados = conexao_cliente.recv(4096)

            # Se o cliente fechar o terminal dele, o recv retorna bytes vazios
            if not dados:
                print(f"[DESCONECTADO] Cliente {endereco_cliente} desconectou de forma limpa.")
                break

            # Acumula no buffer e processa mensagens delimitadas por '\n'
            buffer += dados.decode('utf-8')
            while '\n' in buffer:
                linha, buffer = buffer.split('\n', 1)
                if not linha.strip():
                    continue
                try:
                    pacote = json.loads(linha)
                except json.JSONDecodeError as e:
                    print(f"[ERRO JSON] Falha ao decodificar mensagem de {endereco_cliente}: {e}")
                    continue

                print(f"[RECEBIDO de {endereco_cliente}]: {pacote}")

                # Trata a mensagem baseada no tipo que combinamos
                if pacote.get("tipo") == "CHAT":
                    print(f"Mensagem de chat enviada: {pacote.get('conteudo')}")
                    # No futuro, aqui faremos um loop para enviar a todos (Broadcast)
                    # Por enquanto, apenas confirmamos para o próprio cliente:
                    confirmacao = {"tipo": "INFO", "conteudo": "Mensagem recebida pelo servidor!"}
                    conexao_cliente.sendall((json.dumps(confirmacao) + '\n').encode('utf-8'))

                elif pacote.get("tipo") == "DRAFT_ESCOLHA":
                    # Lógica futura: validar se jogador está livre, travar mutex, mudar turno...
                    pass

    except Exception as e:
        print(f"[ERRO] Falha na comunicação com {endereco_cliente}: {e}")
    finally:
        # Só fecha o socket quando o loop 'while True' quebrar (porque o cliente saiu)
        conexao_cliente.close()
        print(f"[FECHADO] Conexão com {endereco_cliente} encerrada com segurança.")

def iniciar_servidor():
    # Cria o socket TCP (AF_INET = IPv4, SOCK_STREAM = TCP)
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Permite reusar a porta imediatamente caso o servidor caia
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    servidor.bind((HOST, PORT))
    servidor.listen()
    print(f"[SERVIDOR INICIADO] Ouvindo na porta {PORT}...")

    while True:
        # Fica travado aqui esperando alguém conectar
        conexao, endereco = servidor.accept()
        
        # Cria uma nova Thread para cada cliente que chega
        thread_cliente = threading.Thread(target=lidar_com_cliente, args=(conexao, endereco))
        thread_cliente.start()
        print(f"[THREADS ATIVAS] {threading.active_count() - 1}")

if __name__ == "__main__":
    iniciar_servidor()