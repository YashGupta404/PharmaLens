import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Menu, X, History, Sparkles, User, MapPin, Calendar, LogOut } from "lucide-react";
import { useState, useEffect } from "react";
import { toast } from "sonner";

interface UserProfile {
  name: string;
  email: string;
  location: string;
  age: string;
  sex: string;
}

export function Header() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [user, setUser] = useState<UserProfile | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const storedUser = localStorage.getItem("pharmalens_user");
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("pharmalens_user");
    setUser(null);
    toast.success("Logged out successfully");
    navigate("/");
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 glass-subtle border-b border-border/50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16 md:h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="relative group-hover:scale-110 transition-transform duration-300">
              <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                {/* Heart body */}
                <path d="M20 35C20 35 5 25 5 14C5 8 9 4 14 4C17 4 19.5 6 20 8C20.5 6 23 4 26 4C31 4 35 8 35 14C35 25 20 35 20 35Z" fill="url(#heartGradient)" />
                {/* Left eye */}
                <circle cx="14" cy="16" r="3" fill="white" />
                <circle cx="15" cy="16" r="1.5" fill="#1a1a2e" />
                {/* Right eye */}
                <circle cx="23" cy="16" r="3" fill="white" />
                <circle cx="24" cy="16" r="1.5" fill="#1a1a2e" />
                {/* Magnifying glass */}
                <circle cx="32" cy="28" r="6" stroke="hsl(var(--accent))" strokeWidth="2.5" fill="hsl(var(--accent)/0.1)" />
                <line x1="28" y1="32" x2="23" y2="37" stroke="hsl(var(--accent))" strokeWidth="2.5" strokeLinecap="round" />
                {/* Gradient definition */}
                <defs>
                  <linearGradient id="heartGradient" x1="5" y1="4" x2="35" y2="35" gradientUnits="userSpaceOnUse">
                    <stop stopColor="hsl(var(--primary))" />
                    <stop offset="1" stopColor="hsl(var(--accent))" />
                  </linearGradient>
                </defs>
              </svg>
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
            <Button variant="ghost" size="sm" className="gap-2" asChild>
              <Link to="/how-it-works">
                <Sparkles className="w-4 h-4" />
                How It Works
              </Link>
            </Button>
            <Button variant="ghost" size="sm" className="gap-2" asChild>
              <Link to="/search-history">
                <History className="w-4 h-4" />
                Search History
              </Link>
            </Button>
            <Badge variant="success-light" className="ml-2">
              100% Free
            </Badge>
          </nav>

          {/* Desktop CTA */}
          <div className="hidden md:flex items-center gap-3">
            {user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm" className="gap-2">
                    <div className="w-7 h-7 rounded-full bg-gradient-hero flex items-center justify-center">
                      <User className="w-4 h-4 text-primary-foreground" />
                    </div>
                    <span className="max-w-[100px] truncate">{user.name.split(" ")[0]}</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-64">
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">{user.name}</p>
                      <p className="text-xs leading-none text-muted-foreground">{user.email}</p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="gap-2 cursor-default focus:bg-transparent">
                    <MapPin className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm">{user.location}</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem className="gap-2 cursor-default focus:bg-transparent">
                    <Calendar className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm">{user.age} years old</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem className="gap-2 cursor-default focus:bg-transparent">
                    <User className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm capitalize">{user.sex}</span>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} className="gap-2 text-destructive focus:text-destructive cursor-pointer">
                    <LogOut className="w-4 h-4" />
                    <span>Logout</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <>
                <Button variant="outline" size="sm" asChild>
                  <Link to="/auth">Sign In</Link>
                </Button>
                <Button variant="hero" size="sm" asChild>
                  <Link to="/auth">Get Started</Link>
                </Button>
              </>
            )}
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
            <Button variant="ghost" className="justify-start gap-2" asChild>
              <Link to="/how-it-works">
                <Sparkles className="w-4 h-4" />
                How It Works
              </Link>
            </Button>
            <Button variant="ghost" className="justify-start gap-2" asChild>
              <Link to="/search-history">
                <History className="w-4 h-4" />
                Search History
              </Link>
            </Button>
            <div className="h-px bg-border my-2" />
            {user ? (
              <>
                <div className="px-3 py-2 space-y-2">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-hero flex items-center justify-center">
                      <User className="w-5 h-5 text-primary-foreground" />
                    </div>
                    <div>
                      <p className="font-medium text-sm">{user.name}</p>
                      <p className="text-xs text-muted-foreground">{user.email}</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3 h-3" /> {user.location}
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" /> {user.age} yrs
                    </span>
                    <span className="capitalize">{user.sex}</span>
                  </div>
                </div>
                <Button variant="outline" className="w-full text-destructive border-destructive/30 hover:bg-destructive/10" onClick={handleLogout}>
                  <LogOut className="w-4 h-4 mr-2" />
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Button variant="outline" className="w-full" asChild>
                  <Link to="/auth">Sign In</Link>
                </Button>
                <Button variant="hero" className="w-full" asChild>
                  <Link to="/auth">Get Started</Link>
                </Button>
              </>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
