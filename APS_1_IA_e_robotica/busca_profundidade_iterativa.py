from aigyminsper.search.graph import State
from aigyminsper.search.search_algorithms import BuscaProfundidade
import csv
import json
import random
import sys
import time
import tracemalloc


INICIO = (0, 0)
MOVIMENTOS = [
    ("cima", (-1, 0)),
    ("baixo", (1, 0)),
    ("esquerda", (0, -1)),
    ("direita", (0, 1)),
]
DIMENSAO_INICIAL = 2
DIMENSAO_FINAL = 30
TEMPO_MAXIMO_SEGUNDOS = 30.0
SEED = 42
ARQUIVO_CSV = "busca_profundidade_iterativa.csv"


class InterrupcaoBusca(Exception):

    def __init__(self, motivo):
        super().__init__(motivo)
        self.motivo = motivo


class AgentSpecification(State):
    tempo_inicial = 0
    tempo_maximo = TEMPO_MAXIMO_SEGUNDOS
    limite_atual = 0

    def __init__(self, op, n, posicao, sujas, profundidade=0):
        super().__init__(op)
        self.n = n
        self.posicao = posicao
        self.sujas = tuple(sorted(sujas))
        self.profundidade = profundidade

    def successors(self):
        if self.tempo_estourado():
            raise InterrupcaoBusca("tempo")

        if self.profundidade + limite_inferior(self) > AgentSpecification.limite_atual:
            return []

        alvo = self.alvo_mais_proximo()
        proximos_movimentos = self.movimentos_validos()
        proximos_movimentos.sort(
            key=lambda movimento: distancia_manhattan(movimento[1], alvo),
            reverse=True,
        )

        successors = [
            self.novo_estado("ir " + nome, nova_posicao)
            for nome, nova_posicao in proximos_movimentos
        ]

        if self.posicao in self.sujas:
            successors.append(
                self.novo_estado("limpar", sujas=set(self.sujas) - {self.posicao})
            )

        return successors

    def tempo_estourado(self):
        return (
            time.perf_counter() - AgentSpecification.tempo_inicial
            > AgentSpecification.tempo_maximo
        )

    def movimentos_validos(self):
        linha, coluna = self.posicao
        return [
            (nome, (linha + d_linha, coluna + d_coluna))
            for nome, (d_linha, d_coluna) in MOVIMENTOS
            if 0 <= linha + d_linha < self.n and 0 <= coluna + d_coluna < self.n
        ]

    def novo_estado(self, op, posicao=None, sujas=None):
        return AgentSpecification(
            op,
            self.n,
            self.posicao if posicao is None else posicao,
            self.sujas if sujas is None else sujas,
            self.profundidade + 1,
        )

    def alvo_mais_proximo(self):
        if not self.sujas:
            return INICIO

        return min(
            self.sujas,
            key=lambda suja: distancia_manhattan(self.posicao, suja),
        )

    def is_goal(self):
        return not self.sujas and self.posicao == INICIO

    def description(self):
        return "Problema do aspirador de po em uma matriz quadrada"

    def cost(self):
        return 1

    def env(self):
        return json.dumps({"posicao": self.posicao, "sujas": sorted(self.sujas)})


class BuscaProfundidadeIterativa:

    def __init__(self, limite_maximo):
        self.limite_maximo = limite_maximo
        self.limite_atingido = 0

    def search(self, state):
        algorithm = BuscaProfundidade()

        for profundidade in range(self.limite_maximo + 1):
            self.limite_atingido = profundidade
            AgentSpecification.limite_atual = profundidade
            result = algorithm.search(state, m=profundidade, pruning="general")

            if result is not None:
                return result

        return None


def distancia_manhattan(origem, destino):
    return abs(origem[0] - destino[0]) + abs(origem[1] - destino[1])


def gerar_mapa(n):
    celulas = [(linha, coluna) for linha in range(n) for coluna in range(n)]
    sujas = set(random.sample(celulas, (n * n) // 2))
    mapa = [
        ["S" if (linha, coluna) in sujas else "." for coluna in range(n)]
        for linha in range(n)
    ]
    return mapa, sujas


def limite_maximo(n):
    return ((n * n) // 2) + ((n * n) - 1) + (2 * (n - 1))


def limite_inferior(estado):
    if not estado.sujas:
        return distancia_manhattan(estado.posicao, INICIO)

    maior_distancia_obrigatoria = max(
        distancia_manhattan(estado.posicao, suja)
        + distancia_manhattan(suja, INICIO)
        for suja in estado.sujas
    )
    return len(estado.sujas) + maior_distancia_obrigatoria


def executar_teste(n):
    mapa, sujas = gerar_mapa(n)
    state = AgentSpecification("", n, INICIO, sujas)
    algorithm = BuscaProfundidadeIterativa(limite_maximo(n))

    tracemalloc.start()
    memoria_inicial = tracemalloc.get_traced_memory()[0]
    tempo_inicial = time.perf_counter()
    AgentSpecification.tempo_inicial = tempo_inicial
    AgentSpecification.tempo_maximo = TEMPO_MAXIMO_SEGUNDOS

    try:
        result = algorithm.search(state)
        status = "sucesso" if result is not None else "falha"
    except InterrupcaoBusca as interrupcao:
        result = None
        status = "interrompido por " + interrupcao.motivo

    tempo_final = time.perf_counter()
    memoria_final = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()

    return {
        "n": n,
        "mapa": mapa,
        "limite_maximo": algorithm.limite_maximo,
        "status": status,
        "tempo": tempo_final - tempo_inicial,
        "memoria": memoria_final - memoria_inicial,
        "limite_atingido": algorithm.limite_atingido,
        "tamanho_solucao": result.depth if result else 0,
        "caminho": result.show_path() if result else "",
    }


def imprimir_resultado(resultado):
    print("Mapa:", str(resultado["n"]) + "x" + str(resultado["n"]))
    print("Limite maximo:", resultado["limite_maximo"])
    print("Status:", resultado["status"])
    print("Tempo:", round(resultado["tempo"], 4), "segundos")
    print("Memoria:", round(resultado["memoria"] / 1024, 2), "KB")
    print("Limite atingido:", resultado["limite_atingido"])
    print("Tamanho da solucao:", resultado["tamanho_solucao"])

    if resultado["status"] == "sucesso":
        print("Caminho:", resultado["caminho"])

    print("-" * 40)


def criar_csv():
    with open(ARQUIVO_CSV, "a+", newline="", encoding="utf-8") as arquivo:
        arquivo.seek(0, 2)

        if arquivo.tell() == 0:
            escritor = csv.writer(arquivo)
            escritor.writerow(["tamanho_mapa", "tempo_segundos", "memoria_kb"])


def salvar_resultado_csv(resultado):
    with open(ARQUIVO_CSV, "a", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow([
            str(resultado["n"]) + "x" + str(resultado["n"]),
            round(resultado["tempo"], 4),
            round(resultado["memoria"] / 1024, 2),
        ])


def main():
    sys.setrecursionlimit(10000)
    random.seed(SEED)
    print("Busca em profundidade iterativa")
    criar_csv()

    for n in range(DIMENSAO_INICIAL, DIMENSAO_FINAL + 1):
        resultado = executar_teste(n)
        imprimir_resultado(resultado)
        salvar_resultado_csv(resultado)

        if resultado["status"] == "interrompido por tempo":
            break


if __name__ == "__main__":
    main()
