# interface.py
from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console
from rich.text import Text

console = Console(force_terminal=True, force_interactive=True)

class TelaDoJogo:
    def __init__(self):
        # 1. Cria os blocos isolados
        self.bloco_draft = Layout(Panel("Aguardando lista...", title="Draft", border_style="red"))
        self.bloco_servidor = Layout(Panel("Conectando...", title="Servidor", border_style="cyan"))
        self.bloco_chat = Layout(Panel("Sem mensagens.", title="Msgs", border_style="yellow"))

        # 2. Monta a tela final juntando tudo
        self.coluna_direita = Layout()
        self.coluna_direita.split_column(self.bloco_servidor, self.bloco_chat)
        
        self.layout_principal = Layout()
        self.layout_principal.split_row(self.bloco_draft, self.coluna_direita)

    # 3. Métodos fáceis para o seu cliente chamar e atualizar a tela
    def atualizar_servidor(self, texto):
        self.bloco_servidor.update(Panel(texto, title="Servidor", border_style="cyan"))

    def atualizar_chat(self, historico_lista):
        # Mostra as mensagens mais recentes com quebra automática de linha
        texto_chat = Text("\n".join(historico_lista[-18:]), no_wrap=False)
        self.bloco_chat.update(Panel(texto_chat, title="Msgs", border_style="yellow"))

    def atualizar_draft(self, texto):
        self.bloco_draft.update(Panel(texto, title="Draft", border_style="red"))