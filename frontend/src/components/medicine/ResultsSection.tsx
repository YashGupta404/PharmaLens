import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MedicineCard } from "./MedicineCard";
import {
  TrendingDown,
  Package,
  Sparkles,
  ArrowRight,
  FileText,
  Loader2,
  CheckCircle2
} from "lucide-react";
import type { MedicineSearchResult, ScanStatus } from "@/types/pharmalens";

interface PharmacyStatus {
  name: string;
  completed: boolean;
  resultsCount: number;
}

interface ResultsSectionProps {
  results: MedicineSearchResult[];
  status: ScanStatus;
  extractedMedicines: string[];
  completedPharmacies?: string[];
  remainingPharmacies?: number;
  streamMessage?: string;
}

export function ResultsSection({ results, status, extractedMedicines, completedPharmacies = [], remainingPharmacies = 0, streamMessage }: ResultsSectionProps) {
  const totalSavings = results.reduce((acc, r) => acc + (r.savings || 0), 0);
  const medicinesCount = results.length;
  const cheapestOptions = results.filter(r => r.cheapestPrice).length;

  // Processing states
  if (status === 'extracting' || status === 'processing') {
    return (
      <section className="py-16">
        <div className="container mx-auto px-4">
          <Card variant="glass" className="max-w-2xl mx-auto">
            <CardContent className="p-8">
              <div className="flex flex-col items-center text-center">
                <div className="w-16 h-16 rounded-2xl bg-primary-light flex items-center justify-center mb-6 animate-pulse-glow">
                  <Loader2 className="w-8 h-8 text-primary animate-spin" />
                </div>
                <h3 className="text-xl font-semibold mb-2">
                  {status === 'processing' ? 'Processing Image...' : 'Extracting Medicines...'}
                </h3>
                <p className="text-muted-foreground mb-6">
                  {status === 'processing'
                    ? 'Our AI is reading your prescription'
                    : 'Identifying medicine names and dosages'}
                </p>

                {/* Progress Steps */}
                <div className="flex items-center gap-4 text-sm">
                  <Step label="Upload" completed />
                  <div className="w-8 h-px bg-border" />
                  <Step label="OCR" active={status === 'processing'} completed={status === 'extracting'} />
                  <div className="w-8 h-px bg-border" />
                  <Step label="Extract" active={status === 'extracting'} />
                  <div className="w-8 h-px bg-border" />
                  <Step label="Search" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>
    );
  }

  if (status === 'searching') {
    const allPharmacies = ['PharmEasy', '1mg', 'Netmeds', 'Apollo', 'Truemeds'];

    return (
      <section className="py-16">
        <div className="container mx-auto px-4">
          <Card variant="glass" className="max-w-2xl mx-auto">
            <CardContent className="p-8">
              <div className="flex flex-col items-center text-center">
                <div className="w-16 h-16 rounded-2xl bg-success-light flex items-center justify-center mb-6 animate-pulse-glow">
                  <Sparkles className="w-8 h-8 text-success" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Searching Pharmacies...</h3>

                {/* Stream message */}
                {streamMessage && (
                  <div className="bg-primary/10 border border-primary/30 rounded-lg p-3 mb-4 w-full">
                    <p className="text-sm font-medium text-primary">
                      {streamMessage}
                    </p>
                  </div>
                )}

                {/* Progress indicator */}
                <div className="bg-warning/10 border border-warning/30 rounded-lg p-4 mb-4 w-full">
                  <p className="text-lg font-bold text-warning-foreground">
                    ⏳ {completedPharmacies.length}/{allPharmacies.length} pharmacies searched
                    {remainingPharmacies > 0 && ` - ${remainingPharmacies} remaining...`}
                  </p>
                </div>

                {/* Pharmacy Status Grid */}
                <div className="w-full grid grid-cols-2 md:grid-cols-5 gap-2 mb-6">
                  {allPharmacies.map((pharmacy) => {
                    const isComplete = completedPharmacies.includes(pharmacy);
                    return (
                      <div
                        key={pharmacy}
                        className={`p-2 rounded-lg border text-sm flex items-center justify-center gap-1 ${isComplete
                          ? 'bg-success/10 border-success/30 text-success'
                          : 'bg-muted/50 border-border text-muted-foreground'
                          }`}
                      >
                        {isComplete ? (
                          <CheckCircle2 className="w-3 h-3" />
                        ) : (
                          <Loader2 className="w-3 h-3 animate-spin" />
                        )}
                        {pharmacy}
                      </div>
                    );
                  })}
                </div>

                {/* Extracted Medicines */}
                <div className="w-full text-left mb-6">
                  <p className="text-sm font-medium mb-3">Found {extractedMedicines.length} medicines:</p>
                  <div className="flex flex-wrap gap-2">
                    {extractedMedicines.map((med, idx) => (
                      <Badge key={idx} variant="primary-light" className="animate-scale-in" style={{ animationDelay: `${idx * 100}ms` }}>
                        {med}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Progress Steps */}
                <div className="flex items-center gap-4 text-sm">
                  <Step label="Upload" completed />
                  <div className="w-8 h-px bg-border" />
                  <Step label="OCR" completed />
                  <div className="w-8 h-px bg-border" />
                  <Step label="Extract" completed />
                  <div className="w-8 h-px bg-border" />
                  <Step label="Search" active />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>
    );
  }

  if (results.length === 0) {
    return null;
  }

  return (
    <section className="py-16 bg-secondary/30">
      <div className="container mx-auto px-4">
        {/* Summary Card */}
        <Card variant="gradient" className="mb-8">
          <CardContent className="p-6 md:p-8">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div>
                <h2 className="text-2xl md:text-3xl font-display font-bold mb-2">
                  Your Price Comparison Results
                </h2>
                <p className="text-muted-foreground">
                  We found the best prices for {medicinesCount} medicines from your prescription
                </p>
              </div>

              {/* Stats */}
              <div className="flex items-center gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-gradient-savings">
                    ₹{totalSavings.toFixed(0)}
                  </div>
                  <div className="text-sm text-muted-foreground">Total Savings</div>
                </div>
                <div className="h-12 w-px bg-border hidden md:block" />
                <div className="text-center">
                  <div className="text-3xl font-bold text-primary">
                    {cheapestOptions}
                  </div>
                  <div className="text-sm text-muted-foreground">Best Deals</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-3 mb-8">
          <Button variant="hero" className="gap-2">
            <TrendingDown className="w-4 h-4" />
            Buy All at Best Price
          </Button>
          <Button variant="outline" className="gap-2">
            <FileText className="w-4 h-4" />
            Export Comparison
          </Button>
          <Button variant="ghost" className="gap-2">
            <Package className="w-4 h-4" />
            View Generic Alternatives
          </Button>
        </div>

        {/* Medicine Cards */}
        <div className="grid gap-6">
          {results.map((result, index) => (
            <MedicineCard key={result.medicine.id} result={result} index={index} />
          ))}
        </div>
      </div>
    </section>
  );
}

interface StepProps {
  label: string;
  active?: boolean;
  completed?: boolean;
}

function Step({ label, active, completed }: StepProps) {
  return (
    <div className={`flex items-center gap-2 ${active ? 'text-primary' : completed ? 'text-success' : 'text-muted-foreground'}`}>
      <div className={`w-2 h-2 rounded-full ${active ? 'bg-primary animate-pulse' : completed ? 'bg-success' : 'bg-muted'}`} />
      <span className={active || completed ? 'font-medium' : ''}>{label}</span>
    </div>
  );
}
