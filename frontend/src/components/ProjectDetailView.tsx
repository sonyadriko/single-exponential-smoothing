import { useState, useEffect } from 'react';
import { X, Calculator, TrendingUp } from 'lucide-react';
import api from '../api';

interface ProjectDetailViewProps {
    token: string;
    projectName: string;
    onClose: () => void;
    isPage?: boolean;
}

const ProjectDetailView: React.FC<ProjectDetailViewProps> = ({ token: _token, projectName, onClose, isPage = false }) => {
    const [projectData, setProjectData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchProjectDetail();
    }, [projectName]);

    const fetchProjectDetail = async () => {
        try {
            const response = await api.get(`/forecast/project/${encodeURIComponent(projectName)}`);
            setProjectData(response.data);
        } catch (err: any) {
            alert('Failed to fetch project detail: ' + (err.response?.data?.detail || err.message));
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
                <div className="bg-card rounded-xl p-8 text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
                    <p className="mt-4 text-muted-foreground">Loading forecast details...</p>
                </div>
            </div>
        );
    }

    if (!projectData) {
        return null;
    }

    return (
        <div className={isPage ? "w-full" : "fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4 overflow-y-auto"}>
            <div className={isPage ? "w-full" : "bg-card w-full max-w-6xl rounded-xl border border-border shadow-2xl max-h-[90vh] overflow-y-auto"}>
                {/* Header */}
                <div className="sticky top-0 bg-card border-b border-border px-6 py-4 flex justify-between items-center z-10">
                    <div>
                        <h2 className="text-2xl font-bold">{projectData.project_name}</h2>
                        <p className="text-sm text-muted-foreground">Created: {new Date(projectData.created_at).toLocaleString()}</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-muted rounded-lg transition-colors"
                    >
                        <X size={24} />
                    </button>
                </div>

                <div className="p-6 space-y-6">
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
                                <p className="text-3xl font-bold text-secondary">{projectData.overall_mape.toFixed(2)}%</p>
                                <p className="text-xs text-muted-foreground mt-1">Alpha: {projectData.alpha}</p>
                            </div>
                            <TrendingUp className="text-secondary" size={40} />
                        </div>
                    </div>

                    {/* Per Product Calculations */}
                    {Object.entries(projectData.results).map(([productName, data]: [string, any]) => (
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
                                <h4 className="font-semibold mb-3 text-sm text-muted-foreground">Step-by-Step Calculation</h4>
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
            </div>
        </div>
    );
};

export default ProjectDetailView;