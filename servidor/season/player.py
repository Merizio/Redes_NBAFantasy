from season import team
import numpy as np

class Player:
    def __init__(self, id, nick, conexao):
        self.id = id
        self.nick = nick
        self.conexao = conexao
        self.draft = list()
        self.points = 0
        self.pointlist = np.zeros(shape=5)

    def add_jogador(self, Jogador):
        if Jogador.drafted == False:
            Jogador.drafted = True
            self.draft.append(Jogador)
            print(Jogador.Player , 'adicionado ao draft do Player ', self.id)
            return True
        else:
            print('Jogador já Draftado')
            return False

    def exibir_draft(self):
        print('PLAYER:', self.id)
        print('PONTUAÇÃO:', self.points)
        print('JOGADORES:')
        for i, n in enumerate(self.draft):
            print(f"{n.Player:>25} | {n.Pos:<2} | {self.pointlist[i]:.2f}")
        
    def atribuir_points(self, Jogador):
        index = next(
            (i for i, jogador_draft in enumerate(self.draft) if jogador_draft.Player == Jogador.Player),
            None,
        )
            
        pontos_jogo = Jogador.pts

        ##VARIAVEIS DE INCREMENTO
        if Jogador.win:
            pontos_jogo *= 1.2
        pontos_jogo -= 2 * Jogador.fouls

        self.pointlist[index] += pontos_jogo
        self.points = float(self.pointlist.sum())
        return True
    
def gerar_resultados(players, num_jogadores, num_rodadas):
    print('RESULTADOS:')
    resultado = list()
    for i in range(num_jogadores):
        resultado.append(players[i])

    resultado.sort(key=lambda Player: Player.points, reverse=True)
    for i in range(num_jogadores):
        print(f"{i+1}º Lugar!\n{resultado[i].id} = {(resultado[i].points/num_rodadas):.1f} pontos")