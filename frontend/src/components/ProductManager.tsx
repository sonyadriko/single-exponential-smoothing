import { useState, useEffect } from 'react';
import { Plus, Trash2, Package } from 'lucide-react';
import axios from 'axios';

interface Product {
    id: number;
    name: string;
    created_at: string;
}

interface ProductManagerProps {
    token: string;
}

const ProductManager: React.FC<ProductManagerProps> = ({ token }) => {
    const [products, setProducts] = useState<Product[]>([]);
    const [newProductName, setNewProductName] = useState('');
    const [loading, setLoading] = useState(false);

    const fetchProducts = async () => {
        try {
            const response = await axios.get('http://127.0.0.1:8000/products', {
                headers: { Authorization: `Bearer ${token}` }
            });
            setProducts(response.data);
        } catch (err: any) {
            alert('Failed to fetch products: ' + (err.response?.data?.detail || err.message));
        }
    };

    useEffect(() => {
        fetchProducts();
    }, []);

    const handleAddProduct = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newProductName.trim()) return;

        try {
            await axios.post(
                'http://127.0.0.1:8000/products',
                { name: newProductName },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            setNewProductName('');
            fetchProducts();
        } catch (err: any) {
            alert('Failed to add product: ' + (err.response?.data?.detail || err.message));
        }
    };

    const handleDeleteProduct = async (productId: number) => {
        if (!confirm('Are you sure you want to delete this product?')) return;

        try {
            await axios.delete(`http://127.0.0.1:8000/products/${productId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            fetchProducts();
        } catch (err: any) {
            alert('Failed to delete product: ' + (err.response?.data?.detail || err.message));
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">Manage Products</h2>
                    <p className="text-muted-foreground text-sm">Add and manage your product catalog</p>
                </div>
            </div>

            <form onSubmit={handleAddProduct} className="flex gap-4">
                <input
                    type="text"
                    placeholder="Enter product name"
                    value={newProductName}
                    onChange={(e) => setNewProductName(e.target.value)}
                    className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm focus:ring-2 ring-primary outline-none flex-1 max-w-md"
                />
                <button
                    type="submit"
                    className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
                >
                    <Plus size={16} /> Add Product
                </button>
            </form>

            <div className="bg-card border border-border rounded-xl overflow-hidden">
                <table className="w-full">
                    <thead className="bg-muted">
                        <tr>
                            <th className="text-left p-4 font-semibold">Product Name</th>
                            <th className="text-left p-4 font-semibold">Created At</th>
                            <th className="text-right p-4 font-semibold">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {products.map((product) => (
                            <tr key={product.id} className="border-t border-border">
                                <td className="p-4 flex items-center gap-2">
                                    <Package size={16} className="text-muted-foreground" />
                                    {product.name}
                                </td>
                                <td className="p-4 text-muted-foreground text-sm">
                                    {new Date(product.created_at).toLocaleDateString()}
                                </td>
                                <td className="p-4 text-right">
                                    <button
                                        onClick={() => handleDeleteProduct(product.id)}
                                        className="text-destructive hover:bg-destructive/10 p-2 rounded transition-colors"
                                    >
                                        <Trash2 size={16} />
                                    </button>
                                </td>
                            </tr>
                        ))}
                        {products.length === 0 && (
                            <tr>
                                <td colSpan={3} className="p-8 text-center text-muted-foreground">
                                    No products found. Add your first product above.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default ProductManager;