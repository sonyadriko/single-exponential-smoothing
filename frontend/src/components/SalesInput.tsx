import { useState, useEffect } from 'react';
import { Plus, Trash2, Calendar, TrendingUp } from 'lucide-react';
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

const SalesInput: React.FC<SalesInputProps> = ({ token: _token }) => {
    const [products, setProducts] = useState<Product[]>([]);
    const [selectedProduct, setSelectedProduct] = useState<string>('');
    const [sales, setSales] = useState<Sale[]>([]);
    const [newSale, setNewSale] = useState({
        date: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: '2-digit' }).replace(/ /g, '-'),
        qty: 0
    });

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
            alert('Failed to fetch products: ' + (err.response?.data?.detail || err.message));
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
                date: newSale.date,
                product_name: selectedProduct,
                qty: newSale.qty
            });
            setNewSale({ ...newSale, qty: 0 });
            fetchSales();
        } catch (err: any) {
            alert('Failed to add sale: ' + (err.response?.data?.detail || err.message));
        }
    };

    const handleDeleteSale = async (saleId: number) => {
        if (!confirm('Delete this sale record?')) return;
        try {
            await api.delete(`/sales/${saleId}`);
            fetchSales();
        } catch (err: any) {
            alert('Failed to delete sale: ' + (err.response?.data?.detail || err.message));
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
                                <label className="text-sm font-medium">Date (DD-MMM-YY)</label>
                                <input
                                    type="text"
                                    placeholder="01-Jun-25"
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
                                        {sales.map((sale) => (
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