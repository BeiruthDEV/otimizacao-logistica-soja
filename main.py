from core import SoyLogisticsNet
import matplotlib.pyplot as plt
import time


def filtrar_rota_por_inicio(todas_rotas, segundo_no):
    """
    Busca uma rota na lista que comece indo para uma cidade específica.
    Usado para forçar o caminhão a sair por Norte, Sul, Leste ou Oeste.
    """
    for item in todas_rotas:
        caminho = item["caminho"]
        if len(caminho) > 1 and caminho[1] == segundo_no:
            return item
    return None


def calcular_distancia_total(rede, caminho):
    """
    Soma os quilômetros de cada trecho da rota para exibir no terminal.
    """
    km_total = 0
    for u, v in zip(caminho[:-1], caminho[1:]):
        km_total += rede.graph[u][v]["distance"]
    return km_total


def calcular_custos_detalhados(rede, caminhos_tentados):
    """
    Calcula o custo real considerando a Logística Reversa.
    Se o caminhão tentou uma rota e falhou, ele gastou (Ida + Volta).
    """
    custo_desperdicio = 0
    km_desperdicio = 0

    # Itera sobre todas as tentativas FALHAS (todas menos a última)
    for caminho in caminhos_tentados[:-1]:
        # Pega o primeiro trecho da falha
        u, v = caminho[0], caminho[1]
        peso = rede.graph[u][v]["weight"]
        dist = rede.graph[u][v]["distance"]

        # Soma o prejuízo: Ida até o bloqueio + Volta até a base (x2)
        custo_desperdicio += peso * 2
        km_desperdicio += dist * 2

    # Calcula a rota de SUCESSO (A última da lista)
    rota_final = caminhos_tentados[-1]
    custo_final = 0
    km_final = 0

    for i in range(len(rota_final) - 1):
        u, v = rota_final[i], rota_final[i + 1]
        custo_final += rede.graph[u][v]["weight"]
        km_final += rede.graph[u][v]["distance"]

    return {
        "custo_rota": custo_final,
        "km_rota": km_final,
        "custo_erro": custo_desperdicio,
        "km_erro": km_desperdicio,
        "custo_total": custo_final + custo_desperdicio,  # Soma final
        "km_total": km_final + km_desperdicio,
    }


def main():
    print("\n")
    print("████████████████████████████████████████████████████████")
    print("█   AGRO LOGISTICS SYSTEM v11.0 - CUSTO REAL (REAL-LIFE)   █")
    print("████████████████████████████████████████████████████████")
    print("")

    # Inicializa a rede
    rede = SoyLogisticsNet()
    rede.construir_cenario_padrao()
    hub_origem = "Sorriso_MT"

    print(">>> [SISTEMA] Mapeando e classificando rotas (Custo x Distância)...")
    destinos = ["Miritituba_PA", "Santos_SP", "Santarem_PA"]
    # Obtém TODAS as rotas possíveis do grafo
    todas_rotas = rede.obter_todas_rotas(hub_origem, destinos)

    # Captura as 4 rotas principais por direção geográfica para garantir variedade visual
    rota_norte = filtrar_rota_por_inicio(todas_rotas, "Sinop_MT")  # R$ 180
    rota_sul = filtrar_rota_por_inicio(todas_rotas, "Cuiaba_MT")  # R$ 270
    rota_leste = filtrar_rota_por_inicio(todas_rotas, "Agua_Boa_MT")  # R$ 380
    rota_oeste = filtrar_rota_por_inicio(todas_rotas, "Campo_Novo_MT")  # R$ 390

    if not (rota_norte and rota_leste and rota_sul and rota_oeste):
        print("Erro: Rotas insuficientes.")
        return

    # Definição dos Cenários de Apresentação (Listas Acumulativas)
    cenarios = [
        {
            "lista": [rota_norte["caminho"]],
            "titulo": "1. MELHOR CENÁRIO",
            "desc": "Sucesso na primeira tentativa.",
        },
        {
            "lista": [rota_norte["caminho"], rota_sul["caminho"]],
            "titulo": "2. CENÁRIO MEDIANO (1 Erro)",
            "desc": "Falha no Norte -> Retorno -> Sucesso no Sul.",
        },
        {
            "lista": [
                rota_norte["caminho"],
                rota_sul["caminho"],
                rota_leste["caminho"],
            ],
            "titulo": "3. CENÁRIO CRÍTICO (2 Erros)",
            "desc": "Norte (X) -> Sul (X) -> Leste (OK).",
        },
        {
            "lista": [
                rota_norte["caminho"],
                rota_sul["caminho"],
                rota_leste["caminho"],
                rota_oeste["caminho"],
            ],
            "titulo": "4. PIOR CENÁRIO (Colapso)",
            "desc": "Três tentativas falhas antes do sucesso no Oeste.",
        },
    ]

    # Loop de Execução dos Cenários
    for i, cenario in enumerate(cenarios):
        # Calcula a matemática financeira do cenário
        dados = calcular_custos_detalhados(rede, cenario["lista"])

        # Imprime o relatório no terminal
        print(f"\n{'='*60}")
        print(f" {cenario['titulo']}")
        print(f"{'='*60}")
        print(f" ESTRATÉGIA: {cenario['desc']}")
        print(f"{'-'*60}")
        print(f" [+] Custo da Rota Final:      R$ {dados['custo_rota']:.2f}")

        if dados["custo_erro"] > 0:
            print(
                f" [!] Custo de Retorno (Erros): R$ {dados['custo_erro']:.2f}  <-- PREJUÍZO"
            )
            print(f" [!] Km Rodados em Vão:        {dados['km_erro']} km")

        print(f"{'-'*60}")
        print(f" 💰 CUSTO TOTAL REAL:          R$ {dados['custo_total']:.2f} / ton")
        print(f" 🚛 DISTÂNCIA TOTAL REAL:      {dados['km_total']} km")
        print(f"{'='*60}")

        input(f"\n>>> ENTER para rodar animação do Cenário {i+1}...")

        # Passa o título já com o valor total para aparecer no gráfico animado
        titulo_grafico = f"{cenario['titulo']} (Total: R${dados['custo_total']})"
        rede.animar_multiplas_tentativas(
            cenario["lista"], titulo_grafico, cenario["desc"]
        )

    print("\n--- SIMULAÇÃO CONCLUÍDA ---")


if __name__ == "__main__":
    main()
