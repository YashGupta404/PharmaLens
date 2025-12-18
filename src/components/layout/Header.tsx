import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Pill, Menu, X, History, Sparkles } from "lucide-react";
import { useState } from "react";

export function Header() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 glass-subtle border-b border-border/50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16 md:h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="relative">
              <div className="w-10 h-10 rounded-xl bg-gradient-hero flex items-center justify-center shadow-md group-hover:shadow-glow transition-shadow duration-300">
                <Pill className="w-5 h-5 text-primary-foreground" />
              </div>
              <div className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-accent animate-pulse" />
            </div>
            <div className="flex flex-col">
              <span className="font-display font-bold text-xl text-foreground">
                Pharma<span className="text-gradient-hero">Lens</span>
              </span>
              <span className="text-[10px] text-muted-foreground -mt-1 hidden sm:block">
                Smart Medicine Savings
              </span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            <Button variant="ghost" size="sm" className="gap-2">
              <Sparkles className="w-4 h-4" />
              How It Works
            </Button>
            <Button variant="ghost" size="sm" className="gap-2">
              <History className="w-4 h-4" />
              Search History
            </Button>
            <Badge variant="success-light" className="ml-2">
              100% Free
            </Badge>
          </nav>

          {/* Desktop CTA */}
          <div className="hidden md:flex items-center gap-3">
            <Button variant="outline" size="sm">
              Sign In
            </Button>
            <Button variant="hero" size="sm">
              Get Started
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </Button>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden glass border-t border-border/50 animate-fade-in">
          <nav className="container mx-auto px-4 py-4 flex flex-col gap-2">
            <Button variant="ghost" className="justify-start gap-2">
              <Sparkles className="w-4 h-4" />
              How It Works
            </Button>
            <Button variant="ghost" className="justify-start gap-2">
              <History className="w-4 h-4" />
              Search History
            </Button>
            <div className="h-px bg-border my-2" />
            <Button variant="outline" className="w-full">
              Sign In
            </Button>
            <Button variant="hero" className="w-full">
              Get Started
            </Button>
          </nav>
        </div>
      )}
    </header>
  );
}
