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