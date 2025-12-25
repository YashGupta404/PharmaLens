import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Pill, ArrowRight, Sparkles, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";

export interface UserProfile {
  name: string;
  email: string;
  password?: string;
  location: string;
  age: string;
  sex: string;
}

type AuthMode = "signin" | "signup" | "details" | "success";

export default function Auth() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [mode, setMode] = useState<AuthMode>("signin");
  const [formData, setFormData] = useState<UserProfile>({
    name: "",
    email: "",
    password: "",
    location: "",
    age: "",
    sex: "",
  });
  const [isLoading, setIsLoading] = useState(false);

  // Check for success message from URL
  useEffect(() => {
    if (searchParams.get("registered") === "true") {
      setMode("success");
    }
  }, [searchParams]);

  const handleInputChange = (field: keyof UserProfile, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  // Handle Sign In
  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.email.trim() || !formData.password) {
      toast.error("Please enter email and password");
      return;
    }

    setIsLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 800));

    // Check if user exists in localStorage
    const existingUser = localStorage.getItem("pharmalens_registered_user");
    if (existingUser) {
      const user = JSON.parse(existingUser);
      if (user.email === formData.email && user.password === formData.password) {
        // Set session storage (clears on browser close)
        sessionStorage.setItem("pharmalens_session", "active");
        localStorage.setItem("pharmalens_user", JSON.stringify(user));
        toast.success(`Welcome back, ${user.name}!`);
        setIsLoading(false);
        navigate("/");
        return;
      }
    }

    toast.error("Invalid email or password");
    setIsLoading(false);
  };

  // Handle Sign Up (email + password only)
  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.email.trim() || !formData.password || formData.password.length < 6) {
      toast.error("Please enter email and password (min 6 characters)");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      toast.error("Please enter a valid email address");
      return;
    }

    // Store email/password temporarily, move to details
    setMode("details");
  };

  // Handle Details submission (after sign up)
  const handleDetailsSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim() || !formData.location.trim() || !formData.age || !formData.sex) {
      toast.error("Please fill in all fields");
      return;
    }

    setIsLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 800));

    // Save the complete user data
    localStorage.setItem("pharmalens_registered_user", JSON.stringify(formData));

    setIsLoading(false);
    // Redirect with registered flag
    window.location.href = "/auth?registered=true";
  };

  // Handle "Sign In" after success
  const handleGoToSignIn = () => {
    setMode("signin");
    navigate("/auth", { replace: true });
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary/5 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent/5 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-radial from-primary/3 to-transparent rounded-full" />
      </div>

      <div className="w-full max-w-md relative z-10">
        {/* Logo */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <div className="relative">
            <div className="w-12 h-12 rounded-xl bg-gradient-hero flex items-center justify-center shadow-md">
              <Pill className="w-6 h-6 text-primary-foreground" />
            </div>
            <div className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-accent animate-pulse" />
          </div>
          <div className="flex flex-col">
            <span className="font-display font-bold text-2xl text-foreground">
              Pharma<span className="text-gradient-hero">Lens</span>
            </span>
            <span className="text-xs text-muted-foreground -mt-1">
              Smart Medicine Savings
            </span>
          </div>
        </div>

        {/* Success Screen */}
        {mode === "success" && (
          <Card variant="glass" className="border-border/50 shadow-elevated">
            <CardHeader className="text-center pb-2">
              <div className="mx-auto w-16 h-16 rounded-full bg-green-500/10 flex items-center justify-center mb-4">
                <CheckCircle2 className="w-8 h-8 text-green-500" />
              </div>
              <CardTitle className="text-2xl font-display text-green-600">Account Created!</CardTitle>
              <CardDescription className="text-muted-foreground">
                Your account has been created successfully. Please sign in to continue.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="hero" className="w-full" onClick={handleGoToSignIn}>
                Sign In Now
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Sign In Form */}
        {mode === "signin" && (
          <Card variant="glass" className="border-border/50 shadow-elevated">
            <CardHeader className="text-center pb-2">
              <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <Sparkles className="w-6 h-6 text-primary" />
              </div>
              <CardTitle className="text-2xl font-display">Sign In</CardTitle>
              <CardDescription className="text-muted-foreground">
                Welcome back! Enter your credentials to continue.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSignIn} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={formData.email}
                    onChange={(e) => handleInputChange("email", e.target.value)}
                    className="bg-background/50"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="Enter your password"
                    value={formData.password}
                    onChange={(e) => handleInputChange("password", e.target.value)}
                    className="bg-background/50"
                  />
                </div>

                <Button
                  type="submit"
                  variant="hero"
                  className="w-full mt-6"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <span className="flex items-center gap-2">
                      <span className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                      Signing In...
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      Sign In
                      <ArrowRight className="w-4 h-4" />
                    </span>
                  )}
                </Button>
              </form>

              <div className="mt-6 text-center">
                <p className="text-sm text-muted-foreground">
                  Don't have an account?{" "}
                  <button
                    onClick={() => setMode("signup")}
                    className="text-primary hover:underline font-medium"
                  >
                    Sign Up
                  </button>
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Sign Up Form (Email + Password only) */}
        {mode === "signup" && (
          <Card variant="glass" className="border-border/50 shadow-elevated">
            <CardHeader className="text-center pb-2">
              <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <Sparkles className="w-6 h-6 text-primary" />
              </div>
              <CardTitle className="text-2xl font-display">Create Account</CardTitle>
              <CardDescription className="text-muted-foreground">
                Sign up to start saving on medicines
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSignUp} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={formData.email}
                    onChange={(e) => handleInputChange("email", e.target.value)}
                    className="bg-background/50"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="Create a password (min 6 chars)"
                    value={formData.password}
                    onChange={(e) => handleInputChange("password", e.target.value)}
                    className="bg-background/50"
                  />
                </div>

                <Button
                  type="submit"
                  variant="hero"
                  className="w-full mt-6"
                  disabled={isLoading}
                >
                  <span className="flex items-center gap-2">
                    Continue
                    <ArrowRight className="w-4 h-4" />
                  </span>
                </Button>
              </form>

              <div className="mt-6 text-center">
                <p className="text-sm text-muted-foreground">
                  Already have an account?{" "}
                  <button
                    onClick={() => setMode("signin")}
                    className="text-primary hover:underline font-medium"
                  >
                    Sign In
                  </button>
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Profile Details Form (after Sign Up) */}
        {mode === "details" && (
          <Card variant="glass" className="border-border/50 shadow-elevated">
            <CardHeader className="text-center pb-2">
              <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <Sparkles className="w-6 h-6 text-primary" />
              </div>
              <CardTitle className="text-2xl font-display">Complete Your Profile</CardTitle>
              <CardDescription className="text-muted-foreground">
                Tell us a bit about yourself
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleDetailsSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Full Name</Label>
                  <Input
                    id="name"
                    placeholder="Enter your full name"
                    value={formData.name}
                    onChange={(e) => handleInputChange("name", e.target.value)}
                    className="bg-background/50"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="location">Location</Label>
                  <Input
                    id="location"
                    placeholder="City, State"
                    value={formData.location}
                    onChange={(e) => handleInputChange("location", e.target.value)}
                    className="bg-background/50"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="age">Age</Label>
                    <Select value={formData.age} onValueChange={(value) => handleInputChange("age", value)}>
                      <SelectTrigger className="bg-background/50">
                        <SelectValue placeholder="Select age" />
                      </SelectTrigger>
                      <SelectContent>
                        {Array.from({ length: 83 }, (_, i) => i + 18).map((age) => (
                          <SelectItem key={age} value={age.toString()}>
                            {age} years
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="sex">Sex</Label>
                    <Select value={formData.sex} onValueChange={(value) => handleInputChange("sex", value)}>
                      <SelectTrigger className="bg-background/50">
                        <SelectValue placeholder="Select" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="male">Male</SelectItem>
                        <SelectItem value="female">Female</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                        <SelectItem value="prefer-not-to-say">Prefer not to say</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <Button
                  type="submit"
                  variant="hero"
                  className="w-full mt-6"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <span className="flex items-center gap-2">
                      <span className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                      Creating Account...
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      Create Account
                      <ArrowRight className="w-4 h-4" />
                    </span>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        <p className="text-xs text-muted-foreground text-center mt-6">
          By continuing, you agree to our Terms of Service and Privacy Policy
        </p>
      </div>
    </div>
  );
}
