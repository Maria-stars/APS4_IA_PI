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
ARQUIVO_CSV = "busca_profundidade.csv"


class InterrupcaoBusca(Exception):

    def __init__(self, motivo):
        super().__init__(motivo)
        self.motivo = motivo


class AgentSpecification(State):
    tempo_inicial = 0
    tempo_maximo = TEMPO_MAXIMO_SEGUNDOS

    def __init__(self, op, n, posicao, sujas, profundidade=0):
        super().__init__(op)
        self.n = n
        self.posicao = posicao
        self.sujas = tuple(sorted(sujas))
        self.profundidade = profundidade


    def successors(self):
        if self.tempo_estourado():
            raise InterrupcaoBusca("tempo")

        successors = []

        for nome, nova_posicao in self.movimentos_validos():
            novo_estado = self.novo_estado(
                "ir " + nome,
                posicao=nova_posicao
            )

            successors.append(novo_estado)

        if self.posicao in self.sujas:
            novas_sujas = set(self.sujas)
            novas_sujas.remove(self.posicao)

            novo_estado = self.novo_estado(
                "limpar",
                sujas=novas_sujas
            )

            successors.append(novo_estado)

        return successors


    def tempo_estourado(self):
        tempo_atual = time.perf_counter()

        return (
            tempo_atual - AgentSpecification.tempo_inicial
            > AgentSpecification.tempo_maximo
        )
    

    def movimentos_validos(self):
        linha, coluna = self.posicao
        movimentos = []

        for nome, (d_linha, d_coluna) in MOVIMENTOS:
            nova_linha = linha + d_linha
            nova_coluna = coluna + d_coluna

            if (0 <= nova_linha < self.n and 0 <= nova_coluna < self.n):
                movimentos.append((nome, (nova_linha, nova_coluna)))

        return movimentos


    def novo_estado(self, op, posicao=None, sujas=None):
        if posicao is None:
            posicao = self.posicao

        if sujas is None:
            sujas = self.sujas

        return AgentSpecification(
            op,
            self.n,
            posicao,
            sujas,
            self.profundidade + 1
        )


    def is_goal(self):
        if self.sujas:
            return False

        if self.posicao != INICIO:
            return False

        return True


    def description(self):
        return "Problema do aspirador de po em uma matriz quadrada"


    def cost(self):
        return 1


    def env(self):
        return json.dumps({"posicao": self.posicao, "sujas": sorted(self.sujas)})


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


def executar_teste(n):
    mapa, sujas = gerar_mapa(n)
    state = AgentSpecification(
        "",
        n,
        INICIO,
        sujas
    )

    algorithm = BuscaProfundidade()

    limite = limite_maximo(n)

    tracemalloc.start()

    memoria_inicial = tracemalloc.get_traced_memory()[0]

    tempo_inicial = time.perf_counter()

    AgentSpecification.tempo_inicial = tempo_inicial
    AgentSpecification.tempo_maximo = TEMPO_MAXIMO_SEGUNDOS

    try:
        result = algorithm.search(
            state,
            m=limite,
            pruning="general"
        )

        if result is not None:
            status = "sucesso"
        else:
            status = "falha"

    except InterrupcaoBusca as interrupcao:
        result = None
        status = ("interrompido por " + interrupcao.motivo)

    tempo_final = time.perf_counter()
    memoria_final = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()

    return {
        "n": n,
        "mapa": mapa,
        "limite_maximo": limite,
        "status": status,
        "tempo": tempo_final - tempo_inicial,
        "memoria": memoria_final - memoria_inicial,
        "tamanho_solucao": result.depth if result else 0,
        "caminho": result.show_path() if result else "",
    }


def imprimir_resultado(resultado):
    print("Mapa:", str(resultado["n"]) + "x" + str(resultado["n"]))
    print("Limite maximo:", resultado["limite_maximo"])
    print("Status:", resultado["status"])
    print("Tempo:", round(resultado["tempo"], 4), "segundos")
    print("Memoria:", round(resultado["memoria"] / 1024, 2), "KB")
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
    print("Busca em profundidade")
    criar_csv()

    for n in range(DIMENSAO_INICIAL, DIMENSAO_FINAL + 1):
        resultado = executar_teste(n)
        imprimir_resultado(resultado)
        salvar_resultado_csv(resultado)

        if (resultado["status"] == "interrompido por tempo"):
            break


if __name__ == "__main__":
    main()