from aigyminsper.search.search_algorithms import Aestrela
from aigyminsper.search.graph import State
import random

class Entregador(State):

    def __init__(self, mapa, agente, pacote, destino, obstaculo, pedagio, op="", carregando=False, custo_acao=0):
        
        super().__init__(op)
        self.mapa = mapa
        self.agente = agente
        self.pacote = pacote
        self.destino = destino
        self.obstaculo = obstaculo
        self.pedagio = pedagio
        self.carregando = carregando
        self.custo_acao = custo_acao
        
    
    def successors(self):
        successors = []

        tamanho_x = len(self.mapa)
        tamanho_y = len(self.mapa[0])

        linha, coluna = self.agente
        custo = 1

        #No grid, o pedágio é marcado como 3
        if self.mapa[linha][coluna] == 3:
            custo = custo + 2

        # Movimento para cima.
        if (
            linha - 1 >= 0
            and self.mapa[linha - 1][coluna] != 0
        ):
            nova_posicao = (linha - 1, coluna)

            successors.append(
                Entregador(
                    mapa=self.mapa,
                    agente=nova_posicao,
                    pacote=self.pacote,
                    destino=self.destino,
                    obstaculo=self.obstaculo,
                    pedagio=self.pedagio,
                    op="cima",
                    carregando=self.carregando,
                    custo_acao=custo
                )
            )

        # Movimento para baixo.
        if (linha + 1 < tamanho_x and self.mapa[linha + 1][coluna] != 0):
            
            nova_posicao = (linha + 1, coluna)

            successors.append(
                Entregador(
                    mapa=self.mapa,
                    agente=nova_posicao,
                    pacote=self.pacote,
                    destino=self.destino,
                    obstaculo=self.obstaculo,
                    pedagio=self.pedagio,
                    op="baixo",
                    carregando=self.carregando,
                    custo_acao=custo
                )
            )

        #movimenta para a direita
        if (coluna + 1 < tamanho_y and self.mapa[linha][coluna + 1] != 0):
            
            nova_posicao = (linha, coluna + 1)

            successors.append(
                Entregador(
                    mapa=self.mapa,
                    agente=nova_posicao,
                    pacote=self.pacote,
                    destino=self.destino,
                    obstaculo=self.obstaculo,
                    pedagio=self.pedagio,
                    op="direita",
                    carregando=self.carregando,
                    custo_acao=custo
                )
            )

        #movimenta para a esquerda
        if (coluna - 1 >= 0 and self.mapa[linha][coluna - 1] != 0):
           
            nova_posicao = (linha, coluna - 1)

            successors.append(
                Entregador(
                    mapa=self.mapa,
                    agente=nova_posicao,
                    pacote=self.pacote,
                    destino=self.destino,
                    obstaculo=self.obstaculo,
                    pedagio=self.pedagio,
                    op="esquerda",
                    carregando=self.carregando,
                    custo_acao=custo
                )
            )
        
        # Pegar o pacote: o agente precisa estar na mesma célula.
        if not self.carregando and self.agente == self.pacote:
            successors.append(
                Entregador(
                    mapa=self.mapa,
                    agente=self.agente,
                    pacote=None,
                    destino=self.destino,
                    obstaculo=self.obstaculo,
                    pedagio=self.pedagio,
                    op="pegar pacote",
                    carregando=True,
                    custo_acao=custo
                )
            )

        # Entregar: deixa o pacote na célula atual.
        if self.carregando:
            successors.append(
                Entregador(
                    mapa=self.mapa,
                    agente=self.agente,
                    pacote=self.agente,
                    destino=self.destino,
                    obstaculo=self.obstaculo,
                    pedagio=self.pedagio,
                    op="entregar pacote",
                    carregando=False,
                    custo_acao=custo
                )
            )

        return successors
    
    def is_goal(self):
        if self.pacote == self.destino and not self.carregando:
            return True
        return False
        
    def description(self):
        return "Resolução do problema de entregar o pacote"
    
    def cost(self):
        return self.custo_acao
    
    def env(self):
        return str((
            self.agente,
            self.pacote,
            self.carregando
        ))

def main():

    # Dimensão aleatória para um mapa quadrado.
   # n = random.randint(3, 50)
    n = input("Digite o tamanho do grid")
    print(f"Busca em largura — mapa {n}x{n}")

    """
    0 = obstáculo
    1 = agente
    2 = célula livre
    3 = pedágio
    """
    mapa = [[2] * n for _ in range(n)]

    # Todas as posições possíveis, no formato (linha, coluna).
    posicoes = [
        (linha, coluna)
        for linha in range(n)
        for coluna in range(n)
    ]

    # Embaralha as posições para realizar os sorteios.
    random.shuffle(posicoes)

    # pop() remove a posição escolhida, evitando sobreposições.
    agente = posicoes.pop()
    pacote = posicoes.pop()
    destino = posicoes.pop()

    # Sorteia a quantidade de obstáculos: de 0 até 25% do mapa.
    quantidade_obstaculos = random.randint(0, (n * n) // 4)
    obstaculo = set()


    for _ in range(quantidade_obstaculos):
        posicao = posicoes.pop()
        obstaculo.add(posicao)

        linha, coluna = posicao
        mapa[linha][coluna] = 0

    # Sorteia a quantidade de pedágios: de 0 até 20% do mapa.
    quantidade_pedagios = random.randint(
        1,
        min(len(posicoes), (n * n) // 5)
    )

    pedagio = set()

    for _ in range(quantidade_pedagios):
        posicao = posicoes.pop()
        pedagio.add(posicao)

        linha, coluna = posicao
        mapa[linha][coluna] = 3

    # Copia cada linha para não modificar o mapa original.
    mapa_visual = [linha.copy() for linha in mapa]

    linha, coluna = agente
    mapa_visual[linha][coluna] = 1

    linha, coluna = pacote
    mapa_visual[linha][coluna] = 4

    linha, coluna = destino
    mapa_visual[linha][coluna] = 5

    print("Mapa visual:")
    for linha in mapa_visual:
        print(linha)

    # print("Mapa:")
    # for linha in mapa:
    #     print(linha)


    print(f"Agente: {agente}")
    print(f"Pacote: {pacote}")
    print(f"Destino: {destino}")
    print(f"Obstáculos: {obstaculo}")
    print(f"Pedágios: {pedagio}")

    state = Entregador(
        mapa=mapa,
        agente=agente,
        pacote=pacote,
        destino=destino,
        obstaculo=obstaculo,
        pedagio=pedagio,
        op="início"
    )

    algorithm = AEstrela()

    result = algorithm.search(
        state,
        trace=False,
        pruning="general"
    )

    if result is not None:
        print("Achou!")
        print(result.show_path())
        print(f"Custo da solução: {result.g}")
    else:
        print("Não achou solução")

if __name__ == '__main__':
    main()
