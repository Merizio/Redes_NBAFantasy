import socket
import json
import threading
import time

# Configurações do seu servidor
HOST = '127.0.0.1' 
PORT = 6789

# Quantos bots vão tentar invadir o servidor ao mesmo tempo?
NUMERO_DE_BOTS = 50

def comportamento_do_bot(bot_id):
    """O bot conecta e dispara rajadas de mensagens no chat"""
    try:
        bot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bot_socket.connect((HOST, PORT))
        
        dados = bot_socket.recv(1024)
        if "SOLICITAR_NICK" in dados.decode('utf-8'):
            
            # 1. Registra o Nick
            pacote_nick = {
                "tipo": "REGISTRAR_NICK",
                "nick": f"Bot_{bot_id}"
            }
            bot_socket.sendall((json.dumps(pacote_nick) + '\n').encode('utf-8'))
            
            # Pequena pausa para garantir que o servidor registrou todos
            time.sleep(1) 
            
            # 2. O ATAQUE: Manda 50 mensagens por bot sem intervalo
            for i in range(50):
                pacote_spam = {
                    "tipo": "CHAT",
                    "mensagem": f"Esta é a mensagem de teste número {i} do Bot {bot_id}!"
                }
                # A ausência de time.sleep aqui força os pacotes a se grudarem na rede (TCP coalescing)
                bot_socket.sendall((json.dumps(pacote_spam) + '\n').encode('utf-8'))
            
            # Dá tempo do servidor processar tudo antes de fechar a porta
            time.sleep(5) 
            
        bot_socket.close()
        print(f"[+] Bot_{bot_id} terminou o ataque.")
        
    except Exception as e:
        print(f"[-] Bot_{bot_id} falhou: {e}")


print(f"🔥 Iniciando ataque de estresse com {NUMERO_DE_BOTS} bots...")

# Cria um exército de threads (uma para cada bot)
threads_bots = []
for i in range(NUMERO_DE_BOTS):
    t = threading.Thread(target=comportamento_do_bot, args=(i,))
    threads_bots.append(t)

# Inicia TODAS elas de uma vez (aqui acontece o pico de estresse!)
tempo_inicio = time.time()
for t in threads_bots:
    t.start()

# Espera todas terminarem
for t in threads_bots:
    t.join()

tempo_fim = time.time()
print(f"\n✅ Teste finalizado em {tempo_fim - tempo_inicio:.2f} segundos.")