import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { Upload, Scan, Brain, IndianRupee, CheckCircle2, Shield, Zap, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

const HowItWorks = () => {
    const navigate = useNavigate();

    const steps = [
        {
            icon: Upload,
            title: "Upload Prescription",
            description: "Take a photo of your prescription or upload an image. Our system accepts all common formats.",
            color: "bg-blue-500"
        },
        {
            icon: Scan,
            title: "AI-Powered OCR",
            description: "Advanced Google Cloud Vision extracts text from your prescription with high accuracy.",
            color: "bg-purple-500"
        },
        {
            icon: Brain,
            title: "Smart Medicine Detection",
            description: "Our AI agents identify medicines using a comprehensive knowledge base of 40+ common drugs.",
            color: "bg-pink-500"
        },
        {
            icon: IndianRupee,
            title: "Price Comparison",
            description: "We search 5 major pharmacies (PharmEasy, 1mg, Netmeds, Apollo, Truemeds) to find the best prices.",
            color: "bg-green-500"
        }
    ];

    const features = [
        {
            icon: Shield,
            title: "100% Secure",
            description: "Your prescription data is encrypted and never shared with third parties."
        },
        {
            icon: Zap,
            title: "Instant Results",
            description: "Get price comparisons in seconds, not hours."
        },
        {
            icon: Users,
            title: "Multi-Agent AI",
            description: "3 specialized AI agents work together for accurate results."
        },
        {
            icon: CheckCircle2,
            title: "Best Price Guarantee",
            description: "Save up to 80% on medicines by finding the cheapest options."
        }
    ];

    return (
        <div className="min-h-screen flex flex-col bg-gradient-to-b from-background to-muted/20">
            <Header />

            <main className="flex-1">
                {/* Hero Section */}
                <section className="py-20 px-4">
                    <div className="max-w-4xl mx-auto text-center">
                        <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
                            How PharmaLens Works
                        </h1>
                        <p className="text-xl text-muted-foreground mb-8">
                            Our AI-powered platform makes finding affordable medicines simple and fast
                        </p>
                    </div>
                </section>

                {/* Steps Section */}
                <section className="py-12 px-4">
                    <div className="max-w-6xl mx-auto">
                        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                            {steps.map((step, index) => (
                                <div key={index} className="relative">
                                    {/* Connector Line */}
                                    {index < steps.length - 1 && (
                                        <div className="hidden lg:block absolute top-16 left-full w-full h-0.5 bg-gradient-to-r from-primary/50 to-transparent -z-10" />
                                    )}

                                    <div className="bg-card border rounded-xl p-6 hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
                                        <div className={`${step.color} w-16 h-16 rounded-full flex items-center justify-center mb-4 mx-auto`}>
                                            <step.icon className="w-8 h-8 text-white" />
                                        </div>
                                        <div className="text-center">
                                            <div className="text-sm font-semibold text-primary mb-2">Step {index + 1}</div>
                                            <h3 className="text-lg font-bold mb-2">{step.title}</h3>
                                            <p className="text-sm text-muted-foreground">{step.description}</p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* Features Section */}
                <section className="py-16 px-4 bg-muted/30">
                    <div className="max-w-6xl mx-auto">
                        <h2 className="text-3xl font-bold text-center mb-12">Why Choose PharmaLens?</h2>
                        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                            {features.map((feature, index) => (
                                <div key={index} className="bg-card border rounded-lg p-6 text-center hover:shadow-md transition-shadow">
                                    <feature.icon className="w-12 h-12 mx-auto mb-4 text-primary" />
                                    <h3 className="font-semibold mb-2">{feature.title}</h3>
                                    <p className="text-sm text-muted-foreground">{feature.description}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* CTA Section */}
                <section className="py-20 px-4">
                    <div className="max-w-2xl mx-auto text-center">
                        <h2 className="text-3xl font-bold mb-4">Ready to Save on Medicines?</h2>
                        <p className="text-muted-foreground mb-8">
                            Join thousands of users who are already saving money on their prescriptions
                        </p>
                        <Button
                            size="lg"
                            onClick={() => navigate('/')}
                            className="bg-gradient-to-r from-primary to-purple-600 hover:opacity-90"
                        >
                            Get Started Now
                        </Button>
                    </div>
                </section>
            </main>

            <Footer />
        </div>
    );
};

export default HowItWorks;
