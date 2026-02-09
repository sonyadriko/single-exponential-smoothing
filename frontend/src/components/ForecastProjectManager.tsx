import { useState, useEffect } from 'react';
import { FolderOpen, Plus, Trash2, Edit2, Eye, Calendar, User, TrendingUp, FileText } from 'lucide-react';
import axios from 'axios';

interface Project {
    project_name: string;
    created_at: string;
    created_by: string;
    alpha: number;
    forecast_count: number;
    overall_mape: number;
}

interface ForecastProjectManagerProps {
    token: string;
    onViewProject: (projectName: string) => void;
    onViewDetail: (projectName: string) => void;
}

const ForecastProjectManager: React.FC<ForecastProjectManagerProps> = ({ token, onViewProject, onViewDetail }) => {
    const [projects, setProjects] = useState<Project[]>([]);
    const [loading, setLoading] = useState(true);
    const [showNewModal, setShowNewModal] = useState(false);
    const [newProjectName, setNewProjectName] = useState('');

    useEffect(() => {
        fetchProjects();
    }, []);

    const fetchProjects = async () => {
        try {
            const response = await axios.get('http://127.0.0.1:8000/forecast/projects', {
                headers: { Authorization: `Bearer ${token}` }
            });
            setProjects(response.data);
        } catch (err: any) {
            console.error('Failed to fetch projects:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateProject = async () => {
        if (!newProjectName.trim()) return;
        onViewProject(newProjectName);
        setShowNewModal(false);
        setNewProjectName('');
    };

    const handleDeleteProject = async (projectName: string) => {
        if (!confirm(`Delete project "${projectName}"? This cannot be undone.`)) return;
        
        try {
            await axios.delete(
                `http://127.0.0.1:8000/forecast/project/${encodeURIComponent(projectName)}`,
                { headers: { Authorization: `Bearer ${token}` } }
            );
            fetchProjects();
        } catch (err: any) {
            alert('Failed to delete project: ' + (err.response?.data?.detail || err.message));
        }
    };

    const handleRenameProject = async (projectName: string) => {
        const newName = prompt('Enter new project name:', projectName);
        if (!newName || newName === projectName) return;

        try {
            await axios.put(
                `http://127.0.0.1:8000/forecast/project/${encodeURIComponent(projectName)}?new_name=${encodeURIComponent(newName)}`,
                {},
                { headers: { Authorization: `Bearer ${token}` } }
            );
            fetchProjects();
        } catch (err: any) {
            alert('Failed to rename project: ' + (err.response?.data?.detail || err.message));
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold">Forecast Projects</h2>
                    <p className="text-muted-foreground text-sm">Manage and view your forecast scenarios</p>
                </div>
                <button
                    onClick={() => setShowNewModal(true)}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
                >
                    <Plus size={16} /> New Project
                </button>
            </div>

            {loading ? (
                <div className="text-center py-8 text-muted-foreground">Loading projects...</div>
            ) : projects.length === 0 ? (
                <div className="bg-card border border-border rounded-xl p-8 text-center">
                    <FolderOpen size={48} className="mx-auto text-muted-foreground mb-4" />
                    <h3 className="text-lg font-semibold mb-2">No Projects Found</h3>
                    <p className="text-muted-foreground text-sm mb-4">Create your first forecast project to get started.</p>
                    <button
                        onClick={() => setShowNewModal(true)}
                        className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm bg-primary text-primary-foreground hover:bg-primary/90 transition-colors mx-auto"
                    >
                        <Plus size={16} /> Create Project
                    </button>
                </div>
            ) : (
                <div className="bg-card border border-border rounded-xl overflow-hidden">
                    <table className="w-full">
                        <thead className="bg-muted">
                            <tr>
                                <th className="text-left p-4 font-semibold">Project Name</th>
                                <th className="text-left p-4 font-semibold">Created</th>
                                <th className="text-left p-4 font-semibold">Created By</th>
                                <th className="text-right p-4 font-semibold">Alpha</th>
                                <th className="text-right p-4 font-semibold">Products</th>
                                <th className="text-right p-4 font-semibold">MAPE</th>
                                <th className="text-right p-4 font-semibold">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {projects.map((project) => (
                                <tr key={project.project_name} className="border-t border-border hover:bg-muted/50">
                                    <td className="p-4 font-medium">{project.project_name}</td>
                                    <td className="p-4 text-muted-foreground text-sm flex items-center gap-2">
                                        <Calendar size={14} />
                                        {new Date(project.created_at).toLocaleDateString()}
                                    </td>
                                    <td className="p-4 text-sm flex items-center gap-2">
                                        <User size={14} className="text-muted-foreground" />
                                        {project.created_by}
                                    </td>
                                    <td className="p-4 text-right font-mono">{project.alpha}</td>
                                    <td className="p-4 text-right font-mono">{project.forecast_count}</td>
                                    <td className={`p-4 text-right font-mono ${project.overall_mape < 15 ? 'text-green-500' : project.overall_mape < 25 ? 'text-yellow-500' : 'text-red-500'}`}>
                                        {project.overall_mape.toFixed(2)}%
                                    </td>
                                    <td className="p-4">
                                        <div className="flex justify-end gap-2">
                                            <button
                                                onClick={() => onViewDetail(project.project_name)}
                                                className="p-2 rounded hover:bg-secondary text-secondary"
                                                title="View Details"
                                            >
                                                <FileText size={16} />
                                            </button>
                                            <button
                                                onClick={() => onViewProject(project.project_name)}
                                                className="p-2 rounded hover:bg-primary text-primary"
                                                title="Regenerate"
                                            >
                                                <TrendingUp size={16} />
                                            </button>
                                            <button
                                                onClick={() => handleRenameProject(project.project_name)}
                                                className="p-2 rounded hover:bg-muted text-muted-foreground"
                                                title="Rename"
                                            >
                                                <Edit2 size={16} />
                                            </button>
                                            <button
                                                onClick={() => handleDeleteProject(project.project_name)}
                                                className="p-2 rounded hover:bg-destructive/10 text-destructive"
                                                title="Delete"
                                            >
                                                <Trash2 size={16} />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {showNewModal && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-card w-full max-w-md rounded-xl border border-border shadow-2xl p-6">
                        <h3 className="text-xl font-bold mb-4">Create New Forecast Project</h3>
                        <input
                            type="text"
                            placeholder="Project name (e.g., Q1 Forecast Analysis)"
                            value={newProjectName}
                            onChange={(e) => setNewProjectName(e.target.value)}
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:ring-2 ring-primary outline-none mb-4"
                            autoFocus
                        />
                        <div className="flex justify-end gap-3">
                            <button
                                onClick={() => setShowNewModal(false)}
                                className="px-4 py-2 text-sm font-medium hover:bg-muted rounded-md transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleCreateProject}
                                disabled={!newProjectName.trim()}
                                className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 rounded-md transition-colors disabled:opacity-50"
                            >
                                Create & Generate
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ForecastProjectManager;