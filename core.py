# Arquivo: core.py

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.patheffects as pe
import numpy as np
import json
import os
import logging
import random
from typing import List, Tuple, Set, Dict
import copy

logger = logging.getLogger("LogisticsCore")
CUSTO_TRANSBORDO = 12.50

# --- DESIGN SYSTEM ---
COLORS = {
    "bg": "#F4F6F9",
    "road": "#95A5A6",
    "rail": "#2C3E50",
    "node_origin": "#E67E22",
    "node_port": "#2980B9",
    "node_hub": "#27AE60",
    "alert": "#EF4444",
    "text": "#1F2937",
    "highlight": "#F59E0B",
    "white": "#FFFFFF",
    "safe_fill": "#60A5FA",
    "risk_fill": "#F87171",  # Cores novas para o gráfico
}


class SoyLogisticsNet:
    def __init__(self):
        self.graph = nx.DiGraph()
        self._initial_graph = None
        self.pos = {}

    def carregar_dados(self, json_path: str):
        logger.info(f"Carregando dados: {json_path}")
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"{json_path} não encontrado.")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.pos = {k: tuple(v) for k, v in data["nodes"].items()}
        self.graph.clear()
        for edge in data["edges"]:
            self.graph.add_edge(
                edge["u"],
                edge["v"],
                weight=edge["weight"],
                distance=edge["distance"],
                label=edge["label"],
                info=edge["info"],
                type=edge["type"],
                failure_prob=edge.get("failure_prob", 0.0),
            )
        self._initial_graph = copy.deepcopy(self.graph)

    def _calcular_custo_manual(self, caminho: List[str]):
        if not self.graph:
            return 0
        custo = 0
        modal_ant = None
        for i in range(len(caminho) - 1):
            u, v = caminho[i], caminho[i + 1]
            dados = self.graph[u][v]
            custo += dados["weight"]
            modal_atual = dados.get("type", "road")
            if modal_ant and modal_ant != modal_atual:
                custo += CUSTO_TRANSBORDO
            modal_ant = modal_atual
        return custo

    def buscar_melhor_rota(self, origem: str, destinos: List[str], grafo_custom=None):
        G = grafo_custom if grafo_custom else self.graph
        melhor_custo = float("inf")
        melhor_caminho = []
        for destino in destinos:
            if destino not in G:
                continue
            try:
                if nx.has_path(G, origem, destino):
                    caminhos = nx.all_simple_paths(G, source=origem, target=destino)
                    for caminho in caminhos:
                        custo = self._calcular_custo_manual(caminho)
                        if custo < melhor_custo:
                            melhor_custo = custo
                            melhor_caminho = caminho
            except:
                pass
        return melhor_custo, melhor_caminho

    def executar_monte_carlo(
        self, origem: str, destinos: List[str], iteracoes: int = 500
    ):
        custos_simulados = []
        falhas_totais = 0
        logger.info(f"Iniciando Monte Carlo ({iteracoes} iterações)...")

        for _ in range(iteracoes):
            G_temp = copy.deepcopy(self._initial_graph)
            edges_to_remove = []
            for u, v, d in G_temp.edges(data=True):
                if random.random() < d.get("failure_prob", 0):
                    edges_to_remove.append((u, v))
            G_temp.remove_edges_from(edges_to_remove)

            # Truque para usar o custo manual com o grafo temporário
            bkp_graph = self.graph
            self.graph = G_temp
            custo, _ = self.buscar_melhor_rota(origem, destinos, grafo_custom=G_temp)
            self.graph = bkp_graph

            if custo == float("inf"):
                falhas_totais += 1
            else:
                custos_simulados.append(custo)

        return custos_simulados, falhas_totais

    def _find_closest_edge(self, x_click, y_click, tolerance=0.8):
        min_distance = float("inf")
        closest_edge = None
        for u, v in self._initial_graph.edges():
            if u not in self.pos or v not in self.pos:
                continue
            x1, y1 = self.pos[u]
            x2, y2 = self.pos[v]
            dx, dy = x2 - x1, y2 - y1
            if dx == 0 and dy == 0:
                continue
            t = max(
                0,
                min(
                    1, ((x_click - x1) * dx + (y_click - y1) * dy) / (dx * dx + dy * dy)
                ),
            )
            dist = np.sqrt(
                (x_click - (x1 + t * dx)) ** 2 + (y_click - (y1 + t * dy)) ** 2
            )
            if dist < min_distance:
                min_distance = dist
                closest_edge = (u, v)
        return closest_edge if min_distance < tolerance else None

    # --- RENDERIZAÇÃO LUXO (Mapa) ---
    def desenhar_mapa_interativo(self, ax, arestas_bloqueadas, melhor_caminho):
        ax.clear()
        ax.set_facecolor(COLORS["bg"])

        # Base
        road_edges = [
            (u, v)
            for u, v, d in self._initial_graph.edges(data=True)
            if d.get("type") == "road"
        ]
        nx.draw_networkx_edges(
            self._initial_graph,
            self.pos,
            edgelist=road_edges,
            edge_color=COLORS["road"],
            width=2,
            arrowsize=10,
            connectionstyle="arc3,rad=0.1",
            ax=ax,
        )
        rail_edges = [
            (u, v)
            for u, v, d in self._initial_graph.edges(data=True)
            if d.get("type") == "rail"
        ]
        nx.draw_networkx_edges(
            self._initial_graph,
            self.pos,
            edgelist=rail_edges,
            edge_color=COLORS["rail"],
            width=3,
            arrowsize=10,
            style="dashed",
            connectionstyle="arc3,rad=0.1",
            ax=ax,
        )

        # Labels
        edge_labels = {
            (u, v): f"{d['label']}\nR$ {d['weight']}"
            for u, v, d in self._initial_graph.edges(data=True)
        }
        nx.draw_networkx_edge_labels(
            self._initial_graph,
            self.pos,
            edge_labels=edge_labels,
            font_size=7,
            font_family="monospace",
            font_color="#333",
            bbox=dict(
                facecolor="white",
                edgecolor="#BDC3C7",
                boxstyle="round,pad=0.3",
                alpha=0.9,
            ),
            ax=ax,
        )

        # Nós
        nx.draw_networkx_nodes(
            self._initial_graph,
            self.pos,
            nodelist=["Sorriso_MT"],
            node_shape="D",
            node_size=3500,
            node_color=COLORS["node_origin"],
            ax=ax,
            edgecolors="white",
            linewidths=2,
        )
        portos = [
            n for n in self._initial_graph.nodes() if "Santos" in n or "Miritituba" in n
        ]
        nx.draw_networkx_nodes(
            self._initial_graph,
            self.pos,
            nodelist=portos,
            node_shape="s",
            node_size=2800,
            node_color=COLORS["node_port"],
            ax=ax,
            edgecolors="white",
            linewidths=2,
        )
        hubs = [
            n
            for n in self._initial_graph.nodes()
            if n not in portos and n != "Sorriso_MT"
        ]
        nx.draw_networkx_nodes(
            self._initial_graph,
            self.pos,
            nodelist=hubs,
            node_shape="o",
            node_size=1800,
            node_color=COLORS["node_hub"],
            ax=ax,
            edgecolors="white",
            linewidths=2,
        )

        # Textos
        labels_clean = {
            k: k.replace("_MT", "")
            .replace("_PA", "")
            .replace("_SP", "")
            .replace("_MG", "")
            for k in self.pos.keys()
        }
        pos_labels = {k: (v[0], v[1] - 0.5) for k, v in self.pos.items()}
        nx.draw_networkx_labels(
            self._initial_graph,
            pos_labels,
            labels=labels_clean,
            font_size=9,
            font_weight="bold",
            font_color=COLORS["text"],
            ax=ax,
        )

        # Bloqueios
        if arestas_bloqueadas:
            nx.draw_networkx_edges(
                self._initial_graph,
                self.pos,
                edgelist=list(arestas_bloqueadas),
                edge_color=COLORS["alert"],
                width=4,
                style="dotted",
                connectionstyle="arc3,rad=0.1",
                ax=ax,
            )
            for u, v in arestas_bloqueadas:
                if u in self.pos and v in self.pos:
                    mx, my = (np.array(self.pos[u]) + np.array(self.pos[v])) / 2
                    ax.text(
                        mx,
                        my,
                        "BLOQUEADO",
                        fontsize=8,
                        color="white",
                        fontweight="bold",
                        ha="center",
                        va="center",
                        zorder=12,
                        bbox=dict(facecolor=COLORS["alert"], edgecolor="none", pad=2),
                    )

        # Rota Ativa
        if melhor_caminho and len(melhor_caminho) > 1:
            path_edges = list(zip(melhor_caminho[:-1], melhor_caminho[1:]))
            nx.draw_networkx_edges(
                self.graph,
                self.pos,
                edgelist=path_edges,
                edge_color=COLORS["highlight"],
                width=5,
                connectionstyle="arc3,rad=0.1",
                ax=ax,
                alpha=0.8,
            )

        legend_elements = [
            mpatches.Patch(color=COLORS["node_origin"], label="Origem"),
            mpatches.Patch(color=COLORS["node_port"], label="Porto"),
            mlines.Line2D([], [], color=COLORS["road"], linestyle="-", label="Rodovia"),
            mlines.Line2D(
                [],
                [],
                color=COLORS["alert"],
                linewidth=3,
                linestyle=":",
                label="Bloqueio",
            ),
            mlines.Line2D(
                [], [], color=COLORS["highlight"], linewidth=3, label="Rota Ativa"
            ),
        ]
        ax.legend(
            handles=legend_elements,
            loc="upper right",
            fontsize=8,
            facecolor="white",
            framealpha=1,
        ).set_zorder(20)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_title(
            "MAPA OPERACIONAL",
            fontsize=12,
            fontweight="bold",
            color=COLORS["text"],
            loc="left",
        )

    # --- PAINEL ANALÍTICO (Atualizado: Mais Visual) ---
    def desenhar_painel_analitico(
        self, ax, custo_atual, custo_base, dados_monte_carlo=None
    ):
        ax.clear()
        ax.set_facecolor(COLORS["bg"])

        # === MODO 1: GRÁFICO DE RISCO (Clean & Clear) ===
        if dados_monte_carlo:
            custos, falhas = dados_monte_carlo
            if not custos:
                ax.text(
                    0.5, 0.5, "DADOS INSUFICIENTES", ha="center", color=COLORS["alert"]
                )
                return

            media = np.mean(custos)
            p95 = np.percentile(custos, 95)  # O "Pior Caso" realista

            # Histograma: Azul = Seguro, Vermelho = Cauda de Risco (acima de 95%)
            counts, bins, patches = ax.hist(
                custos, bins=20, density=True, alpha=0.7, edgecolor="white"
            )

            # Pintar as barras de risco
            for i in range(len(patches)):
                if bins[i] >= p95:
                    patches[i].set_facecolor(COLORS["risk_fill"])  # Vermelho Claro
                else:
                    patches[i].set_facecolor(COLORS["safe_fill"])  # Azul Claro

            # Linhas de Referência Verticais (Pontilhadas)
            ax.axvline(media, color=COLORS["text"], linestyle="--", linewidth=1.5)
            ax.axvline(p95, color=COLORS["alert"], linestyle="-", linewidth=2)

            # Anotações Diretas no Gráfico (Melhor que legenda)
            ylim = ax.get_ylim()[1]
            ax.text(
                media,
                ylim * 0.95,
                f" Média\n R${media:.0f}",
                color=COLORS["text"],
                ha="left",
                va="top",
                fontweight="bold",
                fontsize=9,
            )
            ax.text(
                p95,
                ylim * 0.75,
                f" ALTO RISCO\n > R${p95:.0f}",
                color=COLORS["alert"],
                ha="left",
                va="top",
                fontweight="bold",
                fontsize=9,
            )

            # Cartão de Resumo (Stats Box)
            stats_text = (
                f"SIMULAÇÕES: {len(custos)}\n"
                f"FALHAS TOTAIS: {falhas}\n"
                f"VARIAÇÃO: R${min(custos):.0f} - R${max(custos):.0f}"
            )
            ax.text(
                0.98,
                0.98,
                stats_text,
                transform=ax.transAxes,
                ha="right",
                va="top",
                fontsize=9,
                bbox=dict(
                    facecolor="white",
                    edgecolor="#E5E7EB",
                    boxstyle="round,pad=0.5",
                    alpha=0.9,
                ),
            )

            ax.set_title(
                "DISTRIBUIÇÃO DE RISCO (PROBABILIDADE)",
                fontsize=10,
                fontweight="bold",
                color=COLORS["text"],
                loc="left",
            )
            ax.set_xlabel(
                "Custo Final por Tonelada (R$)", fontsize=9, color=COLORS["text"]
            )

            # Limpeza extrema: Remove eixo Y e bordas
            ax.set_yticks([])
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_visible(False)

        # === MODO 2: COMPARAÇÃO SIMPLES ===
        else:
            labels = ["Meta (Ideal)", "Custo Real"]
            valores = [custo_base, custo_atual]
            cores = [
                COLORS["node_hub"],
                COLORS["node_port"] if custo_atual == custo_base else COLORS["alert"],
            ]

            y_pos = np.arange(len(labels))
            bars = ax.barh(y_pos, valores, height=0.5, color=cores)

            ax.set_yticks(y_pos)
            ax.set_yticklabels(
                labels, fontweight="bold", fontsize=10, color=COLORS["text"]
            )
            ax.set_xlim(0, max(800, custo_atual * 1.3))
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_visible(False)
            ax.spines["bottom"].set_color(COLORS["road"])

            for bar in bars:
                ax.text(
                    bar.get_width() + 10,
                    bar.get_y() + bar.get_height() / 2,
                    f"R$ {bar.get_width():.2f}",
                    va="center",
                    fontweight="bold",
                    color=COLORS["text"],
                    fontsize=11,
                )

            diff_pct = (
                ((custo_atual - custo_base) / custo_base) * 100 if custo_base > 0 else 0
            )
            msg = (
                "OPERAÇÃO NORMAL" if diff_pct == 0 else f"SOBREPREÇO: +{diff_pct:.0f}%"
            )
            cor_msg = COLORS["node_hub"] if diff_pct == 0 else COLORS["alert"]
            ax.text(
                0.5,
                0.85,
                msg,
                transform=ax.transAxes,
                ha="center",
                fontsize=14,
                fontweight="bold",
                color=cor_msg,
                bbox=dict(
                    facecolor="white",
                    edgecolor=cor_msg,
                    boxstyle="round,pad=0.6",
                    linewidth=2,
                ),
            )
            ax.set_title(
                "INDICADORES FINANCEIROS",
                fontsize=12,
                fontweight="bold",
                color=COLORS["text"],
                loc="left",
            )
