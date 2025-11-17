import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional
import copy


class SoyLogisticsNet:
    """
    Controlador da rede logística. Responsável pela topologia,
    cálculo de custos e simulações de falha.
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        # Layout fixo para plotagem (Geografia aproximada BR)
        self.pos = {
            "Miritituba_PA": (0, 6),
            "Sinop_MT": (0, 2),
            "Sorriso_MT": (0, 0),  # Hub Central
            "Cuiaba_MT": (0, -2),
            "Rondonopolis_MT": (0, -3.5),
            "Santos_SP": (2, -7),
        }

    def construir_cenario_padrao(self):
        """Inicializa os nós e arestas do cenário real."""
        rotas = [
            # (Origem, Destino, Custo, Nome da Via)
            ("Sorriso_MT", "Sinop_MT", 40, "BR-163"),
            ("Sinop_MT", "Miritituba_PA", 140, "BR-163 Norte"),
            ("Sorriso_MT", "Cuiaba_MT", 60, "BR-163 Sul"),
            ("Cuiaba_MT", "Rondonopolis_MT", 50, "BR-364"),
            ("Rondonopolis_MT", "Santos_SP", 160, "Ferronorte"),
        ]
        for u, v, w, l in rotas:
            self.graph.add_edge(u, v, weight=w, label=l)

    def _calcular_custo_manual(self, caminho: List[str]) -> Tuple[float, str]:
        """
        CORE DO ALGORITMO: Itera manualmente sobre o caminho para somar custos.
        Evita uso de funções prontas de 'shortest path' para fins acadêmicos.
        """
        custo_total = 0.0
        log_parts = []

        for i in range(len(caminho) - 1):
            u, v = caminho[i], caminho[i + 1]
            dados_aresta = self.graph[u][v]

            peso = dados_aresta["weight"]
            via = dados_aresta["label"]

            custo_total += peso
            log_parts.append(f"[{via}: {peso}]")

        log_formatado = " + ".join(log_parts)
        return custo_total, log_formatado

    def buscar_melhor_rota(self, origem: str, destinos: List[str]) -> float:
        """Avalia todas as rotas possíveis e retorna o menor custo encontrado."""
        melhor_custo = float("inf")
        melhor_caminho = None
        destino_escolhido = None

        print(f"\n{'='*10} ANÁLISE DE ROTAS A PARTIR DE {origem} {'='*10}")

        for destino in destinos:
            try:
                # Pega todos os caminhos possíveis (Topologia apenas)
                caminhos = list(
                    nx.all_simple_paths(self.graph, source=origem, target=destino)
                )

                if not caminhos:
                    print(f" [!] Sem conexão com {destino}")
                    continue

                for caminho in caminhos:
                    custo, log = self._calcular_custo_manual(caminho)
                    print(f" Rota p/ {destino}: {' -> '.join(caminho)}")
                    print(f"    Cálculo: {log} = R$ {custo}")

                    if custo < melhor_custo:
                        melhor_custo = custo
                        melhor_caminho = caminho
                        destino_escolhido = destino

            except nx.NodeNotFound:
                print(f" [Erro] Nó {origem} ou {destino} não existe.")
            except nx.NetworkXNoPath:
                print(f" [!] Caminho bloqueado para {destino}")

        if melhor_caminho:
            print(f"\n >>> MELHOR ESTRATÉGIA: Exportar via {destino_escolhido}")
            print(f" >>> Custo Mínimo: R$ {melhor_custo:.2f} / ton")
            return melhor_custo
        else:
            print("\n >>> CRÍTICO: Nenhuma rota de escoamento disponível!")
            return float("inf")

    def criar_cenario_falha(self, u: str, v: str):
        """Retorna uma NOVA instância da rede com a aresta removida."""
        nova_rede = copy.deepcopy(self)
        if nova_rede.graph.has_edge(u, v):
            nova_rede.graph.remove_edge(u, v)
            print(f"\n[SIMULAÇÃO] ALERTA: Aresta {u}->{v} rompeu!")
        return nova_rede

    def visualizar(self, titulo: str):
        plt.figure(figsize=(8, 8))
        # Nós
        nx.draw_networkx_nodes(
            self.graph, self.pos, node_size=2000, node_color="#3498db", edgecolors="k"
        )
        nx.draw_networkx_labels(
            self.graph, self.pos, font_size=8, font_weight="bold", font_color="white"
        )

        # Arestas
        nx.draw_networkx_edges(
            self.graph, self.pos, width=2, arrowsize=20, edge_color="#555555"
        )

        # Pesos (Labels das arestas)
        edge_labels = {
            (u, v): f"R${d['weight']}" for u, v, d in self.graph.edges(data=True)
        }
        nx.draw_networkx_edge_labels(
            self.graph, self.pos, edge_labels=edge_labels, font_color="red", font_size=9
        )

        plt.title(titulo, fontsize=12, fontweight="bold")
        plt.axis("off")
        plt.tight_layout()
        plt.show()
