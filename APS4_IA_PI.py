"""Interface gráfica para o código do entregador.
Instalação: python -m pip install aigyminsper
Execução: python entregador_visual.py
Posições no formato (linha, coluna), com origem no canto superior esquerdo.
A animação mostra o plano encontrado, não a exploração interna da busca.
"""
import random
import threading
import queue
import heapq
from itertools import count
import tkinter as tk
from tkinter import ttk, messagebox
from aigyminsper.search.graph import State, Node


class Entregador(State):
    def __init__(self, mapa, agente, pacote, destino, obstaculo, pedagio,
                 op="", carregando=False, custo_acao=0):
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
        if self.mapa[linha][coluna] == 3:
            custo = custo + 2

        # Movimento para cima.
        if linha - 1 >= 0 and self.mapa[linha - 1][coluna] != 0:
            nova_posicao = (linha - 1, coluna)
            successors.append(Entregador(
                mapa=self.mapa, agente=nova_posicao, pacote=self.pacote,
                destino=self.destino, obstaculo=self.obstaculo,
                pedagio=self.pedagio, op="cima",
                carregando=self.carregando, custo_acao=custo))

        # Movimento para baixo.
        if linha + 1 < tamanho_x and self.mapa[linha + 1][coluna] != 0:
            nova_posicao = (linha + 1, coluna)
            successors.append(Entregador(
                mapa=self.mapa, agente=nova_posicao, pacote=self.pacote,
                destino=self.destino, obstaculo=self.obstaculo,
                pedagio=self.pedagio, op="baixo",
                carregando=self.carregando, custo_acao=custo))

        # Movimento para a direita.
        if coluna + 1 < tamanho_y and self.mapa[linha][coluna + 1] != 0:
            nova_posicao = (linha, coluna + 1)
            successors.append(Entregador(
                mapa=self.mapa, agente=nova_posicao, pacote=self.pacote,
                destino=self.destino, obstaculo=self.obstaculo,
                pedagio=self.pedagio, op="direita",
                carregando=self.carregando, custo_acao=custo))

        # Movimento para a esquerda.
        if coluna - 1 >= 0 and self.mapa[linha][coluna - 1] != 0:
            nova_posicao = (linha, coluna - 1)
            successors.append(Entregador(
                mapa=self.mapa, agente=nova_posicao, pacote=self.pacote,
                destino=self.destino, obstaculo=self.obstaculo,
                pedagio=self.pedagio, op="esquerda",
                carregando=self.carregando, custo_acao=custo))

        if not self.carregando and self.agente == self.pacote:
            successors.append(Entregador(
                mapa=self.mapa, agente=self.agente, pacote=None,
                destino=self.destino, obstaculo=self.obstaculo,
                pedagio=self.pedagio, op="pegar pacote",
                carregando=True, custo_acao=custo))

        if self.carregando:
            successors.append(Entregador(
                mapa=self.mapa, agente=self.agente, pacote=self.agente,
                destino=self.destino, obstaculo=self.obstaculo,
                pedagio=self.pedagio, op="entregar pacote",
                carregando=False, custo_acao=custo))
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
        return str((self.agente, self.pacote, self.carregando))

    def h(self):
        # Heurística neutra para executar A* sem inventar uma estimativa.
        # Não altera as regras, sucessores ou custos do problema.
        return 0


def busca_a_estrela(estado_inicial):
    """A* com atualização do melhor custo g para cada estado.

    Com h() = 0, equivale à busca de custo uniforme. Um estado pode
    voltar à fila se encontrarmos um caminho mais barato até ele.
    """
    desempate = count()
    inicio = Node(estado_inicial, None)
    abertos = [(inicio.f(), next(desempate), inicio)]
    melhor_custo = {estado_inicial.env(): 0}

    while abertos:
        _, _, atual = heapq.heappop(abertos)
        chave = atual.state.env()
        if atual.g != melhor_custo[chave]:
            continue  # Entrada antiga, substituída por um caminho melhor.
        if atual.state.is_goal():
            return atual

        for sucessor in atual.state.successors():
            novo = Node(sucessor, atual)
            chave = sucessor.env()
            if novo.g < melhor_custo.get(chave, float("inf")):
                melhor_custo[chave] = novo.g
                heapq.heappush(abertos, (novo.f(), next(desempate), novo))
    return None


