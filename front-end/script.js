// 1. Gerenciamento de Abas
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
        // Tenta achar o botão automaticamente (ex: refresh)
        const autoBtn = document.querySelector(`button[onclick*="${viewId}"]`);
        if (autoBtn) autoBtn.classList.add('active');
    }

    // Se for a aba do Dashboard (view-5), renderiza o gráfico
    if (viewId === 'view-5') {
        renderChart();
    }

    localStorage.setItem('lastView', viewId);
}

// 2. Gráfico ApexCharts (Matriz Comparativa)
let chartInstance = null;

function renderChart() {
    if (chartInstance) return;

    var options = {
        series: [{
            name: 'Custo por Tonelada (R$)',
            data: [180, 350, 580, 770]
        }],
        chart: {
            type: 'bar',
            height: '100%',
            fontFamily: 'Inter, sans-serif',
            toolbar: { show: false },
            animations: { enabled: true, easing: 'easeinout', speed: 800 }
        },
        plotOptions: {
            bar: {
                borderRadius: 6,
                columnWidth: '40%',
                distributed: true,
            }
        },
        colors: ['#10B981', '#EAB308', '#F97316', '#EF4444'], // Cores alinhadas com o Python (Verde, Amarelo, Laranja, Vermelho)
        dataLabels: {
            enabled: true,
            formatter: function (val) { return "R$ " + val; },
            style: { fontSize: '14px', colors: ["#334155"], fontWeight: 'bold' },
            offsetY: -20
        },
        xaxis: {
            categories: ['1. Ideal', '2. Contingência', '3. Crítico', '4. Colapso'],
            labels: { style: { fontSize: '12px', fontWeight: 600, colors: '#64748B' } },
            axisBorder: { show: false },
            axisTicks: { show: false }
        },
        yaxis: {
            title: { text: 'Custo (R$)' },
            labels: { style: { colors: '#64748B' } }
        },
        grid: {
            borderColor: '#F1F5F9',
            strokeDashArray: 4,
        },
        tooltip: {
            theme: 'dark',
            y: { formatter: function (val) { return "R$ " + val + " / ton" } }
        },
        legend: { show: false }
    };

    chartInstance = new ApexCharts(document.querySelector("#chart-container"), options);
    chartInstance.render();

    const selector = document.getElementById('chartTypeSelector');
    if (selector) {
        selector.addEventListener('change', function (e) {
            updateChartType(e.target.value);
        });
    }
}

function updateChartType(type) {
    if (!chartInstance) return;
    chartInstance.updateOptions({
        chart: { type: type },
        plotOptions: { bar: { distributed: type === 'bar' } },
        xaxis: { labels: { show: true } }
    });
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    const last = localStorage.getItem('lastView') || 'view-0';
    showView(last);
});