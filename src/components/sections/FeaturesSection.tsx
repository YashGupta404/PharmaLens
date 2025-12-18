import { Card, CardContent } from "@/components/ui/card";
import { 
  Scan, 
  Search, 
  TrendingDown, 
  ShieldCheck,
  Zap,
  Sparkles
} from "lucide-react";

const features = [
  {
    icon: Scan,
    title: "AI-Powered OCR",
    description: "Our advanced AI reads and extracts medicine names from any prescription image with 99% accuracy.",
    color: "primary"
  },
  {
    icon: Search,
    title: "Multi-Pharmacy Search",
    description: "We search 15+ online pharmacies including 1mg, PharmEasy, Netmeds, and Apollo to find the best prices.",
    color: "accent"
  },
  {
    icon: TrendingDown,
    title: "Price Comparison",
    description: "See real-time price comparisons with discounts, pack sizes, and delivery times at a glance.",
    color: "success"
  },
  {
    icon: Sparkles,
    title: "Generic Alternatives",
    description: "Discover cheaper generic alternatives with the same composition and save even more money.",
    color: "warning"
  },
  {
    icon: Zap,
    title: "Instant Results",
    description: "Get complete price comparisons in seconds, not minutes. Time is money, and we save you both.",
    color: "accent"
  },
  {
    icon: ShieldCheck,
    title: "Verified Pharmacies",
    description: "All pharmacies are licensed and verified. Your health and safety is our top priority.",
    color: "primary"
  }
];

const colorClasses = {
  primary: "bg-primary-light text-primary",
  accent: "bg-accent-light text-accent",
  success: "bg-success-light text-success",
  warning: "bg-warning-light text-warning"
};

export function FeaturesSection() {
  return (
    <section className="py-16 md:py-24 bg-gradient-to-b from-background to-secondary/30">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center mb-12 md:mb-16">
          <h2 className="text-3xl md:text-4xl font-display font-bold mb-4">
            How <span className="text-gradient-hero">PharmaLens</span> Works
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto text-lg">
            Our intelligent system makes finding affordable medicines simple, 
            fast, and reliable. Here's what powers your savings.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <Card 
              key={index} 
              variant="interactive"
              className="group animate-fade-in-up"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <CardContent className="p-6">
                <div className={`w-14 h-14 rounded-2xl ${colorClasses[feature.color as keyof typeof colorClasses]} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                  <feature.icon className="w-7 h-7" />
                </div>
                <h3 className="text-lg font-semibold mb-2 font-display">
                  {feature.title}
                </h3>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {feature.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
