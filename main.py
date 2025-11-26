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
modo_chuva_ativo = False  # Controle global do botão


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


def animar_caminho(caminho, custo):
    global fig, ax_stats, custo_base
    # Desenha o estado inicial
    rede.desenhar_painel_analitico(ax_stats, 0, custo_base)
    fig.canvas.draw_idle()
    plt.pause(0.2)

    caminho_parcial = []
    velocidade_animacao = 0.3

    for i, node in enumerate(caminho):
        caminho_parcial.append(node)
        rede.desenhar_mapa_interativo(
            ax_map, arestas_bloqueadas, caminho, caminho_parcial=caminho_parcial
        )

        if i == len(caminho) - 1:
            rede.desenhar_painel_analitico(ax_stats, custo, custo_base)
            fig.canvas.manager.set_window_title(
                f"Soy Logistics AI (Entrega: R${custo:.2f})"
            )

        fig.canvas.draw_idle()
        plt.pause(velocidade_animacao)


def atualizar_dashboard():
    """
    Atualiza o dashboard considerando clima e bloqueios, sempre com animação se houver rota.
    """
    global rede, fig, ax_map, ax_stats, arestas_bloqueadas, custo_base, modo_chuva_ativo

    # 1. Aplica Clima (Reseta o grafo)
    rede.aplicar_condicoes_climaticas(modo_chuva_ativo)

    # 2. Re-aplica bloqueios manuais
    for u, v in arestas_bloqueadas:
        if rede.graph.has_edge(u, v):
            rede.graph.remove_edge(u, v)

    # 3. Busca Rota
    custo, caminho = rede.buscar_melhor_rota(ORIGEM, DESTINOS)
    if custo == float("inf"):
        custo = 0

    # 4. Desenha e Anima
    rede.desenhar_mapa_interativo(ax_map, arestas_bloqueadas, [])
    fig.canvas.draw_idle()

    if caminho:
        animar_caminho(caminho, custo)
    else:
        rede.desenhar_painel_analitico(ax_stats, 0, custo_base)
        ax_map.set_title(
            "ROTA IMPOSSÍVEL!", fontsize=14, color=COLORS["alert"], loc="left"
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
        atualizar_dashboard()


def toggle_weather(event):
    global modo_chuva_ativo
    modo_chuva_ativo = not modo_chuva_ativo
    btn_clima.label.set_text("CLIMA: ☀️" if not modo_chuva_ativo else "CLIMA: ⛈️")
    btn_clima.color = COLORS["node_hub"] if not modo_chuva_ativo else COLORS["rail"]
    btn_clima.hovercolor = "#1F618D" if not modo_chuva_ativo else "#374151"
    atualizar_dashboard()


def reset_all(event):
    global modo_chuva_ativo
    arestas_bloqueadas.clear()
    modo_chuva_ativo = False
    btn_clima.label.set_text("CLIMA: ☀️")
    btn_clima.color = COLORS["node_hub"]
    atualizar_dashboard()


def export_report(event):
    filename = f"report_{datetime.now().strftime('%H%M%S')}.pdf"
    plt.savefig(filename)
    print(f"Salvo: {filename}")


# Referência global para o botão
btn_clima = None


def main():
    global rede, fig, ax_map, ax_stats, custo_base, btn_clima
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
    fig.canvas.manager.set_window_title("Soy Logistics AI v7.0 (Operations Mode)")

    gs = GridSpec(1, 3, figure=fig, wspace=0.1)
    ax_map = fig.add_subplot(gs[0, :2])
    ax_stats = fig.add_subplot(gs[0, 2])

    # --- BOTÕES (Reposicionados agora que são apenas 3) ---

    # 1. Reset
    ax_btn1 = plt.axes([0.50, 0.05, 0.1, 0.06])
    btn1 = Button(ax_btn1, "RESET", color="white", hovercolor="#E5E7EB")
    btn1.on_clicked(reset_all)

    # 2. Clima (Central)
    ax_btn_clim = plt.axes([0.61, 0.05, 0.12, 0.06])
    btn_clima = Button(
        ax_btn_clim, "CLIMA: ☀️", color=COLORS["node_hub"], hovercolor="#1F618D"
    )
    btn_clima.label.set_color("white")
    btn_clima.label.set_fontweight("bold")
    btn_clima.on_clicked(toggle_weather)

    # 3. Export
    ax_btn2 = plt.axes([0.74, 0.05, 0.1, 0.06])
    btn2 = Button(ax_btn2, "PDF", color=COLORS["node_port"], hovercolor="#1F618D")
    btn2.label.set_color("white")
    btn2.on_clicked(export_report)

    fig.canvas.mpl_connect("button_press_event", on_click_map)

    fig._btn_ref = [btn1, btn2, btn_clima]

    atualizar_dashboard()
    print(
        ">>> SISTEMA PRONTO v7.0: Modo Operacional + Clima (Sem Risco Probabilístico) <<<"
    )
    plt.show(block=True)


if __name__ == "__main__":
    main()
