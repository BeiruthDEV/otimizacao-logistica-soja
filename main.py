from core import SoyLogisticsNet


def main():
    print("--- SISTEMA DE OTIMIZAÇÃO LOGÍSTICA (AGRO V1.0) ---\n")

    # 1. Instanciação do Cenário Base
    rede = SoyLogisticsNet()
    rede.construir_cenario_padrao()

    hub_origem = "Sorriso_MT"
    portos = ["Miritituba_PA", "Santos_SP"]

    # 2. Análise do Cenário Normal
    # Plota o gráfico e calcula custos
    rede.visualizar("Cenário 1: Operação Normal (Arco Norte + Sul)")
    custo_normal = rede.buscar_melhor_rota(hub_origem, portos)

    print("\n" + "-" * 50)
    input("Pressione ENTER para simular a falha na BR-163...")

    # 3. Simulação de Robustez (Falha Crítica)
    # Remove a estrada entre Sinop e Miritituba
    rede_crise = rede.criar_cenario_falha("Sinop_MT", "Miritituba_PA")

    # 4. Análise do Cenário de Crise
    rede_crise.visualizar("Cenário 2: Bloqueio da BR-163 (Norte)")
    custo_crise = rede_crise.buscar_melhor_rota(hub_origem, portos)

    # 5. Relatório Final (KPIs)
    print("\n" + "=" * 30)
    print(" RELATÓRIO DE ROBUSTEZ")
    print("=" * 30)
    if custo_normal != float("inf") and custo_crise != float("inf"):
        delta = custo_crise - custo_normal
        percentual = (delta / custo_normal) * 100
        print(f"Custo Original: R$ {custo_normal:.2f}")
        print(f"Custo na Crise: R$ {custo_crise:.2f}")
        print(f"Impacto Financeiro: +{percentual:.1f}% no frete.")
        print("Conclusão: Alta dependência da rota Norte.")
    else:
        print("Sistema entrou em colapso total.")


if __name__ == "__main__":
    main()
