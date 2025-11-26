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
    "road_safe": "#95A5A6",  # Cinza
    "road_warn": "#F59E0B",  # Laranja
    "road_danger": "#EF4444",  # Vermelho
    "rail": "#2C3E50",  # Azul Escuro
    "node_origin": "#E67E22",
    "node_port": "#2980B9",
    "node_hub": "#27AE60",
    "alert": "#EF4444",
    "text": "#1F2937",
    "highlight": "#10B981",  # Verde Esmeralda (Rota)
    "white": "#FFFFFF",
    "safe_fill": "#60A5FA",
    "risk_fill": "#F87171",
}


class SoyLogisticsNet:
    def __init__(self):
        self.graph = nx.DiGraph()
        self._initial_graph = None
        self.pos = {}
        self.modo_chuva = False  # Estado do clima

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

    def aplicar_condicoes_climaticas(self, chuva_intensa: bool):
        """
        Reconstroi o grafo aplicando penalidades de chuva se necessário.
        """
        self.modo_chuva = chuva_intensa
        # Reset para o estado original (limpo)
        self.graph = copy.deepcopy(self._initial_graph)

        if chuva_intensa:
            logger.warning("CLIMA: Aplicando penalidades de Chuva Intensa!")
            for u, v, d in self.graph.edges(data=True):
                # Penalidade apenas para Rodovias
                if d.get("type") == "road":
                    # Penalidade Leve (Estradas normais ficam mais lentas)
                    d["weight"] *= 1.1

                    # Penalidade Severa (Estradas de terra/precárias)
                    if d.get("info") in [
                        "Não Pavimentada",
                        "Precária",
                        "Rota de Fuga",
                        "Logística Crítica",
                    ]:
                        d["weight"] *= 1.6  # Custo sobe 60%
                        d["failure_prob"] = min(
                            0.95, d.get("failure_prob", 0) * 2.5
                        )  # Risco mais que dobra!
                        d["label"] += " (LAMA)"

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

    def _find_closest_edge(self, x_click, y_click, tolerance=0.8):
        min_distance = float("inf")
        closest_edge = None
        for u, v in self.graph.edges():  # Usa self.graph para pegar o estado atual
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

    # --- RENDERIZAÇÃO ---
    def desenhar_mapa_interativo(
        self, ax, arestas_bloqueadas, melhor_caminho, caminho_parcial=None
    ):
        ax.clear()

        # Mudança visual sutil no fundo se estiver chovendo
        ax.set_facecolor("#E5E7EB" if self.modo_chuva else COLORS["bg"])

        caminho_visual = (
            caminho_parcial if caminho_parcial is not None else melhor_caminho
        )

        # 1. Ferrovias
        rail_edges = [
            (u, v) for u, v, d in self.graph.edges(data=True) if d.get("type") == "rail"
        ]
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

        # 2. Rodovias com Heatmap Dinâmico
        road_edges = []
        road_colors = []
        for u, v, d in self.graph.edges(data=True):
            if d.get("type") == "road":
                road_edges.append((u, v))
                prob = d.get("failure_prob", 0.0)
                # Escala de risco ajustada
                if prob >= 0.20:
                    road_colors.append(COLORS["road_danger"])
                elif prob >= 0.06:
                    road_colors.append(COLORS["road_warn"])
                else:
                    road_colors.append(COLORS["road_safe"])

        nx.draw_networkx_edges(
            self.graph,
            self.pos,
            edgelist=road_edges,
            edge_color=road_colors,
            width=2,
            arrowsize=10,
            connectionstyle="arc3,rad=0.1",
            ax=ax,
        )

        # Labels
        edge_labels = {
            (u, v): f"{d['label']}\nR$ {d['weight']:.0f}"
            for u, v, d in self.graph.edges(data=True)
        }
        nx.draw_networkx_edge_labels(
            self.graph,
            self.pos,
            edge_labels=edge_labels,
            font_size=6,
            font_family="monospace",
            font_color="#333",
            bbox=dict(
                facecolor="white",
                edgecolor="#BDC3C7",
                boxstyle="round,pad=0.2",
                alpha=0.8,
            ),
            ax=ax,
        )

        # Nós
        nx.draw_networkx_nodes(
            self.graph,
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
            n
            for n in self.graph.nodes()
            if "Santos" in n or "Miritituba" in n or "Santarem" in n
        ]
        nx.draw_networkx_nodes(
            self.graph,
            self.pos,
            nodelist=portos,
            node_shape="s",
            node_size=2800,
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
            node_size=1800,
            node_color=COLORS["node_hub"],
            ax=ax,
            edgecolors="white",
            linewidths=2,
        )

        # Texto Cidades
        labels_clean = {
            k: k.replace("_MT", "")
            .replace("_PA", "")
            .replace("_SP", "")
            .replace("_MG", "")
            for k in self.pos.keys()
        }
        pos_labels = {k: (v[0], v[1] - 0.5) for k, v in self.pos.items()}
        nx.draw_networkx_labels(
            self.graph,
            pos_labels,
            labels=labels_clean,
            font_size=9,
            font_weight="bold",
            font_color=COLORS["text"],
            ax=ax,
        )

        # Bloqueios Manuais
        if arestas_bloqueadas:
            nx.draw_networkx_edges(
                self.graph,
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
        if caminho_visual and len(caminho_visual) > 1:
            path_edges = list(zip(caminho_visual[:-1], caminho_visual[1:]))
            nx.draw_networkx_edges(
                self.graph,
                self.pos,
                edgelist=path_edges,
                edge_color=COLORS["highlight"],
                width=5,
                connectionstyle="arc3,rad=0.1",
                ax=ax,
                alpha=0.9,
            )

        # Veículo (Z-Order corrigido)
        if caminho_visual and len(caminho_visual) > 0:
            current_node = caminho_visual[-1]
            if current_node in self.pos:
                vn = nx.draw_networkx_nodes(
                    self.graph,
                    self.pos,
                    nodelist=[current_node],
                    node_shape="h",
                    node_size=1200,
                    node_color=COLORS["highlight"],
                    ax=ax,
                    edgecolors="white",
                    linewidths=2,
                )
                vn.set_zorder(15)

        # Legenda
        legend_elements = [
            mpatches.Patch(color=COLORS["node_origin"], label="Origem"),
            mpatches.Patch(color=COLORS["node_port"], label="Porto"),
            mlines.Line2D([], [], color=COLORS["road_safe"], label="Rodovia (Segura)"),
            mlines.Line2D([], [], color=COLORS["road_warn"], label="Risco Médio"),
            mlines.Line2D([], [], color=COLORS["road_danger"], label="Alto Risco"),
            mlines.Line2D(
                [], [], color=COLORS["rail"], linestyle="--", label="Ferrovia"
            ),
            mlines.Line2D(
                [],
                [],
                color=COLORS["alert"],
                linewidth=3,
                linestyle=":",
                label="Bloqueio",
            ),
            mlines.Line2D(
                [0],
                [0],
                marker="h",
                color="w",
                markerfacecolor=COLORS["highlight"],
                markersize=10,
                label="Veículo",
            ),
        ]
        ax.legend(
            handles=legend_elements,
            loc="upper right",
            fontsize=7,
            facecolor="white",
            framealpha=0.9,
        ).set_zorder(20)

        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Título Dinâmico
        titulo = "MAPA OPERACIONAL (CONDIÇÕES NORMAIS)"
        cor_titulo = COLORS["text"]
        if self.modo_chuva:
            titulo = "⚠️ ALERTA: CHUVAS INTENSAS E ESTRADAS DE TERRA"
            cor_titulo = COLORS["alert"]

        ax.set_title(
            titulo, fontsize=12, fontweight="bold", color=cor_titulo, loc="left"
        )

    # --- PAINEL ANALÍTICO (Simplificado: Apenas Barra de Custo) ---
    def desenhar_painel_analitico(self, ax, custo_atual, custo_base):
        ax.clear()
        ax.set_facecolor(COLORS["bg"])

        labels = ["Meta", "Real"]
        valores = [custo_base, custo_atual]
        cores = [
            COLORS["node_hub"],
            COLORS["node_port"] if custo_atual <= custo_base * 1.1 else COLORS["alert"],
        ]
        y_pos = np.arange(len(labels))

        bars = ax.barh(y_pos, valores, height=0.5, color=cores)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontweight="bold", fontsize=10, color=COLORS["text"])

        # Ajuste de escala do eixo X
        max_val = (
            max(custo_base, custo_atual)
            if custo_atual > 0
            else (custo_base if custo_base > 0 else 100)
        )
        ax.set_xlim(0, max(800, max_val * 1.3))

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_color(COLORS["road_safe"])

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

        diff = custo_atual - custo_base
        diff_pct = (diff / custo_base * 100) if custo_base > 0 else 0
        if custo_atual == 0:
            msg, cor = "ROTA BLOQUEADA", COLORS["alert"]
        elif diff <= 0:
            msg, cor = "OPERAÇÃO NORMAL", COLORS["node_hub"]
        else:
            msg, cor = f"AUMENTO: +{diff_pct:.0f}%", COLORS["alert"]

        ax.text(
            0.5,
            0.85,
            msg,
            transform=ax.transAxes,
            ha="center",
            fontsize=14,
            fontweight="bold",
            color=cor,
            bbox=dict(
                facecolor="white", edgecolor=cor, boxstyle="round,pad=0.6", linewidth=2
            ),
        )
        ax.set_title(
            "INDICADORES FINANCEIROS",
            fontsize=12,
            fontweight="bold",
            color=COLORS["text"],
            loc="left",
        )
