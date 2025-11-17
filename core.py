import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np
from typing import List, Tuple
import copy

# --- PALETA DE CORES ---
COLORS = {
    "bg": "#F4F6F9",
    "road": "#95A5A6",
    "rail": "#2C3E50",
    "node_origin": "#E67E22",
    "node_port": "#2980B9",
    "node_hub": "#27AE60",
    "alert": "#C0392B",
    "text": "#2C3E50",
    "highlight": "#F1C40F",
    "white": "#FFFFFF",
}


class SoyLogisticsNet:
    def __init__(self):
        self.graph = nx.DiGraph()
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
        # ESTRUTURA: (Origem, Destino, CUSTO(R$), Km, Nome, Info, Tipo)
        # Adicionei a COLUNA KM com distâncias aproximadas reais
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
            ),
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

        for u, v, w, km, l, info, tipo in rotas:
            # Guardamos o KM como atributo da aresta também
            self.graph.add_edge(
                u, v, weight=w, distance=km, label=l, info=info, type=tipo
            )

    def _calcular_custo_manual(self, caminho: List[str]):
        return sum(
            self.graph[u][v]["weight"] for u, v in zip(caminho[:-1], caminho[1:])
        )

    def buscar_melhor_rota(self, origem: str, destinos: List[str]):
        melhor_custo = float("inf")
        melhor_caminho = []
        for destino in destinos:
            try:
                caminhos = list(
                    nx.all_simple_paths(self.graph, source=origem, target=destino)
                )
                for caminho in caminhos:
                    custo = self._calcular_custo_manual(caminho)
                    if custo < melhor_custo:
                        melhor_custo = custo
                        melhor_caminho = caminho
            except:
                pass
        return melhor_custo, melhor_caminho

    def obter_todas_rotas(self, origem, destinos):
        todas_rotas = []
        for destino in destinos:
            try:
                caminhos = list(
                    nx.all_simple_paths(self.graph, source=origem, target=destino)
                )
                for caminho in caminhos:
                    custo = self._calcular_custo_manual(caminho)
                    todas_rotas.append(
                        {"caminho": caminho, "custo": custo, "destino": destino}
                    )
            except:
                pass
        return sorted(todas_rotas, key=lambda x: x["custo"])

    def criar_cenario_falha(self, u: str, v: str):
        nova = copy.deepcopy(self)
        if nova.graph.has_edge(u, v):
            nova.graph.remove_edge(u, v)
        return nova

    # --- AUXILIAR DE DESENHO ---
    def _desenhar_base_luxo(self, ax, titulo, subtitulo):
        ax.set_facecolor(COLORS["bg"])

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
            width=2,
            arrowsize=10,
            connectionstyle="arc3,rad=0.1",
            ax=ax,
        )
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

        edge_labels = {}
        for u, v, d in self.graph.edges(data=True):
            tipo_str = "[FERROVIA]" if d["type"] == "rail" else ""
            # --- MUDANÇA VISUAL: MOSTRAR KM E PREÇO ---
            label_text = f"{d['label']}\n{d['distance']}km | R${d['weight']}\n{d['info']} {tipo_str}"
            edge_labels[(u, v)] = label_text

        nx.draw_networkx_edge_labels(
            self.graph,
            self.pos,
            edge_labels=edge_labels,
            font_size=6,
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

        pos_labels = {k: (v[0], v[1] - 0.4) for k, v in self.pos.items()}
        nx.draw_networkx_labels(
            self.graph,
            pos_labels,
            font_size=9,
            font_weight="bold",
            font_color=COLORS["text"],
            ax=ax,
        )

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
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

    # --- ANIMAÇÕES ---
    def animar_rota_normal(
        self, caminho: List[str], titulo="Operação Nominal", subtitulo="Fluxo Eficiente"
    ):
        plt.ion()
        fig, ax = plt.subplots(figsize=(16, 14), facecolor=COLORS["bg"])
        self._desenhar_base_luxo(ax, titulo, subtitulo)

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
        for u, v in zip(caminho[:-1], caminho[1:]):
            start, end = np.array(self.pos[u]), np.array(self.pos[v])
            steps = 30
            for i in range(steps + 1):
                pos = start + (i / steps) * (end - start)
                truck.set_data([pos[0]], [pos[1]])
                x_track.append(pos[0])
                y_track.append(pos[1])
                rastro.set_data(x_track, y_track)
                plt.pause(0.01)

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

    def animar_multiplas_tentativas(
        self, lista_de_caminhos: List[List[str]], titulo: str, subtitulo: str
    ):
        plt.ion()
        fig, ax = plt.subplots(figsize=(16, 14), facecolor=COLORS["bg"])
        self._desenhar_base_luxo(ax, titulo, subtitulo)

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

        for index, caminho in enumerate(lista_de_caminhos):
            is_last = index == len(lista_de_caminhos) - 1
            destino_atual = caminho[-1].split("_")[0]
            x_track = []
            y_track = []
            rastro.set_data([], [])

            status_box.set_text(f"TENTATIVA {index+1}: ROTA PARA {destino_atual}")
            status_box.set_bbox(
                dict(facecolor=COLORS["text"], boxstyle="round,pad=0.6")
            )

            limite_steps = len(caminho) if is_last else max(2, int(len(caminho) * 0.7))
            block_pos = None

            for i in range(limite_steps - 1):
                u, v = caminho[i], caminho[i + 1]
                parar_no_meio = (not is_last) and (i == limite_steps - 2)
                start, end = np.array(self.pos[u]), np.array(self.pos[v])
                steps = 25
                for s in range(steps + 1):
                    progresso = (s / steps) * 0.8 if parar_no_meio else (s / steps)
                    pos = start + progresso * (end - start)
                    truck.set_data([pos[0]], [pos[1]])
                    x_track.append(pos[0])
                    y_track.append(pos[1])
                    rastro.set_data(x_track, y_track)
                    plt.pause(0.01)
                if parar_no_meio:
                    block_pos = pos

            if not is_last:
                msg = mensagens_erro[index % len(mensagens_erro)]
                status_box.set_text(f"⚠️ FALHA: {msg}!")
                status_box.set_bbox(
                    dict(facecolor=COLORS["alert"], boxstyle="round,pad=0.6")
                )
                ax.plot(
                    block_pos[0],
                    block_pos[1],
                    marker="X",
                    markersize=25,
                    color=COLORS["alert"],
                    markeredgecolor="white",
                    markeredgewidth=2,
                )
                plt.pause(1.0)

                status_box.set_text("RETORNANDO...")
                rastro.set_color(COLORS["alert"])

                path_percorrido = caminho[:limite_steps]
                path_volta = list(reversed(path_percorrido))
                start_back = block_pos
                end_back = np.array(self.pos[path_volta[0]])

                for s in range(15):
                    pos = start_back + (s / 15) * (end_back - start_back)
                    truck.set_data([pos[0]], [pos[1]])
                    plt.pause(0.01)

                for i in range(len(path_volta) - 1):
                    u_b, v_b = path_volta[i], path_volta[i + 1]
                    start, end = np.array(self.pos[u_b]), np.array(self.pos[v_b])
                    for s in range(15):
                        pos = start + (s / 15) * (end - start)
                        truck.set_data([pos[0]], [pos[1]])
                        plt.pause(0.01)
                rastro.set_color(COLORS["highlight"])
            else:
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
        fig, ax = plt.subplots(figsize=(16, 14), facecolor=COLORS["bg"])
        self._desenhar_base_luxo(ax, titulo, subtitle)
        plt.show()
