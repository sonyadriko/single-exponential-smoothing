import { useState } from 'react';
import { Calculator, Play, TrendingUp } from 'lucide-react';
import api from '../api';

interface ForecastCalculatorProps {
    token: string;
    onForecastGenerated: () => void;
    projectName?: string;
}

const ForecastCalculator: React.FC<ForecastCalculatorProps> = ({ token: _token, onForecastGenerated, projectName }) => {
    const [alpha, setAlpha] = useState(0.5);
    const [selectedProduct, setSelectedProduct] = useState<string>('');
    const [projectNameInput, setProjectNameInput] = useState(projectName || '');
    const [products] = useState([
        "Soto Ayam", "Nasi Goreng Jawa", "Nasi Bebek Biasa",
        "Nasi Ayam", "Nasi Lele", "Nasi 3T", "Es Teh", "Es Jeruk"
    ]);
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState<any>(null);

    const handleGenerateForecast = async () => {
        setLoading(true);
        try {
            const payload: any = { alpha };
            if (selectedProduct) {
                payload.product_name = selectedProduct;
            }
            if (projectNameInput.trim()) {
                payload.project_name = projectNameInput.trim();
            }

            const response = await api.post('/forecast', payload);
            setResults(response.data);
            onForecastGenerated();
        } catch (err: any) {
            alert('Failed to generate forecast: ' + (err.response?.data?.detail || err.message));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold">Generate Forecast</h2>
                <p className="text-muted-foreground text-sm">Create Single Exponential Smoothing forecast with step-by-step calculation</p>
            </div>

            <div className="bg-card border border-border rounded-xl p-6 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                        <label className="text-sm font-medium">Project Name (Optional)</label>
                        <input
                            type="text"
                            placeholder="e.g., Q1 Forecast"
                            value={projectNameInput}
                            onChange={(e) => setProjectNameInput(e.target.value)}
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:ring-2 ring-primary outline-none mt-2"
                        />
                        <p className="text-xs text-muted-foreground mt-1">Save as a project for future reference</p>
                    </div>
                    <div>
                        <label className="text-sm font-medium">Product</label>
                        <select
                            value={selectedProduct}
                            onChange={(e) => setSelectedProduct(e.target.value)}
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:ring-2 ring-primary outline-none mt-2"
                        >
                            <option value="">All Products</option>
                            {products.map((p) => (
                                <option key={p} value={p}>{p}</option>
                            ))}
                        </select>
                        <p className="text-xs text-muted-foreground mt-1">Leave empty to forecast all products</p>
                    </div>
                    <div>
                        <label className="text-sm font-medium">Smoothing Factor (Alpha): {alpha}</label>
                        <input
                            type="range"
                            min="0.1"
                            max="0.9"
                            step="0.1"
                            value={alpha}
                            onChange={(e) => setAlpha(parseFloat(e.target.value))}
                            className="w-full mt-2 accent-primary cursor-pointer"
                        />
                        <div className="flex justify-between text-xs text-muted-foreground">
                            <span>0.1 (Slow)</span>
                            <span>0.9 (Fast)</span>
                        </div>
                    </div>
                </div>

                <button
                    onClick={handleGenerateForecast}
                    disabled={loading}
                    className="flex items-center justify-center gap-2 w-full h-12 px-4 py-2 rounded-lg text-sm bg-primary text-primary-foreground hover:bg-primary/90 transition-colors font-semibold disabled:opacity-50"
                >
                    {loading ? (
                        <>Calculating...</>
                    ) : (
                        <>
                            <Play size={18} /> Generate Forecast
                        </>
                    )}
                </button>

                {results && (
                    <div className="space-y-6 pt-4 border-t border-border">
                        {/* Formulas Section */}
                        <div className="bg-card border border-border rounded-xl p-6">
                            <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                                <Calculator size={20} /> Forecasting Formulas
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="bg-secondary/5 rounded-lg p-4">
                                    <p className="text-sm font-semibold text-secondary mb-2">Single Exponential Smoothing (SES)</p>
                                    <div className="space-y-2 text-sm">
                                        <p className="font-mono bg-background p-2 rounded">F₁ = A₁ (Initial)</p>
                                        <p className="font-mono bg-background p-2 rounded">Fₜ₊₁ = α × Aₜ + (1 - α) × Fₜ</p>
                                    </div>
                                    <div className="mt-3 text-xs text-muted-foreground">
                                        <p>Where:</p>
                                        <ul className="ml-4 list-disc">
                                            <li>Fₜ = Forecast for period t</li>
                                            <li>Aₜ = Actual value for period t</li>
                                            <li>α = Smoothing factor (0.1 - 0.9)</li>
                                        </ul>
                                    </div>
                                </div>
                                <div className="bg-secondary/5 rounded-lg p-4">
                                    <p className="text-sm font-semibold text-secondary mb-2">Mean Absolute Percentage Error (MAPE)</p>
                                    <div className="space-y-2 text-sm">
                                        <p className="font-mono bg-background p-2 rounded text-center">MAPE = (1/n) × Σ|Aₜ - Fₜ| / Aₜ × 100%</p>
                                    </div>
                                    <div className="mt-3 text-xs text-muted-foreground">
                                        <p>Measures average accuracy as percentage</p>
                                        <p className="mt-1">Lower MAPE = Better forecast</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Overall Results */}
                        <div className="bg-secondary/10 rounded-lg p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-muted-foreground">Overall MAPE (All Products)</p>
                                    <p className="text-3xl font-bold text-secondary">{results.overall_mape.toFixed(2)}%</p>
                                    <p className={`text-xs mt-1 ${results.overall_mape < 15 ? 'text-green-500' : results.overall_mape < 25 ? 'text-yellow-500' : 'text-red-500'}`}>
                                        {results.overall_mape < 15 ? '✓ Excellent Forecast' : results.overall_mape < 25 ? '⚠ Good Forecast' : '✗ Poor Forecast'}
                                    </p>
                                </div>
                                <TrendingUp className="text-secondary" size={40} />
                            </div>
                        </div>

                        {/* Per Product Calculations */}
                        {Object.entries(results.results).map(([productName, data]: [string, any]) => (
                            <div key={productName} className="border border-border rounded-xl overflow-hidden">
                                <div className="bg-muted px-6 py-4 flex justify-between items-center">
                                    <div>
                                        <h3 className="font-bold text-lg">{productName}</h3>
                                        <p className="text-sm text-muted-foreground">MAPE: {data.mape.toFixed(2)}%</p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-xs text-muted-foreground">Next Period Forecast</p>
                                        <p className="text-3xl font-bold text-primary">{data.next_period_forecast.toFixed(1)}</p>
                                    </div>
                                </div>
                                
                                {/* Step-by-Step Calculation Table */}
                                <div className="p-4 bg-background">
                                    <h4 className="font-semibold mb-3 text-sm text-muted-foreground">Step-by-Step Calculation (α = {results.results[Object.keys(results.results)[0]].steps[0]?.formula?.match(/[\d.]+/)?.[0] || '0.5'})</h4>
                                    <div className="overflow-x-auto">
                                        <table className="w-full text-xs">
                                            <thead className="bg-muted">
                                                <tr>
                                                    <th className="text-left p-3">Periode</th>
                                                    <th className="text-left p-3">Tanggal</th>
                                                    <th className="text-right p-3">Aktual (Aₜ)</th>
                                                    <th className="text-right p-3">Forecast (Fₜ)</th>
                                                    <th className="text-left p-3">Rumus</th>
                                                    <th className="text-left p-3">Perhitungan</th>
                                                    <th className="text-right p-3">Hasil</th>
                                                    <th className="text-right p-3">Error</th>
                                                    <th className="text-right p-3">Error %</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {data.steps.map((step: any, idx: number) => (
                                                    <tr key={idx} className="border-t border-border hover:bg-muted/30">
                                                        <td className="p-3 font-semibold">{step.period}</td>
                                                        <td className="p-3">{step.date}</td>
                                                        <td className="p-3 text-right font-mono font-bold">{step.actual}</td>
                                                        <td className="p-3 text-right font-mono">{step.forecast.toFixed(2)}</td>
                                                        <td className="p-3 text-xs text-muted-foreground font-mono">{step.formula}</td>
                                                        <td className="p-3 text-xs font-mono">{step.calculation}</td>
                                                        <td className="p-3 text-right font-mono font-bold text-secondary">{step.result.toFixed(2)}</td>
                                                        <td className="p-3 text-right font-mono text-muted-foreground">
                                                            {step.error > 0 ? `±${step.error.toFixed(2)}` : '0.00'}
                                                        </td>
                                                        <td className={`p-3 text-right font-mono font-semibold ${step.error_pct > 20 ? 'text-destructive' : step.error_pct > 10 ? 'text-yellow-500' : 'text-green-500'}`}>
                                                            {step.error_pct.toFixed(1)}%
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>

                                {/* MAPE Calculation Detail */}
                                <div className="p-4 bg-muted/30 border-t border-border">
                                    <h4 className="font-semibold mb-2 text-sm">MAPE Calculation Detail:</h4>
                                    <div className="text-xs font-mono bg-background p-3 rounded">
                                        <p>MAPE = (1/{data.steps.length}) × [</p>
                                        <div className="ml-4">
                                            {data.steps.slice(0, 5).map((step: any, idx: number) => (
                                                <p key={idx}>
                                                    |{step.actual} - {step.forecast.toFixed(2)}| / {step.actual}
                                                    {idx < Math.min(4, data.steps.length - 1) ? ' + ' : data.steps.length > 5 ? ' + ...' : ''}
                                                </p>
                                            ))}
                                        </div>
                                        <p>] × 100% = <span className="font-bold text-secondary">{data.mape.toFixed(2)}%</span></p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ForecastCalculator;