import React, { useState } from 'react';
import { Settings, BarChart3, TrendingUp, AlertCircle, Loader2 } from 'lucide-react';
import { cn } from '../lib/utils';
import ForecastChart from './ForecastChart';

// Sample Data from the prompt
const MAY_DATA_RAW = [
    ["01-May-25", 21, 9, 23, 14, 17, 19, 21, 12],
    ["02-May-25", 20, 4, 19, 17, 20, 20, 16, 20],
    ["03-May-25", 18, 12, 21, 20, 28, 19, 17, 23],
    ["04-May-25", 20, 8, 16, 24, 24, 24, 8, 16],
    ["05-May-25", 22, 6, 20, 14, 18, 21, 15, 8],
    ["06-May-25", 19, 7, 24, 12, 25, 15, 19, 10],
    ["07-May-25", 14, 6, 10, 13, 15, 12, 17, 11],
    ["08-May-25", 18, 3, 16, 15, 15, 18, 20, 7],
    ["09-May-25", 20, 5, 20, 14, 11, 24, 21, 9],
    ["10-May-25", 21, 15, 14, 20, 17, 19, 19, 16],
    ["11-May-25", 19, 6, 12, 16, 21, 14, 21, 15],
    ["12-May-25", 20, 11, 16, 9, 17, 17, 15, 10],
    ["13-May-25", 16, 18, 15, 12, 15, 19, 18, 9],
    ["14-May-25", 18, 9, 12, 11, 16, 16, 16, 14],
    ["15-May-25", 14, 9, 10, 13, 12, 13, 11, 10],
    ["16-May-25", 16, 16, 14, 17, 18, 15, 22, 18],
    ["17-May-25", 18, 10, 9, 10, 17, 11, 20, 13],
    ["18-May-25", 12, 8, 11, 8, 19, 17, 16, 15],
    ["19-May-25", 14, 11, 15, 11, 17, 12, 10, 11],
    ["20-May-25", 16, 15, 12, 13, 14, 11, 19, 10],
    ["21-May-25", 12, 13, 10, 14, 18, 8, 15, 12],
    ["22-May-25", 11, 8, 9, 9, 16, 11, 18, 11],
    ["23-May-25", 16, 9, 8, 10, 13, 14, 23, 10],
    ["24-May-25", 13, 4, 11, 11, 16, 10, 21, 9],
    ["25-May-25", 11, 5, 12, 14, 14, 9, 19, 11],
    ["26-May-25", 15, 7, 14, 9, 13, 8, 16, 7],
    ["27-May-25", 12, 3, 9, 7, 11, 16, 18, 9],
    ["28-May-25", 10, 12, 8, 12, 15, 20, 15, 6],
    ["29-May-25", 8, 7, 10, 6, 11, 10, 18, 10],
    ["30-May-25", 11, 6, 7, 9, 12, 12, 17, 15],
    ["31-May-25", 9, 9, 11, 10, 15, 16, 14, 11],
];

const PRODUCTS = [
    "Soto Ayam", "Nasi Goreng Jawa", "Nasi Bebek Biasa",
    "Nasi Ayam", "Nasi Lele", "Nasi 3T", "Es Teh", "Es Jeruk"
];

