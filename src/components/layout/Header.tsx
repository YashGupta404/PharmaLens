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
            <div className="relative text-3xl group-hover:scale-110 transition-transform duration-300">
              <span className="relative inline-block">
                ❤️
                <span className="absolute top-0 left-1/2 -translate-x-1/2 text-[0.5em]">🤓</span>
              </span>
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
            <Button variant="ghost" className="justify-start gap-2">
              <Sparkles className="w-4 h-4" />
              How It Works
            </Button>
            <Button variant="ghost" className="justify-start gap-2">
              <History className="w-4 h-4" />
              Search History
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
