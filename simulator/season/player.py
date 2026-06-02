import team
import numpy as np

class Player:
    def __init__(self, id):
        self.id = id
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
        print('JOGADOS:', self.id)
        print('PONTUAÇÃO:', self.points)
        print('JOGADORES:')
        for i, n in enumerate(self.draft):
            print(f"{n.Player:>25} | {n.Pos:<2} | {self.pointlist[i]}")
        
    def atribuir_points(self, Jogador):
        index = next(
            (i for i, jogador_draft in enumerate(self.draft) if jogador_draft.Player == Jogador.Player),
            None,
        )

        pontos_jogo = Jogador.pts
        self.pointlist[index] += pontos_jogo
        self.points = float(self.pointlist.sum())
        return True
