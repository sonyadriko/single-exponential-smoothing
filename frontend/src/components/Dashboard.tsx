import { useState, useEffect } from 'react';
import { BarChart3, AlertCircle, Loader2, LogOut, Plus, RefreshCw, Save } from 'lucide-react';
import { cn } from '../lib/utils';
import ForecastChart from './ForecastChart';
import api from '../api';

interface DashboardProps {
    userRole: string | null;
    token: string;
    onLogout: () => void;
}

const PRODUCTS = [
    "Soto Ayam", "Nasi Goreng Jawa", "Nasi Bebek Biasa",
    "Nasi Ayam", "Nasi Lele", "Nasi 3T", "Es Teh", "Es Jeruk"
];

const Dashboard: React.FC<DashboardProps> = ({ userRole, token: _token, onLogout }) => {
    const [alpha, setAlpha] = useState(0.5);
    const [results, setResults] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [refreshKey, setRefreshKey] = useState(0);

    // Admin State for Add Data
    const [showAddModal, setShowAddModal] = useState(false);
    const [newData, setNewData] = useState({
        date: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: '2-digit' }).replace(/ /g, '-'),
        product_name: PRODUCTS[0],
        qty: 0
    });

    const fetchForecast = async () => {
        setLoading(true);
        setError(null);
        try {
            // POST request to /forecast with Alpha. The backend now fetches data from DB itself.
            const response = await api.post('/forecast', { alpha: alpha });
            setResults(response.data);
        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.detail || 'Failed to fetch forecast');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchForecast();
    }, [alpha, refreshKey]);

    const handleAddData = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await api.post('/sales', newData);
            setShowAddModal(false);
            setRefreshKey(prev => prev + 1); // Trigger re-fetch
        } catch (err: any) {
            alert('Failed to add data: ' + (err.response?.data?.detail || err.message));
        }
    };

    const handleResetData = async () => {
        if (!confirm("Are you sure you want to reset all data to the initial May dataset? This cannot be undone.")) return;
        try {
            await api.post('/reset-data', {});
            setRefreshKey(prev => prev + 1);
        } catch (err: any) {
            alert('Failed to reset: ' + err.message);
        }
    };

    return (
        <div className="p-8 max-w-[1600px] mx-auto space-y-8 pb-20">
            {/* Header */}
            <header className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-4xl font-extrabold tracking-tight text-primary">
                        Depot Jawara Analytics
                    </h1>
                    <p className="text-muted-foreground mt-2 text-lg flex items-center gap-2">
                        <span className={cn("px-2 py-0.5 rounded-full text-xs font-bold uppercase", userRole === 'admin' ? "bg-primary/10 text-primary" : "bg-secondary/10 text-secondary")}>
                            {userRole === 'admin' ? 'Administrator' : 'Business Owner'}
                        </span>
                        View
                    </p>
                </div>

                <div className="flex items-center gap-4">
                    {userRole === 'admin' && (
                        <>
                            <button onClick={handleResetData} className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm bg-destructive/10 text-destructive hover:bg-destructive/20 transition-colors">
                                <RefreshCw size={16} /> Reset Data
                            </button>
                            <button onClick={() => setShowAddModal(true)} className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm bg-primary text-primary-foreground hover:bg-primary/90 transition-colors shadow-lg">
                                <Plus size={16} /> Add Sales Data
                            </button>
                        </>
                    )}
                    <button onClick={onLogout} className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm bg-card border border-border hover:bg-muted transition-colors">
                        <LogOut size={16} /> Logout
                    </button>
                </div>
            </header>

            {/* Controls */}
            <div className="bg-card p-4 rounded-xl border shadow-sm flex flex-wrap items-center gap-8">
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
                            className="w-48 accent-secondary cursor-pointer"
                        />
                        <span className="font-mono font-bold text-xl text-secondary w-8">{alpha}</span>
                    </div>
                </div>

                {results && (
                    <div className="flex items-center gap-4 border-l pl-8 border-border">
                        <div className="p-3 bg-secondary/10 rounded-full text-secondary">
                            <BarChart3 size={24} />
                        </div>
                        <div>
                            <p className="text-xs text-muted-foreground">Overall Error (MAPE)</p>
                            <h2 className="text-2xl font-bold">{results.overall_mape.toFixed(2)}%</h2>
                        </div>
                    </div>
                )}
            </div>

            {/* Error Message */}
            {error && (
                <div className="bg-destructive/10 text-destructive p-4 rounded-lg flex items-center gap-2 border border-destructive/20 animate-in slide-in-from-top-2">
                    <AlertCircle size={20} />
                    {error}
                </div>
            )}

            {/* Loading State */}
            {loading && !results && (
                <div className="flex justify-center py-20">
                    <Loader2 className="animate-spin text-secondary" size={48} />
                </div>
            )}

            {/* Charts Grid */}
            {results && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {Object.keys(results.results).map((product) => {
                        const productData = results.results[product];
                        const chartData = productData.dates.map((date: string, idx: number) => ({
                            date,
                            actual: productData.actuals[idx],
                            forecast: productData.forecasts[idx],
                        }));

                        return (
                            <div key={product} className="relative group bg-card rounded-xl border border-border p-1 overflow-hidden">
                                <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-secondary to-transparent opacity-50" />
                                <div className="p-4">
                                    <div className="flex justify-between items-start mb-4">
                                        <div>
                                            <h3 className="font-bold text-lg">{product}</h3>
                                            <p className="text-xs text-muted-foreground">MAPE: {productData.mape.toFixed(2)}%</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-xs text-muted-foreground">Next Forecast</p>
                                            <span className="text-2xl font-bold text-secondary">{productData.next_period_forecast.toFixed(1)}</span>
                                        </div>
                                    </div>
                                    <ForecastChart data={chartData} productName={product} />
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            {/* Add Data Modal */}
            {showAddModal && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-card w-full max-w-lg rounded-xl border border-border shadow-2xl p-6 animate-in zoom-in-95">
                        <h2 className="text-2xl font-bold mb-6">Add Sales Data</h2>
                        <form onSubmit={handleAddData} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Date (DD-MMM-YY)</label>
                                    <input
                                        type="text"
                                        required
                                        value={newData.date}
                                        onChange={e => setNewData({ ...newData, date: e.target.value })}
                                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:ring-2 ring-primary outline-none"
                                    />
                                    <p className="text-[10px] text-muted-foreground">Ex: 01-Jun-25</p>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Qty</label>
                                    <input
                                        type="number"
                                        required
                                        value={newData.qty}
                                        onChange={e => setNewData({ ...newData, qty: parseInt(e.target.value) })}
                                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:ring-2 ring-primary outline-none"
                                    />
                                </div>
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Product</label>
                                <select
                                    value={newData.product_name}
                                    onChange={e => setNewData({ ...newData, product_name: e.target.value })}
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:ring-2 ring-primary outline-none"
                                >
                                    {PRODUCTS.map(p => <option key={p} value={p}>{p}</option>)}
                                </select>
                            </div>

                            <div className="flex justify-end gap-3 mt-8">
                                <button
                                    type="button"
                                    onClick={() => setShowAddModal(false)}
                                    className="px-4 py-2 text-sm font-medium hover:bg-muted rounded-md transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 rounded-md transition-colors flex items-center gap-2"
                                >
                                    <Save size={16} /> Save Data
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
