import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, X, Search, Pill } from "lucide-react";

interface ManualMedicineInputProps {
    onSearch: (medicines: string[]) => void;
    isSearching: boolean;
}

export function ManualMedicineInput({ onSearch, isSearching }: ManualMedicineInputProps) {
    const [medicines, setMedicines] = useState<string[]>([""]);
    const MAX_MEDICINES = 5;

    const addMedicine = () => {
        if (medicines.length < MAX_MEDICINES) {
            setMedicines([...medicines, ""]);
        }
    };

    const removeMedicine = (index: number) => {
        if (medicines.length > 1) {
            setMedicines(medicines.filter((_, i) => i !== index));
        }
    };

    const updateMedicine = (index: number, value: string) => {
        const updated = [...medicines];
        updated[index] = value;
        setMedicines(updated);
    };

    const handleSearch = () => {
        const validMedicines = medicines.filter(m => m.trim().length > 0);
        if (validMedicines.length > 0) {
            onSearch(validMedicines);
        }
    };

    const hasValidInput = medicines.some(m => m.trim().length > 0);

    return (
        <Card variant="glass" className="w-full">
            <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 rounded-xl bg-primary-light flex items-center justify-center">
                        <Pill className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                        <h3 className="font-semibold text-lg">Type Medicine Names</h3>
                        <p className="text-sm text-muted-foreground">Enter medicine names manually to compare prices</p>
                    </div>
                </div>

                <div className="space-y-3">
                    {medicines.map((medicine, index) => (
                        <div key={index} className="flex gap-2">
                            <Input
                                placeholder={`Medicine ${index + 1} (e.g., Dolo 650, Pantocid 40)`}
                                value={medicine}
                                onChange={(e) => updateMedicine(index, e.target.value)}
                                disabled={isSearching}
                                className="flex-1"
                            />
                            {medicines.length > 1 && (
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={() => removeMedicine(index)}
                                    disabled={isSearching}
                                    className="shrink-0 text-muted-foreground hover:text-destructive"
                                >
                                    <X className="w-4 h-4" />
                                </Button>
                            )}
                        </div>
                    ))}

                    <div className="flex items-center justify-between pt-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={addMedicine}
                            disabled={medicines.length >= MAX_MEDICINES || isSearching}
                            className="gap-2"
                        >
                            <Plus className="w-4 h-4" />
                            Add Medicine ({medicines.length}/{MAX_MEDICINES})
                        </Button>

                        <Button
                            variant="hero"
                            onClick={handleSearch}
                            disabled={!hasValidInput || isSearching}
                            className="gap-2"
                        >
                            <Search className="w-4 h-4" />
                            {isSearching ? "Searching..." : "Find Best Prices"}
                        </Button>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
