# Importa a biblioteca NetworkX para criar e manipular grafos (nós e arestas)
import networkx as nx

# Importa a biblioteca Matplotlib para desenhar os gráficos e animações
import matplotlib.pyplot as plt

# Importa patches para desenhar formas personalizadas (como o oceano azul) no gráfico
import matplotlib.patches as mpatches

# Importa lines para criar linhas personalizadas na legenda
import matplotlib.lines as mlines

# Importa NumPy para cálculos matemáticos (usado na interpolação do movimento do caminhão)
import numpy as np

# Importa tipos para anotação de código (ajuda na leitura e IDEs)
from typing import List, Tuple

# Importa a biblioteca copy para criar cópias profundas dos objetos (backup dos dados)
import copy

# --- PALETA DE CORES "GOVERNO FEDERAL" ---
# Define um dicionário com as cores oficiais usadas no sistema para manter consistência visual
COLORS = {
    "bg": "#F4F6F9",  # Cor de fundo (Cinza Gelo) para parecer um software corporativo
    "road": "#95A5A6",  # Cor das rodovias (Cinza Concreto)
    "rail": "#2C3E50",  # Cor das ferrovias (Azul Petróleo Escuro)
    "node_origin": "#E67E22",  # Cor do nó de origem (Laranja Diamante)
    "node_port": "#2980B9",  # Cor dos portos (Azul Quadrado)
    "node_hub": "#27AE60",  # Cor dos hubs intermediários (Verde Círculo)
    "alert": "#C0392B",  # Cor de alerta/erro (Vermelho Sangue)
    "text": "#2C3E50",  # Cor do texto principal (Texto Escuro)
    "highlight": "#F1C40F",  # Cor de destaque (Dourado para o caminhão)
    "white": "#FFFFFF",  # Branco puro
}


