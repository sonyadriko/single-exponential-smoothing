import { useState, useEffect } from 'react';
import { LogOut, BarChart3, Calendar } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import api from '../api';

interface OwnerDashboardProps {
    token: string;
    onLogout: () => void;
}

interface ForecastData {
    id: number;
    created_at: string;
    alpha: number;
    product_name: string;
    next_period_forecast: number;
    mape: number;
    dates: string[];
    actuals: number[];
    forecasts: number[];
}

const OwnerDashboard: React.FC<OwnerDashboardProps> = ({ token: _token, onLogout }) => {
    const [forecast, setForecast] = useState<ForecastData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchLatestForecast();
    }, []);

    const fetchLatestForecast = async () => {
        try {
            const response = await api.get('/forecast/latest');
            setForecast(response.data);
        } catch (err: any) {
            console.error('Failed to fetch forecast:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
                    <p className="mt-4 text-muted-foreground">Loading forecast data...</p>
                </div>
            </div>
        );
    }

    if (!forecast) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center px-8">
                <div className="text-center">
                    <BarChart3 size={48} className="mx-auto text-muted-foreground mb-4" />
                    <h2 className="text-xl font-semibold mb-2">No Forecast Available</h2>
                    <p className="text-muted-foreground">Please ask the administrator to generate a forecast.</p>
                </div>
            </div>
        );
    }

    const chartData = forecast.dates.map((date, idx) => ({
        date,
        actual: forecast.actuals[idx],
        forecast: forecast.forecasts[idx]
    }));

    return (
        <div className="min-h-screen bg-background">
            <header className="bg-card border-b border-border px-8 py-4">
                <div className="max-w-[1600px] mx-auto flex justify-between items-center">
                    <div>
                        <h1 className="text-2xl font-bold text-primary">Depot Jawara Analytics</h1>
                        <p className="text-sm text-muted-foreground">Owner Dashboard - View Only</p>
                    </div>
                    <button
                        onClick={onLogout}
                        className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm bg-muted hover:bg-muted/80 transition-colors"
                    >
                        <LogOut size={16} /> Logout
                    </button>
                </div>
            </header>

            <div className="max-w-[1600px] mx-auto px-8 py-6 space-y-6">
                <div className="bg-card border border-border rounded-xl p-6">
                    <div className="flex items-center gap-2 mb-4 text-sm text-muted-foreground">
                        <Calendar size={16} />
                        <span>Generated: {new Date(forecast.created_at).toLocaleString()}</span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                        <div className="bg-secondary/10 rounded-lg p-4">
                            <p className="text-sm text-muted-foreground">Product</p>
                            <p className="text-xl font-bold">{forecast.product_name}</p>
                        </div>
                        <div className="bg-secondary/10 rounded-lg p-4">
                            <p className="text-sm text-muted-foreground">Smoothing Factor (α)</p>
                            <p className="text-xl font-bold">{forecast.alpha}</p>
                        </div>
                        <div className="bg-secondary/10 rounded-lg p-4">
                            <p className="text-sm text-muted-foreground">MAPE</p>
                            <p className="text-xl font-bold">{forecast.mape.toFixed(2)}%</p>
                        </div>
                    </div>

                    <div className="bg-primary/10 rounded-lg p-6 mb-6">
                        <p className="text-sm text-muted-foreground mb-2">Next Period Forecast</p>
                        <p className="text-4xl font-bold text-primary">{forecast.next_period_forecast.toFixed(1)} units</p>
                    </div>

                    <div>
                        <h3 className="text-lg font-semibold mb-4">Forecast Chart</h3>
                        <div className="bg-card rounded-lg border border-border p-4">
                            <ResponsiveContainer width="100%" height={400}>
                                <LineChart data={chartData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="date" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Line type="monotone" dataKey="actual" stroke="#3b82f6" name="Actual Sales" strokeWidth={2} />
                                    <Line type="monotone" dataKey="forecast" stroke="#10b981" name="Forecast" strokeWidth={2} strokeDasharray="5 5" />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>

                <div className="bg-card border border-border rounded-xl p-6">
                    <h3 className="text-lg font-semibold mb-4">Forecast Summary Table</h3>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-muted">
                                <tr>
                                    <th className="text-left p-3">Date</th>
                                    <th className="text-right p-3">Actual</th>
                                    <th className="text-right p-3">Forecast</th>
                                    <th className="text-right p-3">Difference</th>
                                    <th className="text-right p-3">Accuracy</th>
                                </tr>
                            </thead>
                            <tbody>
                                {chartData.map((row, idx) => {
                                    const diff = row.actual - row.forecast;
                                    const accuracy = 100 - (Math.abs(diff) / row.actual * 100);
                                    return (
                                        <tr key={idx} className="border-t border-border">
                                            <td className="p-3">{row.date}</td>
                                            <td className="p-3 text-right font-mono">{row.actual}</td>
                                            <td className="p-3 text-right font-mono">{row.forecast.toFixed(2)}</td>
                                            <td className={`p-3 text-right font-mono ${diff > 0 ? 'text-green-500' : 'text-red-500'}`}>
                                                {diff > 0 ? '+' : ''}{diff.toFixed(2)}
                                            </td>
                                            <td className="p-3 text-right font-mono">{accuracy.toFixed(1)}%</td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default OwnerDashboard;