const Dashboard: React.FC = () => {
    const [alpha, setAlpha] = useState(0.5);
    const [results, setResults] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const formatDataForAPI = () => {
        const dataPoints: any[] = [];
        MAY_DATA_RAW.forEach((row) => {
            const date = row[0] as string;
            PRODUCTS.forEach((product, index) => {
                dataPoints.push({
                    date: date,
                    product_name: product,
                    qty: row[index + 1],
                });
            });
        });
        return dataPoints;
    };

    const handleForecast = async () => {
        setLoading(true);
        setError(null);
        try {
            const payload = {
                data: formatDataForAPI(),
                alpha: alpha,
            };

            const response = await fetch('http://127.0.0.1:8000/forecast', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error('Failed to fetch forecast');
            }

            const data = await response.json();
            setResults(data);
        } catch (err: any) {
            setError(err.message || 'An unexpected error occurred');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-8 max-w-[1600px] mx-auto space-y-8">
            {/* Header */}
            <header className="flex justify-between items-center mb-12">
                <div>
                    <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
                        Depot Jawara Analytics
                    </h1>
                    <p className="text-muted-foreground mt-2 text-lg">
                        Sales Forecasting using Single Exponential Smoothing
                    </p>
                </div>
                <div className="flex items-center gap-4 bg-card p-4 rounded-xl border shadow-sm">
                    <div className="flex flex-col">
                        <span className="text-xs text-muted-foreground uppercase font-semibold">Smoothing Factor (Alpha)</span>
                        <div className="flex items-center gap-4 mt-1">
                            <input
                                type="range"
                                min="0.1"
                                max="0.9"
                                step="0.1"
                                value={alpha}
                                onChange={(e) => setAlpha(parseFloat(e.target.value))}
                                className="w-32 accent-blue-500 cursor-pointer"
                            />
                            <span className="font-mono font-bold text-xl text-blue-400">{alpha}</span>
                        </div>
                    </div>
                    <div className="pl-4 border-l border-border">
                        <button
                            onClick={handleForecast}
                            disabled={loading}
                            className={cn(
                                "flex items-center gap-2 px-6 py-3 rounded-lg font-bold transition-all shadow-lg hover:shadow-blue-500/20",
                                loading ? "bg-muted cursor-not-allowed text-muted-foreground" : "bg-blue-600 hover:bg-blue-500 text-white"
                            )}
                        >
                            {loading ? <Loader2 className="animate-spin" /> : <TrendingUp size={20} />}
                            Generate Forecast
                        </button>
                    </div>
                </div>
            </header>

            {/* Stats Overview */}
            {results && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-card p-6 rounded-xl border shadow-sm flex items-center gap-4">
                        <div className="p-3 bg-emerald-500/10 rounded-full text-emerald-400">
                            <BarChart3 size={32} />
                        </div>
                        <div>
                            <p className="text-sm text-muted-foreground">Overall Model Accuracy (MAPE)</p>
                            <h2 className="text-3xl font-bold">{results.overall_mape.toFixed(2)}%</h2>
                            <p className="text-xs text-emerald-400 mt-1">Lower is better</p>
                        </div>
                    </div>
                    {/* Add more stats if needed */}
                </div>
            )}

            {/* Error Message */}
            {error && (
                <div className="bg-destructive/10 text-destructive p-4 rounded-lg flex items-center gap-2 border border-destructive/20">
                    <AlertCircle size={20} />
                    {error}
                </div>
            )}

            {/* Charts Grid */}
            {results && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {Object.keys(results.results).map((product) => {
                        const productData = results.results[product];
                        // Transform for Recharts
                        const chartData = productData.dates.map((date: string, idx: number) => ({
                            date,
                            actual: productData.actuals[idx],
                            forecast: productData.forecasts[idx],
                        }));

                        return (
                            <div key={product} className="relative group">
                                <div className="absolute inset-0 bg-blue-500/5 rounded-xl blur-xl group-hover:bg-blue-500/10 transition-all" />
                                <div className="relative">
                                    <div className="flex justify-between items-center mb-2 px-1">
                                        <span className="text-sm font-mono text-muted-foreground">
                                            Next Period Forecast: <span className="text-foreground font-bold">{productData.next_period_forecast.toFixed(1)}</span>
                                        </span>
                                        <span className="text-xs font-mono text-muted-foreground">
                                            MAPE: {productData.mape.toFixed(2)}%
                                        </span>
                                    </div>
                                    <ForecastChart data={chartData} productName={product} />
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            {!results && !loading && (
                <div className="text-center py-20 text-muted-foreground bg-card/50 rounded-3xl border border-dashed">
                    <Settings className="w-16 h-16 mx-auto mb-4 opacity-20" />
                    <h3 className="text-xl font-semibold">Ready to Analyze</h3>
                    <p className="mt-2">Set your alpha parameter and click "Generate Forecast" to begin.</p>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
