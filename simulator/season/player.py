import team

class Player:
    def __init__(self, id):
        self.id = id
        self.draft = list()
        self.points = 0

    def add_jogador(self, Jogador):
        if Jogador.drafted == False:
            Jogador.drafted == True
            self.draft.append(Jogador.copy())
            print(Jogador.Player , 'adicionado ao draft do Player ', self.id)
        else:
            print('Jogador já Draftado')

    def exibir_draft(self):
        print('JOGADOS:', self.id)
        print('PONTUAÇÃO:', self.points)
        print('JOGADORES:')
        for n in self.draft:
            n.exibir_jogador()
        