document.addEventListener('DOMContentLoaded', function() {
    // Sales Overview Chart Rendering Implementation Matrix
    const ctx = document.getElementById('salesOverviewChart');
    if (ctx) {
        // Gradient fill element calculation loops
        const chartGradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 260);
        chartGradient.addColorStop(0, 'rgba(10, 45, 33, 0.12)');
        chartGradient.addColorStop(1, 'rgba(10, 45, 33, 0.0)');
        const labels = JSON.parse(
            document.getElementById("chart-labels").textContent
        );

        const values = JSON.parse(
            document.getElementById("chart-values").textContent
        );
        console.log(labels);
        console.log(values);

        new Chart(ctx, {
            
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Revenue',
                    data: values,
                                    borderColor: '#0a2d21',
                    borderWidth: 2.5,
                    backgroundColor: chartGradient,
                    fill: true,
                    tension: 0.38, // Beautiful natural organic curve smoothing multiplier
                    pointBackgroundColor: '#0a2d21',
                    pointHoverRadius: 6,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false } // Custom HTML header handles legends manually
                },
                scales: {
                    y: {
                        grid: { borderDash: [4, 4], color: '#eae9e2' },
                        ticks: {
                            callback: function(val) { return '₹' + val ; },
                            color: '#8c9698',
                            font: { size: 10 }
                        }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#8c9698', font: { size: 10 } }
                    }
                }
            }
        });
    }

});
// Payment Distribution Chart
const paymentCanvas = document.getElementById("paymentChart");

if (paymentCanvas) {

    const paymentLabels = JSON.parse(
        document.getElementById("payment-labels").textContent
    );

    const paymentValues = JSON.parse(
        document.getElementById("payment-values").textContent
    );

    new Chart(paymentCanvas, {
        type: "doughnut",
        data: {
            labels: paymentLabels,
            datasets: [{
                data: paymentValues,
                backgroundColor: [
                    "#0A2D21",
                    "#C5A47E",
                    "#2C7EBF"
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom"
                }
            }
        }
    });
}
const statusCanvas = document.getElementById("statusChart");

if (statusCanvas) {

    const statusLabels = JSON.parse(
        document.getElementById("status-labels").textContent
    );

    const statusValues = JSON.parse(
        document.getElementById("status-values").textContent
    );

    new Chart(statusCanvas, {
        type: "doughnut",
        data: {
            labels: statusLabels,
            datasets: [{
                data: statusValues
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}
const dateForm = document.getElementById("dateFilterForm");

if (dateForm) {

    dateForm.addEventListener("submit", function(e) {

        const startDate =
            document.querySelector(
                'input[name="start_date"]'
            ).value;

        const endDate =
            document.querySelector(
                'input[name="end_date"]'
            ).value;

        if (startDate && endDate) {

            if (startDate > endDate) {

                e.preventDefault();

                alert(
                    "End date must be greater than or equal to start date."
                );
            }
        }

    });

}