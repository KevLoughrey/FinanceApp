const commonOptions = {
    responsive: true,
    plugins: {
        legend: {
            position: 'bottom',
        },
    },
};

const expenseChart = new Chart(document.getElementById('expenseChart'), {
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

const incomeChart = new Chart(document.getElementById('incomeChart'), {
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

const compChart = new Chart(document.getElementById('compChart'), {
    type: 'line',
    data: {
        labels: monthlyLabels,
        datasets: [{
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
            legend: {
                position: 'bottom'
            },
            tooltip: {
                mode: 'index',
                intersect: false
            }
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

document.getElementById("filterCharts").addEventListener("click", () => {
    const start = document.getElementById("startMonth").value;
    const end = document.getElementById("endMonth").value;

    fetch(`/finances/get_date_range?start=${start}&end=${end}`)
        .then(res => res.json())
        .then(data => {
            console.log(data);
            expenseChart.data.labels = data.expense_data.map(row => row.category);
            expenseChart.data.datasets[0].data = data.expense_data.map(row => row.total);
            expenseChart.update();

            incomeChart.data.labels = data.income_data.map(row => row.category);
            incomeChart.data.datasets[0].data = data.income_data.map(row => row.total);
            incomeChart.update();

            compChart.data.labels = data.monthly_data.months;
            compChart.data.datasets[0].data = data.monthly_data.expenses;
            compChart.data.datasets[1].data = data.monthly_data.income;
            compChart.update();
        });
});