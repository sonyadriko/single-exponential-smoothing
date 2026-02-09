import { useState } from 'react';
import { LogOut, Package, TrendingUp, Calculator, FolderOpen, ArrowLeft } from 'lucide-react';
import ProductManager from './ProductManager';
import SalesInput from './SalesInput';
import ForecastCalculator from './ForecastCalculator';
import ForecastProjectManager from './ForecastProjectManager';
import ProjectDetailView from './ProjectDetailView';

interface AdminDashboardProps {
    token: string;
    onLogout: () => void;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ token, onLogout }) => {
    const [activeTab, setActiveTab] = useState<'products' | 'sales' | 'forecast' | 'projects' | 'projectDetail'>('products');
    const [refreshKey, setRefreshKey] = useState(0);
    const [selectedProject, setSelectedProject] = useState<string | null>(null);

    const handleForecastGenerated = () => {
        setRefreshKey(prev => prev + 1);
    };

    const handleViewProject = (projectName: string) => {
        setSelectedProject(projectName);
        setActiveTab('forecast');
    };

    const handleViewProjectDetail = (projectName: string) => {
        setSelectedProject(projectName);
        setActiveTab('projectDetail');
    };

    const handleBackToProjects = () => {
        setSelectedProject(null);
        setActiveTab('projects');
    };

    return (
        <div className="min-h-screen bg-background">
            <header className="bg-card border-b border-border px-8 py-4">
                <div className="max-w-[1600px] mx-auto flex justify-between items-center">
                    <div>
                        <h1 className="text-2xl font-bold text-primary">Depot Jawara Analytics</h1>
                        <p className="text-sm text-muted-foreground">Administrator Dashboard</p>
                    </div>
                    <button
                        onClick={onLogout}
                        className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm bg-muted hover:bg-muted/80 transition-colors"
                    >
                        <LogOut size={16} /> Logout
                    </button>
                </div>
            </header>

            <div className="max-w-[1600px] mx-auto px-8 py-6">
                {/* Navigation Tabs */}
                {activeTab !== 'projectDetail' && (
                    <div className="flex gap-2 mb-6 border-b border-border">
                        <button
                            onClick={() => setActiveTab('products')}
                            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
                                activeTab === 'products'
                                    ? 'border-primary text-primary'
                                    : 'border-transparent text-muted-foreground hover:text-foreground'
                            }`}
                        >
                            <Package size={18} /> Products
                        </button>
                        <button
                            onClick={() => setActiveTab('sales')}
                            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
                                activeTab === 'sales'
                                    ? 'border-primary text-primary'
                                    : 'border-transparent text-muted-foreground hover:text-foreground'
                            }`}
                        >
                            <TrendingUp size={18} /> Sales Data
                        </button>
                        <button
                            onClick={() => setActiveTab('projects')}
                            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
                                activeTab === 'projects'
                                    ? 'border-primary text-primary'
                                    : 'border-transparent text-muted-foreground hover:text-foreground'
                            }`}
                        >
                            <FolderOpen size={18} /> Projects
                        </button>
                        <button
                            onClick={() => {
                                setActiveTab('forecast');
                                setSelectedProject(null);
                            }}
                            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
                                activeTab === 'forecast'
                                    ? 'border-primary text-primary'
                                    : 'border-transparent text-muted-foreground hover:text-foreground'
                            }`}
                        >
                            <Calculator size={18} /> Generate
                        </button>
                    </div>
                )}

                {/* Content */}
                <div key={`${activeTab}-${refreshKey}`}>
                    {activeTab === 'products' && <ProductManager token={token} />}
                    {activeTab === 'sales' && <SalesInput token={token} />}
                    {activeTab === 'projects' && <ForecastProjectManager token={token} onViewProject={handleViewProject} onViewDetail={handleViewProjectDetail} />}
                    {activeTab === 'forecast' && <ForecastCalculator token={token} onForecastGenerated={handleForecastGenerated} projectName={selectedProject || undefined} />}
                    {activeTab === 'projectDetail' && selectedProject && (
                        <div>
                            <button
                                onClick={handleBackToProjects}
                                className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm bg-muted hover:bg-muted/80 transition-colors mb-6"
                            >
                                <ArrowLeft size={16} /> Back to Projects
                            </button>
                            <ProjectDetailView
                                token={token}
                                projectName={selectedProject}
                                onClose={handleBackToProjects}
                                isPage={true}
                            />
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;