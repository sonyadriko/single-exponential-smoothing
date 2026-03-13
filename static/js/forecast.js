// Forecast calculator module

const ForecastCalculator = {
    // Calculate Single Exponential Smoothing
    calculateSES(actualData, alpha) {
        if (!actualData || actualData.length === 0) {
            throw new Error('No data provided for calculation');
        }

        const steps = [];
        let forecast = actualData[0]; // F1 = A1
        let totalError = 0;
        let totalErrorPercent = 0;

        actualData.forEach((actual, index) => {
            const period = index + 1;
            const prevForecast = forecast;
            const error = actual - prevForecast;
            const errorPercent = prevForecast !== 0 ? (Math.abs(error) / prevForecast) * 100 : 0;

            totalError += Math.abs(error);
            totalErrorPercent += errorPercent;

            steps.push({
                period,
                actual,
                forecast: prevForecast,
                error: Math.round(error * 100) / 100,
                error_percent: Math.round(errorPercent * 10) / 10,
                formula: `${alpha} × ${actual} + ${(1 - alpha)} × ${prevForecast.toFixed(2)}`
            });

            // Calculate next forecast
            forecast = (alpha * actual) + ((1 - alpha) * prevForecast);
        });

        // Calculate MAPE (Mean Absolute Percentage Error)
        const mape = actualData.length > 0 ? totalErrorPercent / actualData.length : 0;

        return {
            next_period_forecast: Math.round(forecast * 10) / 10,
            mape: Math.round(mape * 10) / 10,
            calculation_steps: steps,
            alpha
        };
    },

    // Format calculation steps for display
    formatSteps(steps) {
        return steps.map(step => ({
            ...step,
            display_formula: this.formatFormula(step.formula),
            calculation_result: `${step.alpha} × ${step.actual} + ${(1 - step.alpha)} × ${step.forecast.toFixed(2)} = ${step.actual * step.alpha + (1 - step.alpha) * step.forecast}`
        }));
    },

    formatFormula(formula) {
        // Pretty print the SES formula
        return formula.replace(/\*/g, '×');
    },

    // Get MAPE rating
    getMapeRating(mape) {
        if (mape < 10) return { label: 'Excellent', class: 'text-green-600' };
        if (mape < 20) return { label: 'Good', class: 'text-yellow-600' };
        return { label: 'Poor', class: 'text-red-600' };
    },

    // Calculate optimal alpha using grid search
    findOptimalAlpha(actualData) {
        const alphas = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9];
        let bestAlpha = 0.3;
        let bestMape = Infinity;

        alphas.forEach(alpha => {
            const result = this.calculateSES(actualData, alpha);
            if (result.mape < bestMape) {
                bestMape = result.mape;
                bestAlpha = alpha;
            }
        });

        return { alpha: bestAlpha, mape: bestMape };
    }
};

// Make available globally
window.ForecastCalculator = ForecastCalculator;
