let mainChartInstance = null;
let rawData = null;
let currentTab = 'equity';
let currentFilter = 'all';

document.addEventListener('DOMContentLoaded', () => {
    fetchDashboardData();
    setupEventListeners();
});

function setupEventListeners() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentTab = e.target.dataset.tab;
            renderChart();
        });
    });

    document.querySelectorAll('.filter-tag').forEach(tag => {
        tag.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-tag').forEach(t => t.classList.remove('active'));
            e.target.classList.add('active');
            currentFilter = e.target.dataset.filter;
            renderSignalsTable();
        });
    });

    const runBtn = document.getElementById('run-pipeline-btn');
    if (runBtn) {
        runBtn.addEventListener('click', async () => {
            const btnIcon = runBtn.querySelector('.btn-icon');
            const btnText = runBtn.querySelector('.btn-text');

            runBtn.disabled = true;
            if (btnIcon) btnIcon.classList.add('spinning');
            if (btnText) btnText.innerText = "Berechnung läuft...";
            showToast("⏳ Pipeline-Neuberechnung gestartet... Daten & TabFM Modell werden verarbeitet.", "info", 0);

            try {
                const res = await fetch('/api/run-analysis', { method: 'POST' });
                if (!res.ok) throw new Error("Fehler bei Serverberechnung");
                
                await fetchDashboardData();
                showToast("✅ Berechnung erfolgreich abgeschlossen! Dashboard-Ergebnisse aktualisiert.", "success", 5000);
            } catch (err) {
                console.error("Pipeline trigger failed:", err);
                showToast("⚠️ Server-Neuberechnung nicht erreichbar. Nutze verfügbare Daten.", "error", 5000);
                await fetchDashboardData();
            } finally {
                if (btnIcon) btnIcon.classList.remove('spinning');
                if (btnText) btnText.innerText = "Berechnung neu starten";
                runBtn.disabled = false;
            }
        });
    }
}

function showToast(message, type = 'info', durationMs = 4000) {
    const toast = document.getElementById('toast-banner');
    if (!toast) return;
    
    toast.className = `toast-banner ${type}`;
    toast.innerHTML = message;

    if (durationMs > 0) {
        setTimeout(() => {
            if (toast.innerHTML === message) {
                toast.className = 'toast-banner hidden';
            }
        }, durationMs);
    }
}

async function fetchDashboardData() {
    const endpoints = [
        '/api/dashboard-data',
        './backtest_dashboard_data.json',
        '../data_store/backtest_dashboard_data.json'
    ];

    rawData = null;
    let lastError = null;

    for (const url of endpoints) {
        try {
            const res = await fetch(url);
            if (res.ok) {
                rawData = await res.json();
                console.log(`[Dashboard] Successfully loaded data from: ${url}`);
                break;
            }
        } catch (err) {
            lastError = err;
        }
    }

    if (!rawData || !rawData.summary || !rawData.tsla_chart_data) {
        console.error("Failed to load dashboard data from all endpoints", lastError);
        showToast("❌ Fehler: Dashboard-Daten konnten nicht geladen werden. Bitte starten Sie 'python web/server.py' oder 'python run_analysis.py'.", "error", 0);
        return;
    }

    renderSummaryMetrics();
    renderAblationTable();
    renderChart();
    renderSignalsTable();
}

function renderSummaryMetrics() {
    if (!rawData || !rawData.summary || rawData.summary.length === 0) return;

    const bestExpName = rawData.best_experiment;
    const bestSummary = rawData.summary.find(s => s.experiment === bestExpName) || rawData.summary[0];

    const retElem = document.getElementById('metric-return');
    if (retElem) {
        const val = bestSummary.total_return || 0;
        retElem.innerText = `${val >= 0 ? '+' : ''}${val.toFixed(1)}%`;
        retElem.className = `metric-value ${val >= 0 ? 'positive' : 'negative'}`;
    }

    const vsBh = document.getElementById('metric-vs-buyhold');
    if (vsBh) {
        const bhVal = bestSummary.buy_hold_return || 0;
        vsBh.innerText = `vs Buy & Hold: ${bhVal >= 0 ? '+' : ''}${bhVal.toFixed(1)}%`;
    }

    const wrElem = document.getElementById('metric-winrate');
    if (wrElem) wrElem.innerText = `${(bestSummary.win_rate || 0).toFixed(1)}%`;

    const tradesElem = document.getElementById('metric-trades');
    if (tradesElem) tradesElem.innerText = `${bestSummary.n_trades || 0} Signals executed`;

    const sharpeElem = document.getElementById('metric-sharpe');
    if (sharpeElem) sharpeElem.innerText = (bestSummary.sharpe_ratio || 0).toFixed(2);

    const pfElem = document.getElementById('metric-profit-factor');
    if (pfElem) pfElem.innerText = (bestSummary.profit_factor || 0).toFixed(2);
    
    const ddElem = document.getElementById('metric-drawdown');
    if (ddElem) ddElem.innerText = `${(bestSummary.max_drawdown || 0).toFixed(1)}%`;
}

