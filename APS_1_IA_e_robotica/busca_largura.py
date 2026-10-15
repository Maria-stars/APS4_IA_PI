from aigyminsper.search.graph import State
from aigyminsper.search.search_algorithms import BuscaLargura
import csv
import json
import random
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
TEMPO_MAXIMO_SEGUNDOS = 3000.0
SEED = 42
ARQUIVO_CSV = "busca_largura.csv"


class InterrupcaoBusca(Exception):

    def __init__(self, motivo):
        super().__init__(motivo)
        self.motivo = motivo


class AgentSpecification(State):

    tempo_inicial = 0
    tempo_maximo = TEMPO_MAXIMO_SEGUNDOS

    def __init__(self, op, n, posicao, sujas):
        super().__init__(op)
        self.n = n
        self.posicao = posicao
        self.sujas = tuple(sorted(sujas))

    def successors(self):
        if self.tempo_estourado():
            raise InterrupcaoBusca("tempo")

        successors = []

        # Se a posição atual estiver suja, permite limpá-la.
        if self.posicao in self.sujas:
            novas_sujas = set(self.sujas)
            novas_sujas.remove(self.posicao)

            successors.append(
                self.novo_estado(
                    "limpar",
                    sujas=novas_sujas
                )
            )

        # Adiciona todos os movimentos válidos.
        for nome, nova_posicao in self.movimentos_validos():
            successors.append(
                self.novo_estado(
                    "ir " + nome,
                    posicao=nova_posicao
                )
            )

        return successors

    def tempo_estourado(self):
        tempo_decorrido = (
            time.perf_counter() - AgentSpecification.tempo_inicial
        )

        return tempo_decorrido > AgentSpecification.tempo_maximo

    def movimentos_validos(self):
        linha, coluna = self.posicao
        movimentos = []

        for nome, (d_linha, d_coluna) in MOVIMENTOS:
            nova_linha = linha + d_linha
            nova_coluna = coluna + d_coluna

            if (
                0 <= nova_linha < self.n
                and 0 <= nova_coluna < self.n
            ):
                movimentos.append(
                    (nome, (nova_linha, nova_coluna))
                )

        return movimentos

    def novo_estado(self, op, posicao=None, sujas=None):
        return AgentSpecification(
            op=op,
            n=self.n,
            posicao=self.posicao if posicao is None else posicao,
            sujas=self.sujas if sujas is None else sujas,
        )

    def is_goal(self):
        # O objetivo é limpar todas as posições e retornar ao início.
        return not self.sujas and self.posicao == INICIO

    def description(self):
        return "Problema do aspirador de po em uma matriz quadrada"

    def cost(self):
        return 1

    def env(self):
        return json.dumps({
            "posicao": self.posicao,
            "sujas": sorted(self.sujas),
        })


def gerar_mapa(n):
    celulas = [
        (linha, coluna)
        for linha in range(n)
        for coluna in range(n)
    ]

    quantidade_sujas = (n * n) // 2
    sujas = set(random.sample(celulas, quantidade_sujas))

    mapa = [
        [
            "S" if (linha, coluna) in sujas else "."
            for coluna in range(n)
        ]
        for linha in range(n)
    ]

    return mapa, sujas


def executar_teste(n):
    mapa, sujas = gerar_mapa(n)

    estado_inicial = AgentSpecification(
        op="",
        n=n,
        posicao=INICIO,
        sujas=sujas,
    )

    algorithm = BuscaLargura()

    tracemalloc.start()

    memoria_inicial = tracemalloc.get_traced_memory()[0]
    tempo_inicial = time.perf_counter()

    AgentSpecification.tempo_inicial = tempo_inicial
    AgentSpecification.tempo_maximo = TEMPO_MAXIMO_SEGUNDOS

    try:
        # O pruning geral evita visitar repetidamente o mesmo estado.
        result = algorithm.search(
            estado_inicial,
            pruning="general"
        )

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
        "status": status,
        "tempo": tempo_final - tempo_inicial,
        "memoria": memoria_final - memoria_inicial,
        "tamanho_solucao": result.depth if result else 0,
        "caminho": result.show_path() if result else "",
    }


def imprimir_mapa(mapa):
    for linha in mapa:
        print(" ".join(linha))


def imprimir_resultado(resultado):
    print(
        "Mapa:",
        str(resultado["n"]) + "x" + str(resultado["n"])
    )

    imprimir_mapa(resultado["mapa"])

    print("Status:", resultado["status"])
    print(
        "Tempo:",
        round(resultado["tempo"], 4),
        "segundos"
    )
    print(
        "Memoria:",
        round(resultado["memoria"] / 1024, 2),
        "KB"
    )
    print(
        "Tamanho da solucao:",
        resultado["tamanho_solucao"]
    )

    if resultado["status"] == "sucesso":
        print("Caminho:", resultado["caminho"])

    print("-" * 40)


def criar_csv():
    with open(
        ARQUIVO_CSV,
        "a+",
        newline="",
        encoding="utf-8"
    ) as arquivo:

        arquivo.seek(0, 2)

        if arquivo.tell() == 0:
            escritor = csv.writer(arquivo)

            escritor.writerow([
                "tamanho_mapa",
                "status",
                "tempo_segundos",
                "memoria_kb",
                "tamanho_solucao",
            ])


def salvar_resultado_csv(resultado):
    with open(
        ARQUIVO_CSV,
        "a",
        newline="",
        encoding="utf-8"
    ) as arquivo:

        escritor = csv.writer(arquivo)

        escritor.writerow([
            str(resultado["n"]) + "x" + str(resultado["n"]),
            resultado["status"],
            round(resultado["tempo"], 4),
            round(resultado["memoria"] / 1024, 2),
            resultado["tamanho_solucao"],
        ])


def main():
    random.seed(SEED)

    print("Busca em largura")
    criar_csv()

    for n in range(
        DIMENSAO_INICIAL,
        DIMENSAO_FINAL + 1
    ):
        resultado = executar_teste(n)

        imprimir_resultado(resultado)
        salvar_resultado_csv(resultado)

        if resultado["status"] == "interrompido por tempo":
            break


if __name__ == "__main__":
    main()