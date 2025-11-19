// 1. Gerenciamento de Abas (com persistência e carregamento de gráficos)
function showView(viewId, clickedButton) {
    // Esconde tudo
    document.querySelectorAll('.view-content').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.menu-item').forEach(el => el.classList.remove('active'));

    // Mostra o selecionado
    const target = document.getElementById(viewId);
    if (target) target.style.display = 'block';

    // Ativa botão
    if (clickedButton) {
        clickedButton.classList.add('active');
    } else {
        // Tenta achar o botão automaticamente se vier de um refresh
        const autoBtn = document.querySelector(`button[onclick*="${viewId}"]`);
        if (autoBtn) autoBtn.classList.add('active');
    }

    // Se for a aba do Dashboard (view-5), renderiza o gráfico
    if (viewId === 'view-5') {
        renderChart();
    }

    // Inicia animação de terminal se for uma das abas de vídeo
    if (viewId.includes('view-') && viewId !== 'view-0' && viewId !== 'view-5') {
        const scenarioId = viewId.split('-')[1];
        runTerminalEffect(scenarioId);
    }

    localStorage.setItem('lastView', viewId);
}

// 2. Gráfico ApexCharts (O "Wow Factor")
let chartInstance = null;

function renderChart() {
    if (chartInstance) return; // Já renderizou para não duplicar

    var options = {
        series: [{
            name: 'Custo por Tonelada (R$)',
            data: [180, 350, 580, 770]
        }],
        chart: {
            type: 'bar', // Padrão inicial
            height: 350,
            fontFamily: 'Inter, sans-serif',
            toolbar: { show: false },
            animations: { enabled: true, easing: 'easeinout', speed: 800 }
        },
        plotOptions: {
            bar: {
                borderRadius: 8,
                columnWidth: '50%',
                distributed: true, // Cores diferentes por barra
            }
        },
        colors: ['#22c55e', '#eab308', '#f97316', '#dc2626'], // Verde, Amarelo, Laranja, Vermelho
        dataLabels: {
            enabled: true,
            formatter: function (val) { return "R$ " + val; },
            style: { fontSize: '14px', colors: ["#334155"] },
            offsetY: -20
        },
        xaxis: {
            categories: ['1. Ideal (Norte)', '2. Contingência (Sul)', '3. Crítico (Leste)', '4. Colapso (Oeste)'],
            labels: { style: { fontSize: '12px', fontWeight: 600 } }
        },
        yaxis: {
            title: { text: 'Custo (R$)' }
        },
        grid: {
            borderColor: '#f1f5f9',
            strokeDashArray: 4,
        },
        tooltip: {
            theme: 'dark',
            y: { formatter: function (val) { return "R$ " + val + " / ton" } }
        }
    };

    chartInstance = new ApexCharts(document.querySelector("#chart-container"), options);
    chartInstance.render();

    // Adiciona o listener para o seletor de tipo de gráfico
    const selector = document.getElementById('chartTypeSelector');
    if (selector) {
        selector.addEventListener('change', function (e) {
            updateChartType(e.target.value);
        });
    }
}

// Função para trocar entre Barra e Radar
function updateChartType(type) {
    if (!chartInstance) return;

    chartInstance.updateOptions({
        chart: {
            type: type
        },
        // Ajustes específicos para ficar bonito no Radar também
        plotOptions: {
            bar: { distributed: type === 'bar' }
        },
        xaxis: {
            labels: { show: true } // Garante labels
        }
    });
}

// 3. Efeito de Digitação no Terminal (Hacker Style)
const logs = {
    '1': ["> INICIANDO SISTEMA...", "> Rota Norte: DETECTADA", "> Verificando Clima... OK", "> Status BR-163: LIVRE", "> Calculando Frete... R$ 180", "[SUCESSO] Entrega Confirmada."],
    '2': ["> INICIANDO SISTEMA...", "> Rota Norte: FALHA (Bloqueio)", "! ALERTA: Chuvas Intensas", "> Redirecionando p/ SUL...", "> Custo Adicional: +50%", "[ATENÇÃO] Entrega com Atraso."],
    '3': ["> INICIANDO SISTEMA...", "! FALHA CRÍTICA: Norte (X)", "! FALHA CRÍTICA: Sul (X)", "> Buscando Rotas Alternativas...", "> Rota Leste (Terra): ATIVA", "[PERIGO] Dano ao Veículo Alto."],
    '4': ["! SYSTEM FAILURE !", "! Rota Norte: BLOCKED", "! Rota Sul: BLOCKED", "! Rota Leste: BLOCKED", ">>> ATIVANDO ROTA DE FUGA OESTE", ">>> Custo: EXORBITANTE", "[COLAPSO] Logística Reversa x3"]
};

function runTerminalEffect(id) {
    const container = document.getElementById(`terminal-${id}`);
    if (!container || container.dataset.typed === "true") return; // Já digitou

    container.innerHTML = ''; // Limpa
    const lines = logs[id];
    let i = 0;

    function typeLine() {
        if (i < lines.length) {
            const p = document.createElement('div');
            p.textContent = lines[i];
            p.className = "opacity-0 transition-opacity duration-300"; // Fade in
            container.appendChild(p);

            // Força reflow para animação funcionar
            setTimeout(() => p.classList.remove('opacity-0'), 50);

            i++;
            setTimeout(typeLine, 600); // Velocidade da digitação
        } else {
            container.dataset.typed = "true"; // Marca como feito
        }
    }
    typeLine();
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    const last = localStorage.getItem('lastView') || 'view-0';
    showView(last);
});