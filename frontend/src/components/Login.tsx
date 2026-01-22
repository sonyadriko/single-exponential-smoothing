import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Lock, User, Loader2 } from 'lucide-react';
import { cn } from '../lib/utils';
import { jwtDecode } from 'jwt-decode';

interface LoginProps {
    setToken: (token: string) => void;
    setUserRole: (role: string) => void;
}

const Login: React.FC<LoginProps> = ({ setToken, setUserRole }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const response = await axios.post('http://127.0.0.1:8000/token', formData);
            const token = response.data.access_token;

            setToken(token);
            localStorage.setItem('token', token);

            // Decode token to get role
            const decoded: any = jwtDecode(token);
            const role = decoded.role;
            setUserRole(role);
            localStorage.setItem('role', role);

            navigate('/dashboard');
        } catch (err: any) {
            setError('Invalid username or password');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4">
            <div className="w-full max-w-md bg-card border border-border rounded-xl shadow-2xl p-8 space-y-8 animate-in fade-in zoom-in duration-500">
                <div className="text-center space-y-2">
                    <h1 className="text-3xl font-extrabold text-primary">
                        Depot Jawara
                    </h1>
                    <p className="text-muted-foreground">Sales Forecasting System</p>
                </div>

                <form onSubmit={handleLogin} className="space-y-6">
                    <div className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                Username
                            </label>
                            <div className="relative">
                                <User className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
                                <input
                                    type="text"
                                    placeholder="admin"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 pl-10 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                    required
                                />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
                                <input
                                    type="password"
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 pl-10 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                    required
                                />
                            </div>
                        </div>
                    </div>

                    {error && (
                        <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md flex items-center justify-center font-medium">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className={cn(
                            "w-full h-11 rounded-md font-bold text-primary-foreground transition-all flex items-center justify-center gap-2",
                            loading ? "bg-muted cursor-not-allowed" : "bg-primary hover:bg-primary/90"
                        )}
                    >
                        {loading ? <Loader2 className="animate-spin h-5 w-5" /> : "Sign In"}
                    </button>
                </form>

                <div className="text-center text-xs text-muted-foreground">
                    <p>Demo Credentials:</p>
                    <div className="mt-2 grid grid-cols-2 gap-2 text-left bg-muted/50 p-2 rounded">
                        <div><span className="font-bold">admin</span> / admin123</div>
                        <div><span className="font-bold">owner</span> / owner123</div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
