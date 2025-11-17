from core import SoyLogisticsNet, COLORS
import matplotlib.pyplot as plt


# --- FUNÇÕES AUXILIARES (As mesmas do main.py para consistência) ---
def filtrar_rota_por_inicio(todas_rotas, segundo_no):
    for item in todas_rotas:
        caminho = item["caminho"]
        if len(caminho) > 1 and caminho[1] == segundo_no:
            return item
    return None


def calcular_custo_com_falhas(rede, caminho_final, caminhos_falhos_anteriores):
    """
    Calcula o custo total somando a rota final + (ida e volta das falhas).
    """
    custo_desperdicio = 0

    # Soma o prejuízo das tentativas anteriores (Ida + Volta)
    for falha in caminhos_falhos_anteriores:
        u, v = falha["caminho"][0], falha["caminho"][1]
        peso = rede.graph[u][v]["weight"]
        custo_desperdicio += peso * 2  # Foi e voltou

    return caminho_final["custo"] + custo_desperdicio


def main():
    print("--- GERANDO DASHBOARD DE RESULTADOS (CUSTO REAL) ---")

    rede = SoyLogisticsNet()
    rede.construir_cenario_padrao()

    # 1. Mapeamento
    destinos = ["Miritituba_PA", "Santos_SP", "Santarem_PA"]
    todas_rotas = rede.obter_todas_rotas("Sorriso_MT", destinos)

    # 2. Seleção Inteligente (Mesma do main.py)
    rota_norte = filtrar_rota_por_inicio(todas_rotas, "Sinop_MT")  # R$ 180
    rota_sul = filtrar_rota_por_inicio(todas_rotas, "Cuiaba_MT")  # R$ 270
    rota_leste = filtrar_rota_por_inicio(todas_rotas, "Agua_Boa_MT")  # R$ 380
    rota_oeste = filtrar_rota_por_inicio(todas_rotas, "Campo_Novo_MT")  # R$ 390

    if not (rota_norte and rota_leste and rota_sul and rota_oeste):
        print("Erro: Rotas insuficientes.")
        return

    # 3. Definição dos Cenários e Cálculo do Custo Real
    # Custo Real = Rota Final + (Rotas Anteriores x 2)

    # Cenário 1: Só Norte (0 erros)
    custo_1 = rota_norte["custo"]

    # Cenário 2: Norte falhou -> Sul (1 erro)
    custo_2 = calcular_custo_com_falhas(rede, rota_sul, [rota_norte])

    # Cenário 3: Norte falhou -> Sul falhou -> Leste (2 erros)
    custo_3 = calcular_custo_com_falhas(rede, rota_leste, [rota_norte, rota_sul])

    # Cenário 4: Norte falhou -> Sul falhou -> Leste falhou -> Oeste (3 erros)
    custo_4 = calcular_custo_com_falhas(
        rede, rota_oeste, [rota_norte, rota_sul, rota_leste]
    )

    # Lista para plotagem
    cenarios_plot = [
        (rota_norte, f"1. MELHOR CENÁRIO", f"R$ {custo_1:.2f}/ton", "#27AE60"),
        (rota_sul, f"2. CONTINGÊNCIA (1 Falha)", f"R$ {custo_2:.2f}/ton", "#F1C40F"),
        (rota_leste, f"3. CRÍTICO (2 Falhas)", f"R$ {custo_3:.2f}/ton", "#E67E22"),
        (rota_oeste, f"4. PIOR CENÁRIO (Colapso)", f"R$ {custo_4:.2f}/ton", "#C0392B"),
    ]

    # 4. Configuração Visual (Grid 2x2)
    fig, axs = plt.subplots(2, 2, figsize=(18, 12), facecolor="#E5E8E8")
    fig.suptitle(
        "DASHBOARD FINANCEIRO: IMPACTO DAS FALHAS LOGÍSTICAS",
        fontsize=24,
        fontweight="bold",
        color="#2C3E50",
    )

    # Plota os 4 gráficos
    # Usamos um truque: passamos um dicionário falso com o 'custo' já somado (com erros)
    # para que a função core.py escreva o valor total no título.

    # Gráfico 1
    dados_fake_1 = {"caminho": rota_norte["caminho"], "custo": custo_1}
    rede.plotar_caminho_estatico_em_ax(
        axs[0, 0], dados_fake_1, cenarios_plot[0][1], cenarios_plot[0][3]
    )

    # Gráfico 2
    dados_fake_2 = {"caminho": rota_sul["caminho"], "custo": custo_2}  # Custo acumulado
    rede.plotar_caminho_estatico_em_ax(
        axs[0, 1], dados_fake_2, cenarios_plot[1][1], cenarios_plot[1][3]
    )

    # Gráfico 3
    dados_fake_3 = {"caminho": rota_leste["caminho"], "custo": custo_3}
    rede.plotar_caminho_estatico_em_ax(
        axs[1, 0], dados_fake_3, cenarios_plot[2][1], cenarios_plot[2][3]
    )

    # Gráfico 4
    dados_fake_4 = {"caminho": rota_oeste["caminho"], "custo": custo_4}
    rede.plotar_caminho_estatico_em_ax(
        axs[1, 1], dados_fake_4, cenarios_plot[3][1], cenarios_plot[3][3]
    )

    plt.tight_layout(rect=[0, 0.03, 1, 0.93])

    print("\n=== RESUMO EXECUTIVO ===")
    for i, (rota, tit, cust, cor) in enumerate(cenarios_plot):
        print(f"{tit}: {cust}")

    print("\n>>> Abrindo Dashboard Visual...")
    plt.show()


if __name__ == "__main__":
    main()
