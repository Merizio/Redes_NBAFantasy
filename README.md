# Redes_NBAFantasy
Francisco Vassoler Merizio
2024102652

## O PROJETO
Trabalho dedicado para a disciplina de Redes de Computadores, um fantasy para uma temporada da NBA.

Os jogadores fazem um Draft dos atletas disponíveis (seleções alternadas), e de acordo com as performances durante a temporada os times vão ganhando pontos.
Ganha o time que tiver mais pontos entre os seus atletas draftados

### TECNOLOGIAS E ARQUITETURA
- Implementação de um sistema padrão cliente/servidor, com conexão via TCP.
- Linguagem escolhida Python, por comodidade em relação a manipulação de csv e utilização das bibliotecas nativas
- Utilização das bibliotecas Threads e Sockets, além das dependências Pandas, Numpy
- Transferência de dados sempre em formato Json

## COMO EXECUTAR
Para execução do sistema, depois do Git clonado corretamente, é necessária a utilização de algumas dependências específicas para o Python, para isso usaremos o ambiente virtual Conda:

### Para Criar o Ambiente Virtual:
```bash
conda env create -f fantasy.yml
```
Com o ambiente virtual, iniciaremos o nosso servidor e os nossos clientes: (lembrar de configurar o IP do host)
### Iniciar o servidor:
```bash
python servidor/servidor.py
```
### Iniciar os clientes:
```bash
python cliente/cliente.py
```

## TESTES
Para execuções mais simples, é possível alterar o Número de Times (Max de 30), número de atletas por time (base 5) e a quantidade de jogadores (base 3)

**Com o servidor rodando, é só conectar os clientes, escolher o seu nome de usuário na partida, draftar os seus jogadores favoritos e torcer!**

### DESEMPENHO
Em um teste de overload de clientes, o sistema conseguiu aceitar corretamente todos os clientes em um teste com 250 bots entrando ao mesmo tempo, em 10.10 segundos

Em um outro teste, 50 bots enviando 50 mensagens cada em um fluxo acelerado, simultâneamente, também não teve nenhum problema de recebimento e performance 


## FUNCIONALIDADES IMPLEMENTADAS
1. A funcionalidade base é o simulador, os dados usados são da última temporada regular da NBA, e todo o sistema é feito para tentar uma reprodução completamente aleatória dos eventos de uma partida em tempo real. Isso pode ser visto melhor no *seasoon/simulator.py*
2. A partir da Definição da quantidade de times, são escolhidos aleatoriamente da base de dados, um algoritmo define as rodadas em um sistema TODOS CONTRA TODOS, em que todos os times se enfrentam 1x. Os jogos da rodada são simulatos em paralelo, por um sistema de threads, e os resultados são computados para os atletas, e, respectivamente, para os times do draft.


## MELHORIAS PARA O FUTURO PRÓXIMO
- melhorar a visibilidade das coisas - OK
- trazer a ideia de jogo em tempo real, com o resultado da rodada - OK
- o servidor controlar quando inicia cada ação pelo terminal - OK
- os players definirem o nome deles - OK
- atribuição de custo dos jogadores por rank
- possibilidade de jogar com menos que o máximo de jogadores ou clientes
- divisão tela, chat e servidor
- impressão dos jogadores restantes do draft apenas
- melhorar a forma de inicialização
- escolha de quantidades de times/clientes/jogadores ser interativa

## COISAS PARA UM FUTURO UM POUCO MAIS DISTANTE
- interface real
- jogadores com imagem