def gerar_estado(n):
    if not 3 <= n <= 50:
        raise ValueError("Digite uma dimensão entre 3 e 50.")
    mapa = [[2] * n for _ in range(n)]
    posicoes = [(linha, coluna) for linha in range(n) for coluna in range(n)]
    random.shuffle(posicoes)
    agente = posicoes.pop()
    pacote = posicoes.pop()
    destino = posicoes.pop()
    quantidade_obstaculos = random.randint(0, (n * n) // 4)
    obstaculo = set()
    for _ in range(quantidade_obstaculos):
        posicao = posicoes.pop()
        obstaculo.add(posicao)
        linha, coluna = posicao
        mapa[linha][coluna] = 0
    quantidade_pedagios = random.randint(1, min(len(posicoes), (n * n) // 5))
    pedagio = set()
    for _ in range(quantidade_pedagios):
        posicao = posicoes.pop()
        pedagio.add(posicao)
        linha, coluna = posicao
        mapa[linha][coluna] = 3
    return Entregador(mapa, agente, pacote, destino, obstaculo, pedagio, op="início")


class InterfaceEntregador:
    def __init__(self, janela):
        self.janela = janela
        janela.title("Entregador — visualização com A*")
        self.estado_inicial = None
        self.estado = None
        self.timer = None
        self.nos = []
        self.indice = 0
        self.resultados = queue.Queue()
        self.buscando = False

        painel = ttk.Frame(janela, padding=12)
        painel.pack(fill="x")
        ttk.Label(painel, text="Dimensão (n × n):").pack(side="left")
        self.dimensao = tk.StringVar(value="4")
        ttk.Spinbox(painel, from_=3, to=50, width=5,
                    textvariable=self.dimensao).pack(side="left", padx=8)
        self.gerar = ttk.Button(painel, text="Gerar mapa", command=self.novo_mapa)
        self.gerar.pack(side="left", padx=4)
        self.resolver = ttk.Button(painel, text="Buscar solução", command=self.buscar)
        self.resolver.pack(side="left", padx=4)

        ttk.Label(janela, text="A: agente   P: pacote   D: destino   A+P: carregando\n"
                  "Preto: obstáculo | Amarelo: pedágio (ação custa 3)").pack(pady=5)
        controles = ttk.Frame(janela)
        controles.pack(fill="x", padx=12)
        ttk.Button(controles, text="Pausar", command=self.parar_animacao).pack(side="left")
        ttk.Button(controles, text="Continuar", command=self.continuar).pack(side="left", padx=4)
        ttk.Button(controles, text="Próximo passo", command=self.proximo).pack(side="left")
        self.atraso = tk.IntVar(value=450)
        ttk.Label(controles, text="Intervalo (ms):").pack(side="left", padx=(14, 4))
        ttk.Scale(controles, from_=100, to=1200, variable=self.atraso).pack(side="left", fill="x", expand=True)
        area = ttk.Frame(janela)
        area.pack(fill="both", expand=True, padx=12, pady=8)
        self.canvas = tk.Canvas(area, width=600, height=450,
                                background="white", highlightthickness=0)
        vertical = ttk.Scrollbar(area, orient="vertical", command=self.canvas.yview)
        horizontal = ttk.Scrollbar(area, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        area.rowconfigure(0, weight=1)
        area.columnconfigure(0, weight=1)
        self.status = tk.StringVar()
        ttk.Label(janela, textvariable=self.status, wraplength=600).pack(padx=12, pady=5)
        ttk.Label(janela, text="A animação mostra a solução encontrada. Coordenadas: (linha, coluna).").pack(pady=5)
        self.caminho = tk.Text(janela, height=4, width=80, wrap="word", state="disabled")
        self.caminho.pack(fill="x", padx=12, pady=(0, 12))
        self.novo_mapa()
        janela.after(100, self.verificar_resultado)

    def mostrar_caminho(self, texto):
        self.caminho.config(state="normal")
        self.caminho.delete("1.0", "end")
        self.caminho.insert("1.0", texto)
        self.caminho.config(state="disabled")

    def parar_animacao(self):
        if self.timer is not None:
            self.janela.after_cancel(self.timer)
            self.timer = None

    def novo_mapa(self):
        if self.buscando:
            return
        try:
            n = int(self.dimensao.get())
            estado = gerar_estado(n)
        except ValueError:
            messagebox.showerror("Dimensão inválida", "Digite um inteiro entre 3 e 50.")
            return
        self.parar_animacao()
        self.nos = []
        self.indice = 0
        self.estado_inicial = estado
        self.estado = estado
        self.desenhar()
        self.mostrar_caminho("")
        self.status.set(f"Mapa {n} × {n}: {len(estado.obstaculo)} obstáculos e "
                        f"{len(estado.pedagio)} pedágios. Posições (linha, coluna): "
                        f"A={estado.agente}, P={estado.pacote}, D={estado.destino}.")

    def desenhar(self):
        self.canvas.delete("all")
        estado = self.estado
        n = len(estado.mapa)
        tamanho = max(28, 440 / n)
        self.canvas.configure(scrollregion=(0, 0, n * tamanho, n * tamanho))
        fonte = max(8, min(22, int(tamanho / 4)))
        cores = {0: "#273244", 2: "#f1f5f9", 3: "#fde68a"}
        for linha in range(n):
            for coluna in range(n):
                x, y = coluna * tamanho, linha * tamanho
                self.canvas.create_rectangle(x, y, x + tamanho, y + tamanho,
                    fill=cores[estado.mapa[linha][coluna]], outline="#94a3b8")
                posicao = (linha, coluna)
                rotulos = []
                if posicao == estado.destino:
                    rotulos.append("D")
                if posicao == estado.agente:
                    rotulos.append("A+P" if estado.carregando else "A")
                if posicao == estado.pacote:
                    rotulos.append("P")
                if rotulos:
                    self.canvas.create_text(x + tamanho / 2, y + tamanho / 2,
                        text="\n".join(rotulos), font=("Arial", fonte, "bold"),
                        fill="#1d4ed8")

    def buscar(self):
        if self.buscando:
            return
        self.parar_animacao()
        self.nos = []
        self.indice = 0
        self.estado = self.estado_inicial
        self.desenhar()
        self.mostrar_caminho("")
        self.buscando = True
        self.gerar.config(state="disabled")
        self.resolver.config(state="disabled")
        self.status.set("Buscando solução...")
        # A busca fica fora da thread da interface para não congelar a janela.
        estado = self.estado_inicial

        def executar():
            try:
                resultado = busca_a_estrela(estado)
                self.resultados.put((resultado, None))
            except Exception as erro:
                self.resultados.put((None, str(erro)))

        threading.Thread(target=executar, daemon=True).start()

    def verificar_resultado(self):
        try:
            resultado, erro = self.resultados.get_nowait()
        except queue.Empty:
            pass
        else:
            self.buscando = False
            self.gerar.config(state="normal")
            self.resolver.config(state="normal")
            if erro:
                self.status.set("Não foi possível concluir a busca.")
                messagebox.showerror("Erro na busca", erro)
            elif resultado is None:
                self.status.set("Este mapa não tem solução. Clique em Gerar mapa para tentar outro.")
            else:
                nos = []
                atual = resultado
                while atual is not None:
                    nos.append(atual)
                    atual = atual.father_node
                nos.reverse()
                self.mostrar_caminho(resultado.show_path())
                self.nos = nos
                self.animar(nos, 0)
        self.janela.after(100, self.verificar_resultado)

    def animar(self, nos, indice):
        self.timer = None
        self.indice = indice
        no = nos[indice]
        self.estado = no.state
        self.desenhar()
        self.status.set(f"Passo {indice}/{len(nos) - 1}: {no.state.operator}. "
                        f"Custo acumulado: {no.g}.")
        if indice + 1 < len(nos):
            self.timer = self.janela.after(int(self.atraso.get()), self.animar, nos, indice + 1)
        else:
            self.status.set(f"Entrega concluída! {len(nos) - 1} ações. Custo total: {no.g}.")

    def continuar(self):
        if self.nos and self.timer is None and self.indice + 1 < len(self.nos):
            self.animar(self.nos, self.indice + 1)

    def proximo(self):
        self.parar_animacao()
        if self.nos and self.indice + 1 < len(self.nos):
            self.animar(self.nos, self.indice + 1)
            self.parar_animacao()


def main():
    janela = tk.Tk()
    InterfaceEntregador(janela)
    janela.mainloop()


if __name__ == "__main__":
    main()
