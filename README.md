# Redes_NBAFantasy
Francisco Vassoler Merizio
2024102652

## Resumo
Trabalho dedicado para a disciplina de Redes de Computadores, um fantasy para uma temporada da NBA.

Os jogadores fazem um Draft dos atletas disponíveis, e de acordo com as performances durante a temporada os times vão ganhando pontos,
ganha o time que tiver mais pontos entre os seus atletas draftados

## COMO EXECUTAR
Para Criar o Ambiente Virtual:
```bash
conda env create -f fantasy.yml
```
Iniciar o servidor:
```bash
python servidor/servidor.py
```
Iniciar os clientes:
```bash
python cliente/cliente.py
```



## COISAS QUE EU TENHO QUE FAZER:
- melhorar a visibilidade das coisas - OK
- trazer a ideia de jogo em tempo real, com o resultado da rodada - OK
- o servidor controlar quando inicia cada ação pelo terminal - OK
- os players definirem o nome deles - OK
- atribuição de custo dos jogadores por rank
- possibilidade de jogar com menos que o máximo de jogadores ou clientes
- divisão tela, chat e servidor
- impressão dos jogadores restantes do draft apenas
- melhorar a forma de inicialização

## COISAS PARA UM FUTURO PRÓXIMO
- interface real
- jogadores com imagem