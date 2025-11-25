# Arquivo: main.py

import argparse
import logging
import sys
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Button
import copy
from core import SoyLogisticsNet, COLORS

DESTINOS = ["Miritituba_PA", "Santos_SP"]
ORIGEM = "Sorriso_MT"

rede = None
fig = None
ax_map = None
ax_stats = None
arestas_bloqueadas = set()
custo_base = 0.0


def setup_logging(debug_mode):
    logging.basicConfig(
        filename="simulacao.log",
        level=logging.INFO,
        filemode="w",
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger("").addHandler(console)


def atualizar_dashboard(monte_carlo=False):
    global rede, fig, ax_map, ax_stats, arestas_bloqueadas, custo_base

    # Reset e Aplica Bloqueios Manuais
    rede.graph = copy.deepcopy(rede._initial_graph)
    for u, v in arestas_bloqueadas:
        if rede.graph.has_edge(u, v):
            rede.graph.remove_edge(u, v)

    # Lógica Principal
    custo, caminho = rede.buscar_melhor_rota(ORIGEM, DESTINOS)
    if custo == float("inf"):
        custo = 0

    # Renderiza Mapa (Esquerda)
    rede.desenhar_mapa_interativo(ax_map, arestas_bloqueadas, caminho)

    # Renderiza Analítico (Direita) - Agora com opção Monte Carlo
    dados_mc = None
    if monte_carlo:
        logging.info("Rodando simulação de Monte Carlo...")
        dados_mc = rede.executar_monte_carlo(ORIGEM, DESTINOS)

    rede.desenhar_painel_analitico(
        ax_stats, custo, custo_base, dados_monte_carlo=dados_mc
    )
    fig.canvas.draw_idle()


def on_click_map(event):
    if event.inaxes != ax_map:
        return
    edge = rede._find_closest_edge(event.xdata, event.ydata)
    if edge:
        if edge in arestas_bloqueadas:
            arestas_bloqueadas.remove(edge)
        else:
            arestas_bloqueadas.add(edge)
        atualizar_dashboard(monte_carlo=False)  # Volta para vista normal ao editar


def run_risk_analysis(event):
    # Roda com Monte Carlo ativado
    atualizar_dashboard(monte_carlo=True)


def reset_all(event):
    arestas_bloqueadas.clear()
    atualizar_dashboard(monte_carlo=False)


def export_report(event):
    filename = f"report_{datetime.now().strftime('%H%M%S')}.pdf"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    logging.info(f"Exportado: {filename}")
    ax_map.set_title(f"SALVO: {filename}", color=COLORS["node_hub"])
    fig.canvas.draw()
    plt.pause(0.5)
    ax_map.set_title("MAPA OPERACIONAL", color=COLORS["text"])
    fig.canvas.draw()


def main():
    global rede, fig, ax_map, ax_stats, custo_base
    setup_logging(False)

    try:
        rede = SoyLogisticsNet()
        rede.carregar_dados("dados.json")
    except Exception as e:
        print(f"Erro: {e}")
        return

    custo_base, _ = rede.buscar_melhor_rota(ORIGEM, DESTINOS)

    plt.ion()
    fig = plt.figure(figsize=(16, 9), facecolor=COLORS["bg"])
    fig.canvas.manager.set_window_title("Soy Logistics AI v6.0 (Stochastic)")

    gs = GridSpec(1, 3, figure=fig, wspace=0.1)
    ax_map = fig.add_subplot(gs[0, :2])
    ax_stats = fig.add_subplot(gs[0, 2])

    # Botões
    # Reset
    ax_btn1 = plt.axes([0.55, 0.05, 0.1, 0.06])
    btn1 = Button(ax_btn1, "RESET", color="white", hovercolor="#E5E7EB")
    btn1.label.set_fontweight("bold")
    btn1.on_clicked(reset_all)

    # Export
    ax_btn2 = plt.axes([0.66, 0.05, 0.1, 0.06])
    btn2 = Button(ax_btn2, "PDF", color=COLORS["node_port"], hovercolor="#1F618D")
    btn2.label.set_fontweight("bold")
    btn2.label.set_color("white")
    btn2.on_clicked(export_report)

    # --- NOVO BOTÃO: ANÁLISE DE RISCO ---
    ax_btn3 = plt.axes([0.77, 0.05, 0.15, 0.06])
    btn3 = Button(
        ax_btn3, "ANALISAR RISCO 🎲", color=COLORS["alert"], hovercolor="#C0392B"
    )
    btn3.label.set_fontweight("bold")
    btn3.label.set_color("white")
    btn3.on_clicked(run_risk_analysis)

    fig.canvas.mpl_connect("button_press_event", on_click_map)
    fig._btn_ref = [btn1, btn2, btn3]

    atualizar_dashboard()
    print(
        ">>> SISTEMA PRONTO: Clique em 'ANALISAR RISCO' para simulação estocástica <<<"
    )
    plt.show(block=True)


if __name__ == "__main__":
    main()
