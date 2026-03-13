// Chart.js helper module

const ChartHelper = {
    colors: [
        '#3b82f6', // blue
        '#8b5cf6', // purple
        '#10b981', // green
        '#f59e0b', // yellow
        '#ef4444', // red
        '#ec4899', // pink
        '#06b6d4', // cyan
        '#84cc16', // lime
    ],

    // Default chart options
    defaultOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    usePointStyle: true,
                    padding: 15
                }
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                padding: 12,
                cornerRadius: 6
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        }
    },

    // Create forecast line chart
    createForecastChart(canvasId, forecasts) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');

        // Destroy existing chart if any
        const existingChart = Chart.getChart(canvas);
        if (existingChart) {
            existingChart.destroy();
        }

        const datasets = this.buildDatasets(forecasts);
        const labels = this.extractLabels(forecasts);

        return new Chart(ctx, {
            type: 'line',
            data: { labels, datasets },
            options: {
                ...this.defaultOptions,
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        title: {
                            display: true,
                            text: 'Quantity'
                        }
                    }
                }
            }
        });
    },

    // Build datasets from forecast data
    buildDatasets(forecasts) {
        const datasets = [];
        const forecastArray = Array.isArray(forecasts) ? forecasts : [forecasts];

        forecastArray.forEach((forecast, index) => {
            if (!forecast.calculation_steps || !Array.isArray(forecast.calculation_steps)) {
                return;
            }

            const color = this.colors[index % this.colors.length];
            const productName = forecast.product_name || 'Product';

            // Actual data line
            datasets.push({
                label: `${productName} - Actual`,
                data: forecast.calculation_steps.map(s => s.actual),
                borderColor: color,
                backgroundColor: color + '20',
                borderWidth: 2.5,
                pointRadius: 4,
                pointHoverRadius: 6,
                tension: 0.2,
                fill: false
            });

            // Forecast data line
            datasets.push({
                label: `${productName} - Forecast`,
                data: forecast.calculation_steps.map(s => s.forecast),
                borderColor: color,
                backgroundColor: 'transparent',
                borderWidth: 2,
                borderDash: [6, 4],
                pointRadius: 3,
                pointHoverRadius: 5,
                pointStyle: 'triangle',
                tension: 0.2,
                fill: false
            });
        });

        return datasets;
    },

    // Extract labels from forecast steps
    extractLabels(forecasts) {
        const forecastArray = Array.isArray(forecasts) ? forecasts : [forecasts];

        if (forecastArray.length > 0 &&
            forecastArray[0].calculation_steps &&
            Array.isArray(forecastArray[0].calculation_steps)) {
            return forecastArray[0].calculation_steps.map(s => s.period || s.date || s.month || '');
        }

        return [];
    },

    // Create a simple bar chart
    createBarChart(canvasId, labels, data, label = 'Value') {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');

        // Destroy existing chart
        const existingChart = Chart.getChart(canvas);
        if (existingChart) {
            existingChart.destroy();
        }

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label,
                    data,
                    backgroundColor: this.colors[0] + '80',
                    borderColor: this.colors[0],
                    borderWidth: 2,
                    borderRadius: 6
                }]
            },
            options: this.defaultOptions
        });
    },

    // Update existing chart with new data
    updateChart(chart, newData) {
        if (!chart) return;

        chart.data.datasets = this.buildDatasets(newData);
        chart.data.labels = this.extractLabels(newData);
        chart.update();
    },

    // Destroy chart by canvas ID
    destroyChart(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const existingChart = Chart.getChart(canvas);
        if (existingChart) {
            existingChart.destroy();
        }
    }
};

// Make available globally
window.ChartHelper = ChartHelper;
