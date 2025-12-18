import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Upload, Sparkles, TrendingDown, Shield, Zap } from "lucide-react";

interface HeroSectionProps {
  onUploadClick: () => void;
}

export function HeroSection({ onUploadClick }: HeroSectionProps) {
  return (
    <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden pt-20">
      {/* Background Elements */}
      <div className="absolute inset-0 -z-10">
        {/* Gradient Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary-light via-background to-success-light opacity-60" />
        
        {/* Animated Circles */}
        <div className="absolute top-20 left-10 w-72 h-72 rounded-full bg-primary/10 blur-3xl animate-float" />
        <div className="absolute bottom-20 right-10 w-96 h-96 rounded-full bg-success/10 blur-3xl animate-float delay-500" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-accent/5 blur-3xl" />
        
        {/* Grid Pattern */}
        <div 
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `radial-gradient(circle at 1px 1px, currentColor 1px, transparent 0)`,
            backgroundSize: '40px 40px'
          }}
        />
      </div>

      <div className="container mx-auto px-4 py-12 md:py-20">
        <div className="max-w-4xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 mb-6 animate-fade-in-up">
            <Badge variant="success-light" className="px-4 py-1.5 text-sm gap-1.5">
              <TrendingDown className="w-3.5 h-3.5" />
              Save up to 80% on medicines
            </Badge>
          </div>

          {/* Headline */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-display font-bold tracking-tight mb-6 animate-fade-in-up delay-100">
            Find the{" "}
            <span className="text-gradient-hero">Cheapest</span>
            <br />
            Medicine Prices{" "}
            <span className="text-gradient-savings">Instantly</span>
          </h1>

          {/* Subheadline */}
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-8 animate-fade-in-up delay-200">
            Upload your prescription and let our AI scan multiple pharmacies across India 
            to find you the best deals. Compare prices, discover generic alternatives, 
            and save money on every purchase.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12 animate-fade-in-up delay-300">
            <Button variant="hero" size="xl" className="gap-2 w-full sm:w-auto" onClick={onUploadClick}>
              <Upload className="w-5 h-5" />
              Upload Prescription
            </Button>
            <Button variant="glass" size="xl" className="gap-2 w-full sm:w-auto">
              <Sparkles className="w-5 h-5" />
              See How It Works
            </Button>
          </div>

          {/* Trust Indicators */}
          <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-muted-foreground animate-fade-in-up delay-400">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-success" />
              <span>100% Secure</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-warning" />
              <span>Instant Results</span>
            </div>
            <div className="flex items-center gap-2">
              <TrendingDown className="w-4 h-4 text-accent" />
              <span>Best Price Guarantee</span>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-16 animate-fade-in-up delay-500">
            {[
              { value: "50K+", label: "Prescriptions Scanned" },
              { value: "₹2Cr+", label: "Customer Savings" },
              { value: "15+", label: "Pharmacies Compared" },
              { value: "4.9★", label: "User Rating" },
            ].map((stat, index) => (
              <div 
                key={index} 
                className="p-4 rounded-xl glass border border-border/50"
              >
                <div className="text-2xl md:text-3xl font-display font-bold text-gradient-hero">
                  {stat.value}
                </div>
                <div className="text-xs md:text-sm text-muted-foreground mt-1">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
