import { useState, useEffect } from "react";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { History, Trash2, Search, Calendar, IndianRupee, Package, ExternalLink } from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import { getSession } from "@/lib/supabase";

interface SearchHistoryItem {
    id: string;
    user_id: string;
    prescription_url: string | null;
    extracted_text: string | null;
    medicines: Array<{ name: string; dosage?: string }>;
    results: Array<{
        medicine_name: string;
        prices: Array<{ pharmacy_name: string; price: number; url: string }>;
        cheapest?: { pharmacy_name: string; price: number };
    }>;
    total_savings: number;
    created_at: string;
}

const SearchHistory = () => {
    const [history, setHistory] = useState<SearchHistoryItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [token, setToken] = useState<string | null>(null);
    const navigate = useNavigate();

    useEffect(() => {
        const getAuthToken = async () => {
            const { session, error } = await getSession();
            if (error || !session) {
                console.log("No session found");
                toast.error("Please sign in to view search history");
                navigate("/auth");
                return;
            }
            console.log("Session found");
            setToken(session.access_token);
        };
        getAuthToken();
    }, [navigate]);

    useEffect(() => {
        if (token) {
            fetchHistory();
        }
    }, [token]);

    const fetchHistory = async () => {
        if (!token) {
            setLoading(false);
            return;
        }

        try {
            console.log("Fetching history...");
            const response = await fetch(`${import.meta.env.VITE_API_URL}/history`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                console.log("History loaded:", data);
                setHistory(data);
            } else if (response.status === 401) {
                toast.error("Session expired. Please sign in again.");
                navigate("/auth");
            } else {
                const errorText = await response.text();
                console.error("Failed to load history:", response.status, errorText);
            }
        } catch (error) {
            console.error("History fetch error:", error);
        } finally {
            setLoading(false);
        }
    };

    const deleteSearch = async (id: string) => {
        if (!token) return;

        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/history/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
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

    const getMedicineNames = (item: SearchHistoryItem): string[] => {
        if (item.medicines && item.medicines.length > 0) {
            return item.medicines.map(m => m.name || 'Unknown');
        }
        if (item.extracted_text) {
            return [item.extracted_text.substring(0, 50) + '...'];
        }
        return ['Unknown Medicine'];
    };

    const getCheapestInfo = (item: SearchHistoryItem) => {
        if (item.results && item.results.length > 0) {
            const firstResult = item.results[0];
            if (firstResult.cheapest) {
                return {
                    price: firstResult.cheapest.price,
                    pharmacy: firstResult.cheapest.pharmacy_name
                };
            }
        }
        return null;
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
                            {history.map((item) => {
                                const medicines = getMedicineNames(item);
                                const cheapest = getCheapestInfo(item);
                                const resultsCount = item.results?.reduce((acc, r) => acc + (r.prices?.length || 0), 0) || 0;

                                return (
                                    <Card key={item.id} className="hover:shadow-md transition-shadow">
                                        <CardHeader className="pb-3">
                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <CardTitle className="text-xl mb-2 flex items-center gap-2">
                                                        <Package className="w-5 h-5 text-primary" />
                                                        {medicines[0]}
                                                        {medicines.length > 1 && (
                                                            <Badge variant="secondary">+{medicines.length - 1} more</Badge>
                                                        )}
                                                    </CardTitle>
                                                    <div className="flex flex-wrap gap-2 text-sm text-muted-foreground">
                                                        <span className="flex items-center gap-1">
                                                            <Calendar className="w-4 h-4" />
                                                            {formatDate(item.created_at)}
                                                        </span>
                                                        <Badge variant={item.prescription_url ? 'default' : 'secondary'}>
                                                            {item.prescription_url ? '📋 Prescription' : '⌨️ Manual'}
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
                                            <div className="flex flex-wrap gap-2 mb-4">
                                                {medicines.slice(0, 5).map((med, idx) => (
                                                    <Badge key={idx} variant="outline">{med}</Badge>
                                                ))}
                                            </div>

                                            <div className="grid grid-cols-3 gap-4">
                                                <div>
                                                    <p className="text-sm text-muted-foreground mb-1">Results</p>
                                                    <p className="text-lg font-semibold">{resultsCount} prices</p>
                                                </div>
                                                {cheapest && (
                                                    <div>
                                                        <p className="text-sm text-muted-foreground mb-1">Best Price</p>
                                                        <p className="text-lg font-semibold text-green-600 flex items-center gap-1">
                                                            <IndianRupee className="w-4 h-4" />
                                                            {cheapest.price.toFixed(2)}
                                                        </p>
                                                        <p className="text-xs text-muted-foreground">{cheapest.pharmacy}</p>
                                                    </div>
                                                )}
                                                {item.total_savings > 0 && (
                                                    <div>
                                                        <p className="text-sm text-muted-foreground mb-1">Savings</p>
                                                        <p className="text-lg font-semibold text-primary flex items-center gap-1">
                                                            <IndianRupee className="w-4 h-4" />
                                                            {item.total_savings.toFixed(2)}
                                                        </p>
                                                    </div>
                                                )}
                                            </div>

                                            {item.prescription_url && (
                                                <div className="mt-4 flex items-center gap-4">
                                                    <img
                                                        src={item.prescription_url}
                                                        alt="Prescription"
                                                        className="w-20 h-20 object-cover rounded border"
                                                    />
                                                    <a
                                                        href={item.prescription_url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="text-sm text-primary flex items-center gap-1 hover:underline"
                                                    >
                                                        View full image <ExternalLink className="w-3 h-3" />
                                                    </a>
                                                </div>
                                            )}
                                        </CardContent>
                                    </Card>
                                );
                            })}
                        </div>
                    )}
                </div>
            </main>

            <Footer />
        </div>
    );
};

export default SearchHistory;
