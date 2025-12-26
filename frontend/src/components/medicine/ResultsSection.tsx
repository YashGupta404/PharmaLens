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
  Loader2
} from "lucide-react";
import type { MedicineSearchResult, ScanStatus } from "@/types/pharmalens";

interface ResultsSectionProps {
  results: MedicineSearchResult[];
  status: ScanStatus;
  extractedMedicines: string[];
}

export function ResultsSection({ results, status, extractedMedicines }: ResultsSectionProps) {
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

                {/* Prominent wait message */}
                <div className="bg-warning/10 border border-warning/30 rounded-lg p-4 mb-4">
                  <p className="text-lg font-bold text-warning-foreground">
                    ⏳ Searching medicines on 4 platforms may take 1-3 minutes. Please wait...
                  </p>
                </div>

                <p className="text-muted-foreground mb-6">
                  Comparing prices across PharmEasy, 1mg, Netmeds & Apollo for the best deals
                </p>

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