class SoyLogisticsNet:
    """
    Classe principal que gerencia a rede logística.
    Encapsula o grafo, as posições e as funções de desenho.
    """

    def __init__(self):
        # Inicializa um grafo direcionado (DiGraph) vazio
        self.graph = nx.DiGraph()
        # Define o layout fixo (coordenadas X, Y) de cada cidade para parecer um mapa real
        # O eixo Y positivo é o Norte, Y negativo é o Sul
        self.pos = {
            "Miritituba_PA": (0, 9),
            "Santarem_PA": (3, 9.5),
            "Sinop_MT": (0, 5),
            "Sorriso_MT": (0, 2.5),
            "Campo_Novo_MT": (-4, 2.5),
            "Agua_Boa_MT": (4, 2.5),
            "Cuiaba_MT": (0, -0.5),
            "Barra_Garcas_MT": (5, -1),
            "Rondonopolis_MT": (0, -3),
            "Uberaba_MG": (4, -5.5),
            "Santos_SP": (5, -9),
        }

    def construir_cenario_padrao(self):
        """
        Popula o grafo com as cidades (nós) e estradas (arestas) do cenário real.
        Define custos, distâncias e tipos de via.
        """
        # Lista de tuplas contendo: (Origem, Destino, Custo, Distância, Nome, Info, Tipo)
        rotas = [
            ("Sorriso_MT", "Sinop_MT", 40, 85, "BR-163", "Pavimentada", "road"),
            (
                "Sinop_MT",
                "Miritituba_PA",
                140,
                830,
                "BR-163 (Norte)",
                "Logística Crítica",
                "road",
            ),
            ("Sinop_MT", "Santarem_PA", 190, 1200, "BR-230", "Longa Distância", "road"),
            (
                "Sorriso_MT",
                "Cuiaba_MT",
                60,
                420,
                "BR-163 (Sul)",
                "Concessionada",
                "road",
            ),
            ("Cuiaba_MT", "Rondonopolis_MT", 50, 210, "BR-364", "Alto Fluxo", "road"),
            (
                "Rondonopolis_MT",
                "Santos_SP",
                160,
                1400,
                "Ferronorte",
                "MALHA FERROVIÁRIA",
                "rail",
            ),  # Modal Ferroviário
            (
                "Rondonopolis_MT",
                "Uberaba_MG",
                100,
                900,
                "BR-364",
                "Pista Simples",
                "road",
            ),
            ("Uberaba_MG", "Santos_SP", 90, 490, "SP-330", "Duplicada", "road"),
            ("Sorriso_MT", "Agua_Boa_MT", 90, 450, "BR-242", "Não Pavimentada", "road"),
            ("Agua_Boa_MT", "Barra_Garcas_MT", 80, 380, "BR-158", "Precária", "road"),
            ("Barra_Garcas_MT", "Uberaba_MG", 120, 750, "BR-050", "Regular", "road"),
            ("Sorriso_MT", "Campo_Novo_MT", 70, 300, "MT-235", "Estadual", "road"),
            ("Campo_Novo_MT", "Cuiaba_MT", 110, 550, "MT-010", "Rota de Fuga", "road"),
        ]
        # Itera sobre a lista e adiciona cada rota ao grafo com todos os seus atributos
        for u, v, w, km, l, info, tipo in rotas:
            self.graph.add_edge(
                u, v, weight=w, distance=km, label=l, info=info, type=tipo
            )

    def _calcular_custo_manual(self, caminho: List[str]):
        """
        Calcula o custo total de uma rota somando manualmente os pesos das arestas.
        Requisito acadêmico para não usar função pronta de soma.
        """
        # Usa list comprehension e zip para pegar pares (u, v) e somar seus pesos ('weight')
        return sum(
            self.graph[u][v]["weight"] for u, v in zip(caminho[:-1], caminho[1:])
        )

    # --- MÉTODOS DE CÁLCULO ---
    def buscar_melhor_rota(self, origem: str, destinos: List[str]):
        """
        Encontra a rota de menor custo entre a origem e uma lista de destinos possíveis.
        Retorna o menor custo e a lista de cidades dessa rota.
        """
        melhor_custo = float("inf")  # Inicializa com infinito
        melhor_caminho = []
        for destino in destinos:
            try:
                # Encontra TODOS os caminhos simples (sem loops) possíveis
                caminhos = list(
                    nx.all_simple_paths(self.graph, source=origem, target=destino)
                )
                for caminho in caminhos:
                    # Calcula o custo de cada caminho encontrado
                    custo = self._calcular_custo_manual(caminho)
                    # Se for menor que o melhor encontrado até agora, atualiza
                    if custo < melhor_custo:
                        melhor_custo = custo
                        melhor_caminho = caminho
            except:
                pass  # Ignora destinos inalcançáveis
        return melhor_custo, melhor_caminho

    def obter_todas_rotas(self, origem, destinos):
        """
        Retorna UMA LISTA com todas as rotas possíveis, ordenadas por custo.
        Usado para gerar os múltiplos cenários (do melhor para o pior).
        """
        todas_rotas = []
        for destino in destinos:
            try:
                caminhos = list(
                    nx.all_simple_paths(self.graph, source=origem, target=destino)
                )
                for caminho in caminhos:
                    custo = self._calcular_custo_manual(caminho)
                    # Armazena o caminho, o custo e o destino em um dicionário
                    todas_rotas.append(
                        {"caminho": caminho, "custo": custo, "destino": destino}
                    )
            except:
                pass
        # Ordena a lista do menor custo para o maior (lambda x: x['custo'])
        return sorted(todas_rotas, key=lambda x: x["custo"])

    def criar_cenario_falha(self, u: str, v: str):
        """
        Cria uma cópia da rede e remove uma estrada específica (simula bloqueio).
        Usa deepcopy para não estragar o grafo original.
        """
        nova = copy.deepcopy(self)
        if nova.graph.has_edge(u, v):
            nova.graph.remove_edge(u, v)
        return nova

    # --- AUXILIAR DE DESENHO (Base do Mapa - Estilo Luxo) ---
    def _desenhar_base_luxo(self, ax, titulo, subtitulo):
        """
        Função privada que desenha o fundo bonito (linhas, nós, legendas) em um eixo (ax).
        É reutilizada por todas as funções de visualização.
        """
        ax.set_facecolor(COLORS["bg"])  # Define a cor de fundo

        # Adiciona textos de cabeçalho (Título, Subtítulo, Data)
        plt.figtext(
            0.05,
            0.95,
            "SISTEMA NACIONAL DE LOGÍSTICA E TRANSPORTE",
            fontsize=10,
            fontweight="bold",
            color="#7F8C8D",
        )
        plt.figtext(
            0.05,
            0.92,
            titulo.upper(),
            fontsize=22,
            fontweight="bold",
            color=COLORS["text"],
        )
        plt.figtext(0.05, 0.89, subtitulo, fontsize=12, color="#7F8C8D")
        plt.figtext(
            0.95,
            0.95,
            "RELATÓRIO TÉCNICO\nNOV/2025",
            fontsize=10,
            ha="right",
            color="#7F8C8D",
        )

        # Separa as arestas em duas listas: Rodovias e Ferrovias
        road_edges = [
            (u, v) for u, v, d in self.graph.edges(data=True) if d.get("type") == "road"
        ]
        rail_edges = [
            (u, v) for u, v, d in self.graph.edges(data=True) if d.get("type") == "rail"
        ]

        # Desenha Rodovias (Linha sólida)
        nx.draw_networkx_edges(
            self.graph,
            self.pos,
            edgelist=road_edges,
            edge_color=COLORS["road"],
            width=2,
            arrowsize=10,
            connectionstyle="arc3,rad=0.1",
            ax=ax,
        )
        # Desenha Ferrovias (Linha tracejada - style='dashed')
        nx.draw_networkx_edges(
            self.graph,
            self.pos,
            edgelist=rail_edges,
            edge_color=COLORS["rail"],
            width=3,
            arrowsize=10,
            style="dashed",
            connectionstyle="arc3,rad=0.1",
            ax=ax,
        )

        # Cria os labels (caixinhas de texto) para as arestas
        edge_labels = {}
        for u, v, d in self.graph.edges(data=True):
            tipo_str = "[FERROVIA]" if d["type"] == "rail" else ""
            label_text = f"{d['label']}\nR$ {d['weight']}\n{d['info']} {tipo_str}"
            edge_labels[(u, v)] = label_text

        # Desenha os labels das arestas com fundo branco e borda
        nx.draw_networkx_edge_labels(
            self.graph,
            self.pos,
            edge_labels=edge_labels,
            font_size=7,
            font_family="monospace",
            font_color="#444",
            bbox=dict(
                facecolor="white",
                edgecolor="#BDC3C7",
                boxstyle="round,pad=0.3",
                alpha=0.9,
            ),
            ax=ax,
        )

        # Desenha os nós (Cidades) com formas diferentes para cada tipo
        # Origem = Diamante (D)
        nx.draw_networkx_nodes(
            self.graph,
            self.pos,
            nodelist=["Sorriso_MT"],
            node_shape="D",
            node_size=4500,
            node_color=COLORS["node_origin"],
            ax=ax,
            edgecolors="white",
            linewidths=2,
        )
        # Portos = Quadrado (s)
        portos = [
            n
            for n in self.graph.nodes()
            if "Santos" in n or "Miritituba" in n or "Santarem" in n
        ]
        nx.draw_networkx_nodes(
            self.graph,
            self.pos,
            nodelist=portos,
            node_shape="s",
            node_size=3500,
            node_color=COLORS["node_port"],
            ax=ax,
            edgecolors="white",
            linewidths=2,
        )
        # Hubs = Círculo (o)
        hubs = [n for n in self.graph.nodes() if n not in portos and n != "Sorriso_MT"]
        nx.draw_networkx_nodes(
            self.graph,
            self.pos,
            nodelist=hubs,
            node_shape="o",
            node_size=2000,
            node_color=COLORS["node_hub"],
            ax=ax,
            edgecolors="white",
            linewidths=2,
        )

        # Desenha o nome das cidades
        pos_labels = {
            k: (v[0], v[1] - 0.4) for k, v in self.pos.items()
        }  # Ajusta posição para baixo do nó
        nx.draw_networkx_labels(
            self.graph,
            pos_labels,
            font_size=9,
            font_weight="bold",
            font_color=COLORS["text"],
            ax=ax,
        )

        # Cria a legenda personalizada no canto superior direito
        legend_elements = [
            mpatches.Patch(color=COLORS["node_origin"], label="Origem"),
            mpatches.Patch(color=COLORS["node_port"], label="Porto"),
            mpatches.Patch(color=COLORS["node_hub"], label="Hub"),
            mlines.Line2D(
                [], [], color=COLORS["rail"], linestyle="--", label="Ferrovia"
            ),
            mlines.Line2D([], [], color=COLORS["road"], linestyle="-", label="Rodovia"),
            mlines.Line2D([], [], color=COLORS["alert"], linewidth=4, label="Bloqueio"),
            mlines.Line2D(
                [],
                [],
                color=COLORS["highlight"],
                marker="o",
                linestyle="None",
                label="Veículo",
            ),
        ]
        ax.legend(
            handles=legend_elements,
            loc="upper right",
            title="LEGENDA",
            fancybox=True,
            shadow=True,
            fontsize=8,
            facecolor="white",
        )

        # Remove os eixos numéricos (X e Y) para limpar o visual
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

    # --- ANIMAÇÕES (Para o main.py) ---
    def animar_rota_normal(
        self, caminho: List[str], titulo="Operação Nominal", subtitulo="Fluxo Eficiente"
    ):
        """
        Anima um caminhão percorrendo uma rota do início ao fim sem interrupções.
        """
        plt.ion()  # Ativa modo interativo do Matplotlib
        fig, ax = plt.subplots(figsize=(16, 14), facecolor=COLORS["bg"])

        # Desenha o mapa base com o título dinâmico
        self._desenhar_base_luxo(ax, titulo, subtitulo)

        # Cria o objeto visual do caminhão (bolinha) e do rastro (linha)
        (truck,) = ax.plot(
            [],
            [],
            marker="o",
            markersize=12,
            color=COLORS["highlight"],
            markeredgecolor="white",
            markeredgewidth=2,
            zorder=10,
        )
        (rastro,) = ax.plot(
            [], [], color=COLORS["highlight"], linewidth=4, alpha=0.5, zorder=5
        )
        x_track, y_track = [], []

        print(f"Iniciando: {' -> '.join(caminho)}")
        # Loop de animação: percorre cada trecho da rota
        for u, v in zip(caminho[:-1], caminho[1:]):
            start, end = np.array(self.pos[u]), np.array(self.pos[v])
            steps = 30  # Número de quadros por trecho (suavidade)
            for i in range(steps + 1):
                # Interpolação linear para mover o caminhão
                pos = start + (i / steps) * (end - start)
                truck.set_data([pos[0]], [pos[1]])  # Atualiza caminhão
                x_track.append(pos[0])
                y_track.append(pos[1])
                rastro.set_data(x_track, y_track)  # Atualiza rastro
                plt.pause(0.01)  # Pausa para o olho humano acompanhar

        # Mensagem de sucesso ao final
        dest_x, dest_y = self.pos[caminho[-1]]
        ax.text(
            dest_x,
            dest_y - 1.2,
            "CHEGADA CONFIRMADA",
            ha="center",
            fontsize=10,
            color="white",
            fontweight="bold",
            bbox=dict(
                facecolor=COLORS["node_hub"], edgecolor="none", boxstyle="round,pad=0.5"
            ),
        )
        plt.ioff()
        plt.show()

    def animar_cenario_crise(self, caminho_falha: List[str], caminho_novo: List[str]):
        """
        [DEPRECADA] Versão antiga da animação de crise.
        Mantida apenas para compatibilidade, mas a lógica principal agora está em 'animar_multiplas_tentativas'.
        """
        # (O código é similar ao animar_multiplas_tentativas, mas simplificado para 1 falha só)
        pass

    def animar_multiplas_tentativas(
        self, lista_de_caminhos: List[List[str]], titulo: str, subtitulo: str
    ):
        """
        O MOTOR DA CASCATA: Recebe uma lista de rotas.
        Tenta a 1ª -> Falha -> Volta.
        Tenta a 2ª -> Falha -> Volta.
        Tenta a Última -> Sucesso.
        """
        plt.ion()
        fig, ax = plt.subplots(figsize=(16, 14), facecolor=COLORS["bg"])
        self._desenhar_base_luxo(ax, titulo, subtitulo)

        # Caixa de Status no canto inferior esquerdo
        status_box = ax.text(
            0.02,
            0.02,
            "STATUS: PLANEJAMENTO OPERACIONAL...",
            transform=ax.transAxes,
            fontsize=12,
            fontweight="bold",
            color="white",
            bbox=dict(facecolor=COLORS["text"], boxstyle="round,pad=0.6"),
        )

        (truck,) = ax.plot(
            [],
            [],
            marker="o",
            markersize=12,
            color=COLORS["highlight"],
            markeredgecolor="white",
            markeredgewidth=2,
            zorder=10,
        )
        (rastro,) = ax.plot(
            [], [], color=COLORS["highlight"], linewidth=4, alpha=0.5, zorder=5
        )

        mensagens_erro = ["QUEDA DE BARREIRA", "GREVE", "PONTE QUEBRADA", "ALAGAMENTO"]

        # Loop Principal: Itera sobre as rotas fornecidas
        for index, caminho in enumerate(lista_de_caminhos):
            is_last = (
                index == len(lista_de_caminhos) - 1
            )  # Verifica se é a última (a que vai dar certo)
            destino_atual = caminho[-1].split("_")[0]

            # Limpa o rastro para a nova tentativa
            x_track = []
            y_track = []
            rastro.set_data([], [])

            status_box.set_text(f"TENTATIVA {index+1}: ROTA PARA {destino_atual}")
            status_box.set_bbox(
                dict(facecolor=COLORS["text"], boxstyle="round,pad=0.6")
            )

            # Define até onde o caminhão vai. Se for falhar, vai só até 70% do caminho.
            limite_steps = len(caminho) if is_last else max(2, int(len(caminho) * 0.7))
            block_pos = None

            # Animação de IDA
            for i in range(limite_steps - 1):
                u, v = caminho[i], caminho[i + 1]
                parar_no_meio = (not is_last) and (
                    i == limite_steps - 2
                )  # Flag para parar na aresta final
                start, end = np.array(self.pos[u]), np.array(self.pos[v])
                steps = 25
                for s in range(steps + 1):
                    progresso = (
                        (s / steps) * 0.8 if parar_no_meio else (s / steps)
                    )  # Para em 80% da aresta
                    pos = start + progresso * (end - start)
                    truck.set_data([pos[0]], [pos[1]])
                    x_track.append(pos[0])
                    y_track.append(pos[1])
                    rastro.set_data(x_track, y_track)
                    plt.pause(0.01)
                if parar_no_meio:
                    block_pos = pos

            # Se não for a última rota, executa o BLOQUEIO e RETORNO
            if not is_last:
                msg = mensagens_erro[index % len(mensagens_erro)]
                status_box.set_text(f"⚠️ FALHA: {msg}!")
                status_box.set_bbox(
                    dict(facecolor=COLORS["alert"], boxstyle="round,pad=0.6")
                )

                # Desenha o X vermelho
                ax.plot(
                    block_pos[0],
                    block_pos[1],
                    marker="X",
                    markersize=25,
                    color=COLORS["alert"],
                    markeredgecolor="white",
                    markeredgewidth=2,
                )
                plt.pause(1.0)  # Pausa dramática

                status_box.set_text("RETORNANDO À BASE...")
                rastro.set_color(COLORS["alert"])  # Rastro fica vermelho

                # Lógica de RETORNO (Backtracking)
                path_percorrido = caminho[:limite_steps]
                path_volta = list(
                    reversed(path_percorrido)
                )  # Inverte a lista de cidades
                start_back = block_pos
                end_back = np.array(self.pos[path_volta[0]])

                # Volta do bloqueio até o nó anterior
                for s in range(15):
                    pos = start_back + (s / 15) * (end_back - start_back)
                    truck.set_data([pos[0]], [pos[1]])
                    plt.pause(0.01)

                # Volta o resto do caminho até a origem
                for i in range(len(path_volta) - 1):
                    u_b, v_b = path_volta[i], path_volta[i + 1]
                    start, end = np.array(self.pos[u_b]), np.array(self.pos[v_b])
                    for s in range(15):
                        pos = start + (s / 15) * (end - start)
                        truck.set_data([pos[0]], [pos[1]])
                        plt.pause(0.01)
                rastro.set_color(COLORS["highlight"])  # Reseta cor
            else:
                # Se for a última rota, SUCESSO
                status_box.set_text("STATUS: ENTREGA REALIZADA.")
                status_box.set_bbox(
                    dict(facecolor=COLORS["node_hub"], boxstyle="round,pad=0.6")
                )
                dest_x, dest_y = self.pos[caminho[-1]]
                ax.text(
                    dest_x,
                    dest_y - 1.2,
                    "DESTINO ALCANÇADO",
                    ha="center",
                    fontsize=10,
                    color="white",
                    fontweight="bold",
                    bbox=dict(
                        facecolor=COLORS["node_port"],
                        edgecolor="none",
                        boxstyle="round,pad=0.5",
                    ),
                )

        plt.ioff()
        plt.show()

    # --- VISUALIZAÇÃO ESTÁTICA (Dashboard) ---
    def plotar_caminho_estatico_em_ax(self, ax, dados_rota, rank_titulo, cor_destaque):
        """
        Desenha um grafo estático em um subplot (ax).
        Usado pelo main_dashboard.py para criar o grid 2x2.
        """
        ax.set_facecolor(COLORS["bg"])
        caminho = dados_rota["caminho"]
        custo = dados_rota["custo"]
        ax.set_title(
            f"{rank_titulo}\nCusto: R$ {custo}/ton",
            fontsize=10,
            fontweight="bold",
            color=COLORS["text"],
            pad=10,
        )

        # Desenha todas as estradas em cinza claro no fundo
        road_edges = [
            (u, v) for u, v, d in self.graph.edges(data=True) if d.get("type") == "road"
        ]
        rail_edges = [
            (u, v) for u, v, d in self.graph.edges(data=True) if d.get("type") == "rail"
        ]
        nx.draw_networkx_edges(
            self.graph,
            self.pos,
            edgelist=road_edges,
            edge_color=COLORS["road"],
            width=1,
            arrowsize=5,
            connectionstyle="arc3,rad=0.1",
            ax=ax,
            alpha=0.4,
        )
        nx.draw_networkx_edges(
            self.graph,
            self.pos,
            edgelist=rail_edges,
            edge_color=COLORS["rail"],
            width=1.5,
            style="dashed",
            connectionstyle="arc3,rad=0.1",
            ax=ax,
            alpha=0.4,
        )

        # Desenha a rota específica com a cor de destaque
        if caminho:
            path_edges = list(zip(caminho[:-1], caminho[1:]))
            path_road = []
            path_rail = []
            for u, v in path_edges:
                if self.graph[u][v].get("type") == "rail":
                    path_rail.append((u, v))
                else:
                    path_road.append((u, v))
            nx.draw_networkx_edges(
                self.graph,
                self.pos,
                edgelist=path_road,
                edge_color=cor_destaque,
                width=3,
                arrowsize=10,
                connectionstyle="arc3,rad=0.1",
                ax=ax,
            )
            nx.draw_networkx_edges(
                self.graph,
                self.pos,
                edgelist=path_rail,
                edge_color=cor_destaque,
                width=3,
                style="dashed",
                connectionstyle="arc3,rad=0.1",
                ax=ax,
            )

        # Desenha os nós miniaturizados
        nx.draw_networkx_nodes(
            self.graph,
            self.pos,
            nodelist=["Sorriso_MT"],
            node_shape="D",
            node_size=1500,
            node_color=COLORS["node_origin"],
            ax=ax,
            edgecolors="white",
            linewidths=1.5,
        )
        portos = [
            n
            for n in self.graph.nodes()
            if "Santos" in n or "Miritituba" in n or "Santarem" in n
        ]
        nx.draw_networkx_nodes(
            self.graph,
            self.pos,
            nodelist=portos,
            node_shape="s",
            node_size=1200,
            node_color=COLORS["node_port"],
            ax=ax,
            edgecolors="white",
            linewidths=1.5,
        )
        hubs = [n for n in self.graph.nodes() if n not in portos and n != "Sorriso_MT"]
        nx.draw_networkx_nodes(
            self.graph,
            self.pos,
            nodelist=hubs,
            node_shape="o",
            node_size=800,
            node_color=COLORS["node_hub"],
            ax=ax,
            edgecolors="white",
            linewidths=1.5,
        )

        # Labels simplificados (remove _MT, _PA para economizar espaço)
        labels_clean = {
            k: k.replace("_MT", "")
            .replace("_PA", "")
            .replace("_SP", "")
            .replace("_MG", "")
            for k in self.pos.keys()
        }
        nx.draw_networkx_labels(
            self.graph,
            self.pos,
            labels=labels_clean,
            font_size=7,
            font_weight="bold",
            font_color=COLORS["text"],
            ax=ax,
        )

        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_edgecolor(cor_destaque)
            spine.set_linewidth(2)

    def visualizar(self, titulo: str, subtitle: str = ""):
        """Apenas abre uma janela estática do grafo."""
        fig, ax = plt.subplots(figsize=(16, 14), facecolor=COLORS["bg"])
        self._desenhar_base_luxo(ax, titulo, subtitle)
        plt.show()
