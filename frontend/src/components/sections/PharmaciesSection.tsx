import { Badge } from "@/components/ui/badge";
import { Star, Shield, Truck } from "lucide-react";

const pharmacies = [
  { name: "1mg", rating: 4.5, reviews: "2.5L" },
  { name: "PharmEasy", rating: 4.4, reviews: "1.8L" },
  { name: "Netmeds", rating: 4.3, reviews: "1.2L" },
  { name: "Apollo", rating: 4.6, reviews: "90K" },
  { name: "Tata 1mg", rating: 4.5, reviews: "2.1L" },
  { name: "MedPlus", rating: 4.2, reviews: "75K" },
];

export function PharmaciesSection() {
  return (
    <section className="py-16 border-t border-border">
      <div className="container mx-auto px-4">
        <div className="text-center mb-10">
          <h2 className="text-2xl md:text-3xl font-display font-bold mb-3">
            Trusted Pharmacy Partners
          </h2>
          <p className="text-muted-foreground">
            We compare prices from India's most trusted online pharmacies
          </p>
        </div>

        {/* Pharmacy Logos */}
        <div className="flex flex-wrap items-center justify-center gap-6 md:gap-10 mb-10">
          {pharmacies.map((pharmacy, index) => (
            <div 
              key={index}
              className="flex flex-col items-center gap-2 p-4 rounded-xl hover:bg-secondary/50 transition-colors"
            >
              <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-primary-light to-secondary flex items-center justify-center font-bold text-lg text-primary">
                {pharmacy.name.charAt(0)}
              </div>
              <span className="font-medium text-sm">{pharmacy.name}</span>
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Star className="w-3 h-3 text-warning fill-warning" />
                <span>{pharmacy.rating}</span>
                <span>({pharmacy.reviews})</span>
              </div>
            </div>
          ))}
        </div>

        {/* Trust Badges */}
        <div className="flex flex-wrap items-center justify-center gap-4">
          <Badge variant="outline" className="gap-2 px-4 py-2">
            <Shield className="w-4 h-4 text-success" />
            All Pharmacies Verified
          </Badge>
          <Badge variant="outline" className="gap-2 px-4 py-2">
            <Truck className="w-4 h-4 text-primary" />
            Pan-India Delivery
          </Badge>
          <Badge variant="outline" className="gap-2 px-4 py-2">
            <Star className="w-4 h-4 text-warning fill-warning" />
            4.5+ Average Rating
          </Badge>
        </div>
      </div>
    </section>
  );
}
