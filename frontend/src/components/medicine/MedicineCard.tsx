import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Pill, 
  TrendingDown, 
  ExternalLink, 
  ChevronDown, 
  ChevronUp,
  Sparkles,
  AlertTriangle,
  Check,
  Truck,
  Star
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";
import type { MedicineSearchResult, PharmacyPrice } from "@/types/pharmalens";

interface MedicineCardProps {
  result: MedicineSearchResult;
  index: number;
}

export function MedicineCard({ result, index }: MedicineCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const { medicine, prices, cheapestPrice, genericAlternatives, savings } = result;

  const sortedPrices = [...prices].sort((a, b) => a.price - b.price);
  const displayedPrices = isExpanded ? sortedPrices : sortedPrices.slice(0, 3);
  const maxPrice = Math.max(...prices.map(p => p.price));

  return (
    <Card 
      variant="elevated" 
      className="overflow-hidden animate-fade-in-up"
      style={{ animationDelay: `${index * 100}ms` }}
    >
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="w-12 h-12 rounded-xl bg-primary-light flex items-center justify-center flex-shrink-0">
              <Pill className="w-6 h-6 text-primary" />
            </div>
            <div>
              <CardTitle className="text-lg">{medicine.name}</CardTitle>
              <p className="text-sm text-muted-foreground mt-0.5">
                {medicine.dosage} {medicine.frequency && `• ${medicine.frequency}`}
              </p>
              {medicine.genericName && (
                <Badge variant="muted" className="mt-2 text-xs">
                  Generic: {medicine.genericName}
                </Badge>
              )}
            </div>
          </div>

          {savings && savings > 0 && (
            <Badge variant="success" className="gap-1 flex-shrink-0">
              <TrendingDown className="w-3 h-3" />
              Save ₹{savings.toFixed(0)}
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Price Comparison */}
        <div className="space-y-2">
          {displayedPrices.map((price, idx) => (
            <PharmacyPriceRow 
              key={price.pharmacyId} 
              price={price} 
              isCheapest={idx === 0}
              maxPrice={maxPrice}
            />
          ))}
        </div>

        {/* Expand/Collapse */}
        {prices.length > 3 && (
          <Button
            variant="ghost"
            size="sm"
            className="w-full text-muted-foreground"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? (
              <>
                <ChevronUp className="w-4 h-4 mr-1" />
                Show Less
              </>
            ) : (
              <>
                <ChevronDown className="w-4 h-4 mr-1" />
                Show {prices.length - 3} More Options
              </>
            )}
          </Button>
        )}

        {/* Generic Alternatives */}
        {genericAlternatives && genericAlternatives.length > 0 && (
          <div className="pt-4 border-t border-border">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="w-4 h-4 text-accent" />
              <span className="text-sm font-medium">Generic Alternatives</span>
              <Badge variant="accent-light" className="text-xs">
                Save More
              </Badge>
            </div>
            <div className="space-y-2">
              {genericAlternatives.slice(0, 2).map((alt) => (
                <div 
                  key={alt.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-accent-light/50 border border-accent/20"
                >
                  <div>
                    <p className="font-medium text-sm">{alt.name}</p>
                    <p className="text-xs text-muted-foreground">{alt.composition}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-accent">
                      ₹{alt.priceRange.min} - ₹{alt.priceRange.max}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {alt.pharmaciesCount} pharmacies
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

interface PharmacyPriceRowProps {
  price: PharmacyPrice;
  isCheapest: boolean;
  maxPrice: number;
}

function PharmacyPriceRow({ price, isCheapest, maxPrice }: PharmacyPriceRowProps) {
  const savingsPercent = price.originalPrice 
    ? Math.round((1 - price.price / price.originalPrice) * 100)
    : null;
  
  const priceBarWidth = (price.price / maxPrice) * 100;

  return (
    <div 
      className={cn(
        "relative p-4 rounded-xl border transition-all duration-200",
        isCheapest 
          ? "bg-success-light border-success/30" 
          : "bg-secondary/50 border-transparent hover:border-border"
      )}
    >
      {/* Price Bar Background */}
      <div 
        className={cn(
          "absolute left-0 top-0 bottom-0 rounded-xl transition-all duration-500",
          isCheapest ? "bg-success/10" : "bg-primary/5"
        )}
        style={{ width: `${priceBarWidth}%` }}
      />

      <div className="relative flex items-center justify-between gap-4">
        <div className="flex items-center gap-3 min-w-0">
          {/* Pharmacy Logo */}
          <div className={cn(
            "w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 font-bold text-sm",
            isCheapest ? "bg-success text-success-foreground" : "bg-muted text-muted-foreground"
          )}>
            {price.pharmacyName.charAt(0)}
          </div>

          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-medium truncate">{price.pharmacyName}</span>
              {isCheapest && (
                <Badge variant="success" className="text-[10px] px-1.5 py-0">
                  BEST
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground mt-0.5">
              <span>{price.packSize}</span>
              {price.inStock ? (
                <span className="flex items-center gap-1 text-success">
                  <Check className="w-3 h-3" />
                  In Stock
                </span>
              ) : (
                <span className="flex items-center gap-1 text-warning">
                  <AlertTriangle className="w-3 h-3" />
                  Limited
                </span>
              )}
              {price.deliveryDays && (
                <span className="flex items-center gap-1">
                  <Truck className="w-3 h-3" />
                  {price.deliveryDays}d
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0">
          <div className="text-right">
            <div className="flex items-center gap-2">
              <span className={cn(
                "font-bold text-lg",
                isCheapest ? "text-success" : "text-foreground"
              )}>
                ₹{price.price.toFixed(0)}
              </span>
              {price.originalPrice && (
                <span className="text-sm text-muted-foreground line-through">
                  ₹{price.originalPrice.toFixed(0)}
                </span>
              )}
            </div>
            {savingsPercent && (
              <span className="text-xs text-success">
                {savingsPercent}% off
              </span>
            )}
          </div>

          <Button 
            variant={isCheapest ? "savings" : "outline"} 
            size="sm"
            className="gap-1"
            asChild
          >
            <a href={price.url} target="_blank" rel="noopener noreferrer">
              Buy
              <ExternalLink className="w-3 h-3" />
            </a>
          </Button>
        </div>
      </div>
    </div>
  );
}
