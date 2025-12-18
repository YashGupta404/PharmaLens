import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Pill, ArrowRight, Sparkles } from "lucide-react";
import { toast } from "sonner";

export interface UserProfile {
  name: string;
  email: string;
  location: string;
  age: string;
  sex: string;
}

export default function Auth() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<UserProfile>({
    name: "",
    email: "",
    location: "",
    age: "",
    sex: "",
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (field: keyof UserProfile, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    if (!formData.name.trim() || !formData.email.trim() || !formData.location.trim() || !formData.age || !formData.sex) {
      toast.error("Please fill in all fields");
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      toast.error("Please enter a valid email address");
      return;
    }

    setIsLoading(true);
    
    // Simulate a brief loading state
    await new Promise((resolve) => setTimeout(resolve, 800));
    
    // Store user data in localStorage
    localStorage.setItem("pharmalens_user", JSON.stringify(formData));
    
    toast.success(`Welcome to PharmaLens, ${formData.name}!`);
    setIsLoading(false);
    navigate("/");
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

        <Card variant="glass" className="border-border/50 shadow-elevated">
          <CardHeader className="text-center pb-2">
            <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
              <Sparkles className="w-6 h-6 text-primary" />
            </div>
            <CardTitle className="text-2xl font-display">Get Started</CardTitle>
            <CardDescription className="text-muted-foreground">
              Create your profile to start saving on medicines
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
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
                    Creating Profile...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    Get Started
                    <ArrowRight className="w-4 h-4" />
                  </span>
                )}
              </Button>
            </form>

            <p className="text-xs text-muted-foreground text-center mt-6">
              By continuing, you agree to our Terms of Service and Privacy Policy
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
