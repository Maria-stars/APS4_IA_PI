# APS 1 — Inteligência Artificial e Robótica

Este projeto compara o desempenho de três algoritmos de busca aplicados ao problema do aspirador de pó em mapas quadrados de diferentes dimensões.

Os algoritmos avaliados são:
- Busca em largura (BFS — Breadth-First Search);
- Busca em profundidade (DFS — Depth-First Search);
- Busca em profundidade iterativa (IDDFS — Iterative Deepening Depth-First Search).


## Descrição do problema

O ambiente é representado por uma matriz quadrada de dimensão n × n, em que:
- n varia de 2 até 30;
- 50% das células do mapa começam sujas;
- as células sujas são escolhidas aleatoriamente;
- o robô sempre começa na posição (0, 0);
- o robô pode se movimentar para células vizinhas válidas;
- quando está em uma célula suja, o robô pode executar a ação de limpar.
- Uma execução termina quando o estado-meta é alcançado.

## Estado-meta
O problema é considerado resolvido somente quando as duas condições abaixo forem satisfeitas:

- todas as células do mapa estiverem limpas;
- o robô tiver retornado à posição inicial (0, 0).

Em forma lógica:
```
meta = todas_as_celulas_limpas AND posicao_robo == (0, 0)
```
## Geração dos mapas
Deve ser criada uma função que receba a dimensão n e produza um mapa n × n com 50% das células sujas.

Como mapas com uma quantidade ímpar de células não permitem uma divisão exata de 50%, será adotada a seguinte regra:
```
quantidade_de_celulas_sujas = floor((n × n) / 2)
```
Assim, um mapa 3 × 3, por exemplo, terá 4 das suas 9 células inicialmente sujas.

## Representação de um estado
Cada estado da busca deve armazenar, no mínimo:

- a posição atual do robô;
- quais células ainda estão sujas;
- o caminho ou a referência necessária para reconstruir a solução;
- a profundidade do estado na árvore de busca.


## Ações possíveis
Dependendo da posição e da situação atual, o robô pode:
- mover-se para cima;
- mover-se para baixo;
- mover-se para a esquerda;
- mover-se para a direita;
- limpar a célula atual, caso ela esteja suja.

## Limite de profundidade

Será usado o seguinte limite máximo conservador para um mapa de dimensão n:
```
limite_maximo = floor(n² / 2) + (n² - 1) + 2(n - 1)
```
Esse valor considera uma estratégia válida que:
- limpa todas as floor(n² / 2) células inicialmente sujas;
- percorre todas as células do mapa em até n² - 1 movimentos;
- retorna ao ponto (0, 0) em até 2(n - 1) movimentos.


## Coleta das métricas
Para cada dimensão e algoritmo, devem ser coletadas as seguintes informações:
- tempo de execução total;
- memória usada para a execução total;
- tamanho do mapa;
- indicação de sucesso, falha ou interrupção por limite de recursos.

O tempo deve ser medido antes e depois da execução do método de busca:
``` tempo_inicial = relógio_de_alta_resolução()
resultado = search(estado_inicial)
tempo_final = relógio_de_alta_resolução()

tempo_gasto = tempo_final - tempo_inicial 
```
A memória deve seguir a medição solicitada:
```
memoria_inicial = memoria_atual()
resultado = search(estado_inicial)
memoria_final = memoria_atual()

memoria_gasta = memoria_final - memoria_inicial
```