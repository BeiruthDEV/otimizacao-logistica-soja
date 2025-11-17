<p align="center">
  <img src="assets/logo-vassouras.png" alt="Universidade de Vassouras" width="400"/>
</p>

<h3 align="center">
  Universidade de Vassouras  
</h3>

---

### 📚 Curso: **Engenharia de Software**  
### 🖥️ Disciplina: **Analise Complexidade de Algoritmos**  
### 👨‍🎓 Autor: **Matheus Beiruth**

---





# Otimização Logística: Escoamento de Soja (MT) 🚛 🇧🇷

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![NetworkX](https://img.shields.io/badge/Library-NetworkX-green)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

> Uma abordagem baseada em Teoria dos Grafos para análise de robustez e custos na malha logística do agronegócio brasileiro.

## 📖 Sobre o Projeto

Este projeto modela a rede de distribuição de soja partindo de **Sorriso (MT)** — o maior produtor nacional — com destino aos portos de exportação. O objetivo é solucionar um problema clássico de Pesquisa Operacional: a escolha entre o **Arco Norte (Porto de Miritituba)** e o **Corredor Sul (Porto de Santos)**.

Diferente de implementações genéricas, este software simula cenários de **falha na infraestrutura crítica** (ex: bloqueio da BR-163), quantificando o impacto financeiro da falta de redundância na malha rodoviária brasileira.

### 🎯 Objetivos Técnicos
* **Modelagem de Grafo Direcionado (Digraph):** Representação de cidades como vértices e rodovias como arestas ponderadas.
* **Algoritmo de Caminho Mínimo Customizado:** Implementação manual da lógica de busca e acumulação de custos (sem dependência de "caixa preta" como `dijkstra` pronto), iterando sobre todas as rotas simples.
* **Análise de Robustez (Resiliência):** Simulação de remoção de arestas críticas em tempo de execução para avaliar o comportamento da rede sob estresse.

---

## 🗺️ Cenários Analisados

O sistema avalia dois cenários principais:

1.  **Cenário Nominal (Blue Sky):** Todas as rodovias (BR-163 Norte/Sul, BR-364, Ferronorte) estão operacionais. O algoritmo busca o menor custo por tonelada.
2.  **Cenário de Contingência (Falha Crítica):** Simulação de colapso na rodovia **BR-163 (Trecho Sinop-Miritituba)**. O sistema recalcula a rota viável e apresenta o delta de custo (prejuízo logístico).

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Core:** `NetworkX` (Estrutura de dados de grafos)
* **Visualização:** `Matplotlib` (Plotagem da rede geográfica)
* **Paradigma:** Programação Orientada a Objetos (POO)

---

## 🚀 Instalação e Execução

Siga os passos abaixo para rodar o projeto em seu ambiente local.

### Pré-requisitos
Certifique-se de ter o **Python 3.8+** e o **pip** instalados.

### 1. Clonar o repositório
```bash
git clone [https://github.com/BeiruthDEV/otimizacao-logistica-soja.git](https://github.com/BeiruthDEV/otimizacao-logistica-soja.git)
cd otimizacao-logistica-soja
```


```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

```bash
pip install networkx matplotlib
```

📊 Visualização dos Resultados
Ao executar o script, o software gerará:

Logs no Console: Detalhamento passo a passo do cálculo de custo de cada rota (Cálculo manual: Aresta A + Aresta B...).

Gráficos (Plot): Janelas interativas mostrando a topologia da rede antes e depois da falha simulada.

🧠 Arquitetura do Código
O projeto está estruturado na classe SoyLogisticsNet, que encapsula:

construir_cenario_padrao(): Definição dos vértices e arestas.

_calcular_custo_caminho(): Método protegido que realiza a aritmética de custos (Core da lógica).

simular_falha(): Método que retorna uma nova instância da rede (Deep Copy) com a aresta removida, preservando a integridade dos dados originais.

📝 Licença
Distribuído sob a licença MIT. Veja LICENSE para mais informações.

Desenvolvido para a disciplina de Algoritmos e Grafos.