function renderAblationTable() {
    const tbody = document.getElementById('ablation-table-body');
    if (!tbody || !rawData || !rawData.summary) return;
    tbody.innerHTML = '';

    rawData.summary.forEach(item => {
        const isBest = item.experiment === rawData.best_experiment;
        const tr = document.createElement('tr');
        if (isBest) tr.className = 'highlight-row';

        const ret = item.total_return || 0;
        tr.innerHTML = `
            <td><strong>${item.experiment}</strong> ${isBest ? '<span class="badge info">Best</span>' : ''}</td>
            <td>${item.num_features || 0}</td>
            <td><strong>${(item.sharpe_ratio || 0).toFixed(2)}</strong></td>
            <td>${(item.win_rate || 0).toFixed(1)}%</td>
            <td class="${ret >= 0 ? 'text-green' : 'text-red'}">${ret >= 0 ? '+' : ''}${ret.toFixed(1)}%</td>
            <td>${(item.max_drawdown || 0).toFixed(1)}%</td>
        `;
        tbody.appendChild(tr);
    });
}

function renderChart() {
    const canvas = document.getElementById('mainChart');
    if (!canvas || !rawData || !rawData.tsla_chart_data) return;
    const ctx = canvas.getContext('2d');
    if (mainChartInstance) mainChartInstance.destroy();

    const chartData = rawData.tsla_chart_data;
    const labels = chartData.map(d => d.date);

    if (currentTab === 'equity') {
        const tabfmEquity = chartData.map(d => (d.equity_curve * 100).toFixed(2));
        const buyHoldEquity = chartData.map(d => (d.buy_hold_equity * 100).toFixed(2));

        mainChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'TabFM Multi-Source Strategy',
                        data: tabfmEquity,
                        borderColor: '#2962FF',
                        backgroundColor: 'rgba(41, 98, 255, 0.1)',
                        borderWidth: 3,
                        tension: 0.2,
                        fill: true
                    },
                    {
                        label: 'TSLA Buy & Hold Benchmark',
                        data: buyHoldEquity,
                        borderColor: 'rgba(255, 255, 255, 0.35)',
                        borderWidth: 1.5,
                        borderDash: [4, 4],
                        fill: false
                    }
                ]
            },
            options: getChartOptions('Portfolio Performance (Base 100)')
        });
    } else {
        const closes = chartData.map(d => d.close);
        const upPoints = chartData.map(d => d.signal === 1 ? d.close : null);
        const downPoints = chartData.map(d => d.signal === -1 ? d.close : null);

        mainChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'TSLA Price ($)',
                        data: closes,
                        borderColor: '#F0F4F8',
                        borderWidth: 2,
                        tension: 0.1
                    },
                    {
                        label: 'Swing Up Signal',
                        data: upPoints,
                        pointStyle: 'triangle',
                        pointRadius: 8,
                        pointBackgroundColor: '#00E676',
                        showLine: false
                    },
                    {
                        label: 'Swing Down Signal',
                        data: downPoints,
                        pointStyle: 'triangle',
                        pointRotation: 180,
                        pointRadius: 8,
                        pointBackgroundColor: '#FF1744',
                        showLine: false
                    }
                ]
            },
            options: getChartOptions('TSLA Daily Price & TabFM Signals')
        });
    }
}

function getChartOptions(titleText) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: '#8A99AD', font: { family: 'Outfit' } } }
        },
        scales: {
            x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#8A99AD' } },
            y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#8A99AD' } }
        }
    };
}

function renderSignalsTable() {
    const tbody = document.getElementById('signals-table-body');
    if (!tbody || !rawData || !rawData.tsla_chart_data) return;
    tbody.innerHTML = '';

    let rows = rawData.tsla_chart_data.slice().reverse();
    if (currentFilter === 'signals') {
        rows = rows.filter(r => r.signal !== 0);
    }

    rows.forEach(item => {
        const tr = document.createElement('tr');
        
        let signalPill = '<span class="signal-pill neutral">NEUTRAL</span>';
        if (item.signal === 1) signalPill = '<span class="signal-pill up">LONG SWING</span>';
        if (item.signal === -1) signalPill = '<span class="signal-pill down">SHORT SWING</span>';

        let targetPill = '<span class="text-secondary">Neutral</span>';
        if (item.swing_target === 2) targetPill = '<span style="color:#00E676; font-weight:600">Up (+5%)</span>';
        if (item.swing_target === 0) targetPill = '<span style="color:#FF1744; font-weight:600">Down (-5%)</span>';

        const newsVal = item.news_sentiment || 0;
        const xVal = item.x_sentiment_score || 0;
        const polSignal = item.political_trade_signal || 0;

        tr.innerHTML = `
            <td><strong>${item.date}</strong></td>
            <td>$${(item.close || 0).toFixed(2)}</td>
            <td>${targetPill}</td>
            <td>${signalPill}</td>
            <td>
                ${((item.prob_up || 0) * 100).toFixed(0)}%
                <div class="prob-bar-container"><div class="prob-bar up" style="width: ${(item.prob_up || 0) * 100}%"></div></div>
            </td>
            <td>
                ${((item.prob_down || 0) * 100).toFixed(0)}%
                <div class="prob-bar-container"><div class="prob-bar down" style="width: ${(item.prob_down || 0) * 100}%"></div></div>
            </td>
            <td>${newsVal > 0 ? '+' : ''}${newsVal.toFixed(2)}</td>
            <td>${polSignal > 0 ? '<span style="color:#00E676; font-weight:600">BUY</span>' : (polSignal < 0 ? '<span style="color:#FF1744; font-weight:600">SELL</span>' : 'None')}</td>
            <td>${xVal > 0 ? '+' : ''}${xVal.toFixed(2)}</td>
        `;
        tbody.appendChild(tr);
    });
}

