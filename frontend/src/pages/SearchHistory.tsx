import { useState, useEffect } from "react";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { History, Trash2, Search, Calendar, IndianRupee, Package } from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

interface SearchHistoryItem {
    id: string;
    medicine_name: string;
    search_type: string;
    results_count: number;
    cheapest_price: number | null;
    cheapest_pharmacy: string | null;
    prescription_image_url: string | null;
    created_at: string;
}

const SearchHistory = () => {
    const [history, setHistory] = useState<SearchHistoryItem[]>([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/history`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setHistory(data);
            } else if (response.status === 401) {
                toast.error("Please sign in to view search history");
                navigate("/auth");
            }
        } catch (error) {
            toast.error("Failed to load search history");
        } finally {
            setLoading(false);
        }
    };

    const deleteSearch = async (id: string) => {
        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/history/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`
                }
            });

            if (response.ok) {
                setHistory(history.filter(item => item.id !== id));
                toast.success("Search deleted");
            } else {
                toast.error("Failed to delete search");
            }
        } catch (error) {
            toast.error("Failed to delete search");
        }
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-IN', {
            day: 'numeric',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    if (loading) {
        return (
            <div className="min-h-screen flex flex-col">
                <Header />
                <main className="flex-1 flex items-center justify-center">
                    <div className="text-center">
                        <History className="w-12 h-12 mx-auto mb-4 animate-pulse text-primary" />
                        <p className="text-muted-foreground">Loading search history...</p>
                    </div>
                </main>
                <Footer />
            </div>
        );
    }

    return (
        <div className="min-h-screen flex flex-col bg-gradient-to-b from-background to-muted/20">
            <Header />

            <main className="flex-1 py-20 px-4">
                <div className="max-w-4xl mx-auto">
                    {/* Header */}
                    <div className="mb-8">
                        <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
                            <History className="w-10 h-10 text-primary" />
                            Search History
                        </h1>
                        <p className="text-muted-foreground">
                            View your past medicine searches and price comparisons
                        </p>
                    </div>

                    {/* History List */}
                    {history.length === 0 ? (
                        <Card className="text-center py-12">
                            <CardContent>
                                <Search className="w-16 h-16 mx-auto mb-4 text-muted-foreground/50" />
                                <h3 className="text-xl font-semibold mb-2">No search history yet</h3>
                                <p className="text-muted-foreground mb-6">
                                    Start searching for medicines to build your history
                                </p>
                                <Button onClick={() => navigate("/")}>
                                    Search Medicines
                                </Button>
                            </CardContent>
                        </Card>
                    ) : (
                        <div className="space-y-4">
                            {history.map((item) => (
                                <Card key={item.id} className="hover:shadow-md transition-shadow">
                                    <CardHeader className="pb-3">
                                        <div className="flex items-start justify-between">
                                            <div className="flex-1">
                                                <CardTitle className="text-xl mb-2 flex items-center gap-2">
                                                    <Package className="w-5 h-5 text-primary" />
                                                    {item.medicine_name}
                                                </CardTitle>
                                                <div className="flex flex-wrap gap-2 text-sm text-muted-foreground">
                                                    <span className="flex items-center gap-1">
                                                        <Calendar className="w-4 h-4" />
                                                        {formatDate(item.created_at)}
                                                    </span>
                                                    <Badge variant={item.search_type === 'prescription' ? 'default' : 'secondary'}>
                                                        {item.search_type === 'prescription' ? '📋 Prescription' : '⌨️ Manual'}
                                                    </Badge>
                                                </div>
                                            </div>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                onClick={() => deleteSearch(item.id)}
                                                className="text-destructive hover:text-destructive"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </Button>
                                        </div>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <p className="text-sm text-muted-foreground mb-1">Results Found</p>
                                                <p className="text-lg font-semibold">{item.results_count} options</p>
                                            </div>
                                            {item.cheapest_price && (
                                                <div>
                                                    <p className="text-sm text-muted-foreground mb-1">Best Price</p>
                                                    <p className="text-lg font-semibold text-green-600 flex items-center gap-1">
                                                        <IndianRupee className="w-4 h-4" />
                                                        {item.cheapest_price.toFixed(2)}
                                                    </p>
                                                    {item.cheapest_pharmacy && (
                                                        <p className="text-xs text-muted-foreground">at {item.cheapest_pharmacy}</p>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                        {item.prescription_image_url && (
                                            <div className="mt-4">
                                                <img
                                                    src={item.prescription_image_url}
                                                    alt="Prescription"
                                                    className="w-24 h-24 object-cover rounded border"
                                                />
                                            </div>
                                        )}
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    )}
                </div>
            </main>

            <Footer />
        </div>
    );
};

export default SearchHistory;
