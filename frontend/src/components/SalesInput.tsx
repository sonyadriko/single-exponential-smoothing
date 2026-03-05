import { useState, useEffect, useMemo } from 'react';
import { Plus, Trash2, Calendar, TrendingUp, Filter, X } from 'lucide-react';
import { toast } from 'sonner';
import api from '../api';

interface Sale {
    id: number;
    date: string;
    product_name: string;
    qty: number;
}

interface Product {
    id: number;
    name: string;
}

interface SalesInputProps {
    token: string;
}

type FilterPreset = 'all' | 'thisMonth' | 'lastMonth' | 'custom';

const SalesInput: React.FC<SalesInputProps> = ({ token: _token }) => {
    const [products, setProducts] = useState<Product[]>([]);
    const [selectedProduct, setSelectedProduct] = useState<string>('');
    const [sales, setSales] = useState<Sale[]>([]);
    const [newSale, setNewSale] = useState({
        date: new Date().toISOString().split('T')[0], // YYYY-MM-DD format for date picker
        qty: 0
    });
    const [filterPreset, setFilterPreset] = useState<FilterPreset>('all');
    const [startDate, setStartDate] = useState<string>('');
    const [endDate, setEndDate] = useState<string>('');

    // Convert date picker format (YYYY-MM-DD) to backend format (DD-MMM-YY)
    const convertToBackendFormat = (dateStr: string): string => {
        const date = new Date(dateStr);
        const day = String(date.getDate()).padStart(2, '0');
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const month = months[date.getMonth()];
        const year = String(date.getFullYear()).slice(-2);
        return `${day}-${month}-${year}`;
    };

    // Convert backend format (DD-MMM-YY) to date picker format (YYYY-MM-DD) for comparison
    const convertFromBackendFormat = (backendDate: string): Date => {
        const parts = backendDate.split('-');
        const day = parseInt(parts[0]);
        const monthMap: Record<string, number> = {
            'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'Jun': 5,
            'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11
        };
        const month = monthMap[parts[1]];
        const year = parseInt('20' + parts[2]); // Convert YY to 20YY
        return new Date(year, month, day);
    };

    // Quick filter presets
    const applyFilterPreset = (preset: FilterPreset) => {
        const today = new Date();
        const firstDayThisMonth = new Date(today.getFullYear(), today.getMonth(), 1);
        const firstDayLastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1);
        const lastDayLastMonth = new Date(today.getFullYear(), today.getMonth(), 0);

        switch (preset) {
            case 'thisMonth':
                setFilterPreset('thisMonth');
                setStartDate(firstDayThisMonth.toISOString().split('T')[0]);
                setEndDate(today.toISOString().split('T')[0]);
                break;
            case 'lastMonth':
                setFilterPreset('lastMonth');
                setStartDate(firstDayLastMonth.toISOString().split('T')[0]);
                setEndDate(lastDayLastMonth.toISOString().split('T')[0]);
                break;
            case 'all':
                setFilterPreset('all');
                setStartDate('');
                setEndDate('');
                break;
            case 'custom':
                setFilterPreset('custom');
                break;
        }
    };

    // Filter sales by date range
    const filteredSales = useMemo(() => {
        if (!startDate && !endDate) return sales;

        return sales.filter(sale => {
            const saleDate = convertFromBackendFormat(sale.date);
            const start = startDate ? new Date(startDate) : new Date(0);
            const end = endDate ? new Date(endDate) : new Date();

            // Reset time portion for accurate comparison
            start.setHours(0, 0, 0, 0);
            end.setHours(23, 59, 59, 999);
            saleDate.setHours(12, 0, 0, 0); // Noon to avoid timezone issues

            return saleDate >= start && saleDate <= end;
        });
    }, [sales, startDate, endDate]);

    useEffect(() => {
        fetchProducts();
    }, []);

    useEffect(() => {
        if (selectedProduct) {
            fetchSales();
        }
    }, [selectedProduct]);

    const fetchProducts = async () => {
        try {
            const response = await api.get('/products');
            setProducts(response.data);
            if (response.data.length > 0 && !selectedProduct) {
                setSelectedProduct(response.data[0].name);
            }
        } catch (err: any) {
            toast.error('Gagal memuat produk', {
                description: err.response?.data?.detail || err.message
            });
        }
    };

    const fetchSales = async () => {
        if (!selectedProduct) return;
        try {
            const response = await api.get(`/sales/product/${encodeURIComponent(selectedProduct)}`);
            setSales(response.data);
        } catch (err: any) {
            console.error('Failed to fetch sales:', err);
        }
    };

    const handleAddSale = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedProduct || newSale.qty <= 0) return;

        try {
            await api.post('/sales', {
                date: convertToBackendFormat(newSale.date), // Convert to backend format
                product_name: selectedProduct,
                qty: newSale.qty
            });
            setNewSale({ ...newSale, qty: 0 });
            fetchSales();
            toast.success('Data penjualan berhasil ditambahkan');
        } catch (err: any) {
            toast.error('Gagal menambahkan data penjualan', {
                description: err.response?.data?.detail || err.message
            });
        }
    };

    const handleDeleteSale = async (saleId: number) => {
        try {
            await api.delete(`/sales/${saleId}`);
            fetchSales();
            toast.success('Data penjualan berhasil dihapus');
        } catch (err: any) {
            toast.error('Gagal menghapus data penjualan', {
                description: err.response?.data?.detail || err.message
            });
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold">Input Sales Data</h2>
                <p className="text-muted-foreground text-sm">Add daily sales data for each product</p>
            </div>

            <div className="bg-card border border-border rounded-xl p-6 space-y-4">
                <div>
                    <label className="text-sm font-medium">Select Product</label>
                    <select
                        value={selectedProduct}
                        onChange={(e) => setSelectedProduct(e.target.value)}
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:ring-2 ring-primary outline-none mt-2"
                    >
                        <option value="">-- Select Product --</option>
                        {products.map((p) => (
                            <option key={p.id} value={p.name}>{p.name}</option>
                        ))}
                    </select>
                </div>

                {selectedProduct && (
                    <>
                        <form onSubmit={handleAddSale} className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label className="text-sm font-medium">Date</label>
                                <input
                                    type="date"
                                    value={newSale.date}
                                    onChange={(e) => setNewSale({ ...newSale, date: e.target.value })}
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:ring-2 ring-primary outline-none mt-2"
                                    required
                                />
                            </div>
                            <div>
                                <label className="text-sm font-medium">Quantity Sold</label>
                                <input
                                    type="number"
                                    min="0"
                                    value={newSale.qty}
                                    onChange={(e) => setNewSale({ ...newSale, qty: parseInt(e.target.value) || 0 })}
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:ring-2 ring-primary outline-none mt-2"
                                    required
                                />
                            </div>
                            <div className="flex items-end">
                                <button
                                    type="submit"
                                    className="flex items-center justify-center gap-2 w-full h-10 px-4 py-2 rounded-lg text-sm bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
                                >
                                    <Plus size={16} /> Add Sale
                                </button>
                            </div>
                        </form>

                        <div className="bg-muted/50 rounded-lg p-4">
                            <h3 className="font-semibold mb-3 flex items-center gap-2">
                                <TrendingUp size={18} />
                                Sales History: {selectedProduct}
                            </h3>

                            {/* Filter Controls */}
                            <div className="mb-4 space-y-3">
                                <div className="flex items-center gap-2 mb-2">
                                    <Filter size={16} className="text-muted-foreground" />
                                    <span className="text-sm font-medium">Filter by Date:</span>
                                </div>

                                {/* Quick Filter Buttons */}
                                <div className="flex flex-wrap gap-2">
                                    <button
                                        onClick={() => applyFilterPreset('all')}
                                        className={`px-3 py-1.5 text-xs rounded-md transition-colors ${
                                            filterPreset === 'all'
                                                ? 'bg-primary text-primary-foreground'
                                                : 'bg-background hover:bg-muted'
                                        }`}
                                    >
                                        All Time
                                    </button>
                                    <button
                                        onClick={() => applyFilterPreset('thisMonth')}
                                        className={`px-3 py-1.5 text-xs rounded-md transition-colors ${
                                            filterPreset === 'thisMonth'
                                                ? 'bg-primary text-primary-foreground'
                                                : 'bg-background hover:bg-muted'
                                        }`}
                                    >
                                        This Month
                                    </button>
                                    <button
                                        onClick={() => applyFilterPreset('lastMonth')}
                                        className={`px-3 py-1.5 text-xs rounded-md transition-colors ${
                                            filterPreset === 'lastMonth'
                                                ? 'bg-primary text-primary-foreground'
                                                : 'bg-background hover:bg-muted'
                                        }`}
                                    >
                                        Last Month
                                    </button>
                                    <button
                                        onClick={() => applyFilterPreset('custom')}
                                        className={`px-3 py-1.5 text-xs rounded-md transition-colors ${
                                            filterPreset === 'custom'
                                                ? 'bg-primary text-primary-foreground'
                                                : 'bg-background hover:bg-muted'
                                        }`}
                                    >
                                        Custom
                                    </button>
                                    {(startDate || endDate) && (
                                        <button
                                            onClick={() => applyFilterPreset('all')}
                                            className="px-3 py-1.5 text-xs rounded-md bg-destructive/10 text-destructive hover:bg-destructive/20 flex items-center gap-1"
                                        >
                                            <X size={12} /> Clear
                                        </button>
                                    )}
                                </div>

                                {/* Custom Date Range */}
                                {filterPreset === 'custom' && (
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2">
                                        <div>
                                            <label className="text-xs text-muted-foreground">From:</label>
                                            <input
                                                type="date"
                                                value={startDate}
                                                onChange={(e) => setStartDate(e.target.value)}
                                                className="flex h-8 w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:ring-2 ring-primary outline-none mt-1"
                                            />
                                        </div>
                                        <div>
                                            <label className="text-xs text-muted-foreground">To:</label>
                                            <input
                                                type="date"
                                                value={endDate}
                                                onChange={(e) => setEndDate(e.target.value)}
                                                className="flex h-8 w-full rounded-md border border-input bg-background px-2 py-1 text-xs focus:ring-2 ring-primary outline-none mt-1"
                                            />
                                        </div>
                                    </div>
                                )}

                                {/* Active Filter Summary */}
                                {(startDate || endDate) && filterPreset !== 'all' && (
                                    <div className="text-xs text-muted-foreground bg-background rounded px-2 py-1">
                                        Showing: {startDate || '...'} to {endDate || '...'}
                                        <span className="ml-2">({filteredSales.length} of {sales.length} records)</span>
                                    </div>
                                )}
                            </div>

                            {/* Sales Table */}
                            <div className="max-h-64 overflow-y-auto">
                                <table className="w-full">
                                    <thead className="text-xs text-muted-foreground">
                                        <tr>
                                            <th className="text-left p-2">Date</th>
                                            <th className="text-left p-2">Qty</th>
                                            <th className="text-right p-2">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {filteredSales.map((sale) => (
                                            <tr key={sale.id} className="border-t border-border">
                                                <td className="p-2 flex items-center gap-2">
                                                    <Calendar size={14} className="text-muted-foreground" />
                                                    {sale.date}
                                                </td>
                                                <td className="p-2 font-mono">{sale.qty}</td>
                                                <td className="p-2 text-right">
                                                    <button
                                                        onClick={() => handleDeleteSale(sale.id)}
                                                        className="text-destructive hover:bg-destructive/10 p-1 rounded transition-colors"
                                                    >
                                                        <Trash2 size={14} />
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                        {filteredSales.length === 0 && sales.length > 0 && (
                                            <tr>
                                                <td colSpan={3} className="p-4 text-center text-muted-foreground text-sm">
                                                    No sales data found for the selected date range.
                                                </td>
                                            </tr>
                                        )}
                                        {sales.length === 0 && (
                                            <tr>
                                                <td colSpan={3} className="p-4 text-center text-muted-foreground text-sm">
                                                    No sales data for this product yet.
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default SalesInput;