import { Button } from "@/components/ui/button";
import { Pill, Twitter, Linkedin, Mail, Heart } from "lucide-react";
import { Link } from "react-router-dom";

export function Footer() {
  return (
    <footer className="bg-foreground text-background py-12 md:py-16">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8 md:gap-12 mb-12">
          {/* Brand */}
          <div className="md:col-span-1">
            <Link to="/" className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
                <Pill className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="font-display font-bold text-xl">PharmaLens</span>
            </Link>
            <p className="text-background/70 text-sm mb-4">
              Making healthcare affordable for everyone in India. 
              Compare medicine prices instantly and save money on every purchase.
            </p>
            <div className="flex items-center gap-3">
              <Button variant="ghost" size="icon" className="hover:bg-background/10 text-background">
                <Twitter className="w-5 h-5" />
              </Button>
              <Button variant="ghost" size="icon" className="hover:bg-background/10 text-background">
                <Linkedin className="w-5 h-5" />
              </Button>
              <Button variant="ghost" size="icon" className="hover:bg-background/10 text-background">
                <Mail className="w-5 h-5" />
              </Button>
            </div>
          </div>

          {/* Links */}
          <div>
            <h4 className="font-semibold mb-4">Product</h4>
            <ul className="space-y-2 text-sm text-background/70">
              <li><a href="#" className="hover:text-background transition-colors">How It Works</a></li>
              <li><a href="#" className="hover:text-background transition-colors">Pricing</a></li>
              <li><a href="#" className="hover:text-background transition-colors">API Access</a></li>
              <li><a href="#" className="hover:text-background transition-colors">Mobile App</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold mb-4">Resources</h4>
            <ul className="space-y-2 text-sm text-background/70">
              <li><a href="#" className="hover:text-background transition-colors">Medicine Database</a></li>
              <li><a href="#" className="hover:text-background transition-colors">Generic Alternatives</a></li>
              <li><a href="#" className="hover:text-background transition-colors">Health Blog</a></li>
              <li><a href="#" className="hover:text-background transition-colors">FAQs</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold mb-4">Company</h4>
            <ul className="space-y-2 text-sm text-background/70">
              <li><a href="#" className="hover:text-background transition-colors">About Us</a></li>
              <li><a href="#" className="hover:text-background transition-colors">Contact</a></li>
              <li><a href="#" className="hover:text-background transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-background transition-colors">Terms of Service</a></li>
            </ul>
          </div>
        </div>

        {/* Bottom */}
        <div className="pt-8 border-t border-background/20 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-background/60">
            © 2024 PharmaLens. All rights reserved.
          </p>
          <p className="text-sm text-background/60 flex items-center gap-1">
            Made with <Heart className="w-4 h-4 text-destructive fill-destructive" /> in India
          </p>
        </div>
      </div>
    </footer>
  );
}
