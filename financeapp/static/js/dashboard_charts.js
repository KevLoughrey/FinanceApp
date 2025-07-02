const commonOptions = {
    responsive: true,
    plugins: {
        legend: {
            position: 'bottom',
        },
    },
};

new Chart(document.getElementById('expenseChart'), {
    type: 'doughnut',
    data: {
        labels: expenseLabels,
        datasets: [{
            label: 'Expenses',
            data: expenseData,
        }]
    },
    options: commonOptions,
});

new Chart(document.getElementById('incomeChart'), {
    type: 'doughnut',
    data: {
        labels: incomeLabels,
        datasets: [{
            label: 'Income',
            data: incomeData,
        }]
    },
    options: commonOptions,
});

new Chart(document.getElementById('compChart'), {
    type: 'line',
    data: {
        labels: monthlyLabels,
        datasets: [
        {
            label: 'Expenses',
            data: monthlyExpenses,
            borderColor: '#e74c3c',
            tension: 0.3
        },
        {
            label: 'Income',
            data: monthlyIncome,
            borderColor: '#2ecc71',
            tension: 0.3
        }
        ]
    },
    options: {
        responsive: true,
        plugins: {
        legend: { position: 'bottom' },
        tooltip: { mode: 'index', intersect: false }
        },
        interaction: {
        mode: 'nearest',
        axis: 'x',
        intersect: false
        },
        scales: {
        y: {
            beginAtZero: true,
            title: {
            display: true,
            text: 'Amount'
            }
        },
        x: {
            title: {
            display: true,
            text: 'Month'
            }
        }
        }
    }
    });