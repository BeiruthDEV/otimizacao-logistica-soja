import unittest
import os
import json
from core import SoyLogisticsNet

# Cria um arquivo de dados temporário para o teste não depender do arquivo real
TEST_DATA_FILE = "dados_teste.json"


class TestLogisticaSoja(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Cria um cenário controlado antes dos testes."""
        dados_mock = {
            "meta": {"version": "test"},
            "nodes": {
                "A": [0, 0],
                "B": [1, 1],
                "C": [2, 2],
                "PORT_SANTOS": [3, 3],
                "PORT_INVALIDO": [4, 4],
            },
            "edges": [
                {
                    "u": "A",
                    "v": "B",
                    "weight": 100,
                    "distance": 100,
                    "label": "Road1",
                    "info": "OK",
                    "type": "road",
                },
                {
                    "u": "B",
                    "v": "PORT_SANTOS",
                    "weight": 50,
                    "distance": 50,
                    "label": "Rail1",
                    "info": "OK",
                    "type": "rail",
                },
                {
                    "u": "A",
                    "v": "C",
                    "weight": 200,
                    "distance": 200,
                    "label": "Road2",
                    "info": "Ruim",
                    "type": "road",
                },
                {
                    "u": "C",
                    "v": "PORT_INVALIDO",
                    "weight": 10,
                    "distance": 10,
                    "label": "Road3",
                    "info": "OK",
                    "type": "road",
                },
            ],
        }
        with open(TEST_DATA_FILE, "w") as f:
            json.dump(dados_mock, f)

    @classmethod
    def tearDownClass(cls):
        """Limpa a bagunça depois dos testes."""
        if os.path.exists(TEST_DATA_FILE):
            os.remove(TEST_DATA_FILE)

    def setUp(self):
        self.rede = SoyLogisticsNet()
        self.rede.carregar_dados(TEST_DATA_FILE)

    def test_carregamento_dados(self):
        """Testa se o JSON foi lido corretamente."""
        self.assertEqual(len(self.rede.graph.nodes), 5)
        self.assertTrue(self.rede.graph.has_edge("A", "B"))

    def test_calculo_custo_simples(self):
        """Testa a soma simples de uma rota rodoviária."""
        # A -> C -> PORT_INVALIDO = 200 + 10 = 210
        custo = self.rede._calcular_custo_manual(["A", "C", "PORT_INVALIDO"])
        self.assertEqual(custo, 210)

    def test_calculo_transbordo(self):
        """Testa se a taxa de transbordo é aplicada na mudança Road->Rail."""
        # A (Road) -> B (Rail) -> PORT_SANTOS
        # Custo esperado: 100 (Road) + 12.50 (Taxa) + 50 (Rail) = 162.50
        custo = self.rede._calcular_custo_manual(["A", "B", "PORT_SANTOS"])
        self.assertEqual(custo, 162.50)

    def test_melhor_rota(self):
        """Testa se o algoritmo escolhe o menor caminho."""
        # Caminho pelo B (com taxa 162.50) é melhor que pelo C (210) se destino fosse comparável
        # Vamos testar A -> PORT_SANTOS
        custo, caminho = self.rede.buscar_melhor_rota("A", ["PORT_SANTOS"])
        self.assertEqual(caminho, ["A", "B", "PORT_SANTOS"])
        self.assertEqual(custo, 162.50)

    def test_destino_inexistente(self):
        """Testa resiliência contra destinos que não estão no mapa."""
        custo, caminho = self.rede.buscar_melhor_rota("A", ["NARNIA"])
        self.assertEqual(custo, float("inf"))
        self.assertEqual(caminho, [])


if __name__ == "__main__":
    print(">>> EXECUTANDO SUÍTE DE TESTES AUTOMATIZADOS <<<")
    unittest.main()
