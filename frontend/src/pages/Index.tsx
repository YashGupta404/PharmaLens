import { useState, useCallback, useRef } from "react";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { HeroSection } from "@/components/sections/HeroSection";
import { PrescriptionUpload } from "@/components/sections/PrescriptionUpload";
import { FeaturesSection } from "@/components/sections/FeaturesSection";
import { PharmaciesSection } from "@/components/sections/PharmaciesSection";
import { ResultsSection } from "@/components/medicine/ResultsSection";
import { ManualMedicineInput } from "@/components/medicine/ManualMedicineInput";
import { AgentStatusPanel } from "@/components/medicine/AgentStatusPanel";
import { SearchHistorySidebar } from "@/components/layout/SearchHistorySidebar";
import { toast } from "sonner";
import type { ScanStatus, MedicineSearchResult, SearchHistory } from "@/types/pharmalens";
import type { AgentStatus } from "@/lib/api";

// API imports
import { processPrescription, searchMedicine } from "@/lib/api";

const Index = () => {
  const [scanStatus, setScanStatus] = useState<ScanStatus | null>(null);
  const [results, setResults] = useState<MedicineSearchResult[]>([]);
  const [extractedMedicines, setExtractedMedicines] = useState<string[]>([]);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [searchHistory, setSearchHistory] = useState<SearchHistory[]>([]);
  const [prescriptionId, setPrescriptionId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isManualSearching, setIsManualSearching] = useState(false);
  const [agentUpdates, setAgentUpdates] = useState<AgentStatus[]>([]);
  const uploadSectionRef = useRef<HTMLDivElement>(null);

  const scrollToUpload = useCallback(() => {
    uploadSectionRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  const handleUpload = useCallback(async (file: File) => {
    console.log("Processing prescription:", file.name);
    setErrorMessage(null);
    setResults([]);
    setExtractedMedicines([]);
    setAgentUpdates([]);

    try {
      // Use the real API
      const result = await processPrescription(file, (step, data) => {
        switch (step) {
          case 'uploading':
            setScanStatus('processing');
            toast.info('Uploading prescription...');
            // Agent 1 starts
            setAgentUpdates([
              { agent: "OCR Interpreter", status: "working", message: "Uploading image...", progress: 20 }
            ]);
            break;
          case 'uploaded':
            setPrescriptionId(data?.prescription_id);
            break;
          case 'extracting':
            setScanStatus('extracting');
            toast.info('🔍 AI Agent: Extracting text with OCR...');
            setAgentUpdates([
              { agent: "OCR Interpreter", status: "working", message: "Analyzing handwriting patterns...", progress: 50 },
              { agent: "Medicine Identifier", status: "idle", message: "Waiting for OCR...", progress: 0 }
            ]);
            break;
          case 'ocr_complete':
            console.log('OCR Text:', data?.text);
            setAgentUpdates([
              { agent: "OCR Interpreter", status: "completed", message: "Text extracted successfully!", progress: 100 },
              { agent: "Medicine Identifier", status: "working", message: "Searching medical database...", progress: 20 }
            ]);
            break;
          case 'parsing':
            toast.info('💊 AI Agent: Searching medical knowledge base...');
            setAgentUpdates([
              { agent: "OCR Interpreter", status: "completed", message: "Done!", progress: 100 },
              { agent: "Medicine Identifier", status: "working", message: "Cross-referencing with medical archives...", progress: 60 },
              { agent: "Price Finder", status: "idle", message: "Waiting...", progress: 0 }
            ]);
            break;
          case 'extraction_complete':
            const medicineNames = (data?.medicines || []).map((m: any) =>
              `${m.name}${m.dosage ? ' ' + m.dosage : ''}`
            );
            setExtractedMedicines(medicineNames);
            setAgentUpdates([
              { agent: "OCR Interpreter", status: "completed", message: "Done!", progress: 100 },
              { agent: "Medicine Identifier", status: "completed", message: `Found ${medicineNames.length} medicines!`, progress: 100 },
              { agent: "Price Finder", status: "working", message: "Connecting to pharmacies...", progress: 10 }
            ]);
            break;
          case 'searching':
            setScanStatus('searching');
            toast.info('💰 AI Agent: Searching 4 pharmacy databases...');
            setAgentUpdates([
              { agent: "OCR Interpreter", status: "completed", message: "Done!", progress: 100 },
              { agent: "Medicine Identifier", status: "completed", message: "Done!", progress: 100 },
              { agent: "Price Finder", status: "working", message: "Searching PharmEasy, 1mg, Netmeds, Apollo...", progress: 50 }
            ]);
            break;
          case 'search_complete':
            console.log('Search results:', data?.results);
            setAgentUpdates([
              { agent: "OCR Interpreter", status: "completed", message: "Done!", progress: 100 },
              { agent: "Medicine Identifier", status: "completed", message: "Done!", progress: 100 },
              { agent: "Price Finder", status: "completed", message: "Found best prices!", progress: 100 }
            ]);
            break;
        }
      });

      // Convert API results to frontend format
      const formattedResults: MedicineSearchResult[] = (result.search_results?.results || []).map((r: any, index: number) => ({
        medicine: {
          id: r.search_id || `med_${Date.now()}_${index}`,
          name: r.medicine_name || 'Unknown',
          genericName: r.cheapest?.generic_name || '',
          dosage: r.dosage || '',
          form: 'tablet',
          manufacturer: '',
          composition: r.cheapest?.generic_name || '',
          isGeneric: false,
        },
        prices: (r.prices || []).map((p: any, idx: number) => ({
          pharmacyId: p.pharmacy_id || `pharmacy_${idx}`,
          pharmacyName: p.pharmacy_name || 'Unknown',
          pharmacyLogo: '',
          price: p.price || 0,
          originalPrice: p.original_price,
          discount: p.discount,
          packSize: p.pack_size || '1 Unit',
          inStock: p.in_stock !== false,
          deliveryDays: p.delivery_days || 2,
          url: p.url || '#',
          lastUpdated: new Date(),
        })),
        cheapestPrice: r.cheapest ? {
          pharmacyId: r.cheapest.pharmacy_id,
          pharmacyName: r.cheapest.pharmacy_name,
          pharmacyLogo: '',
          price: r.cheapest.price || 0,
          packSize: r.cheapest.pack_size || '1 Unit',
          inStock: r.cheapest.in_stock !== false,
          url: r.cheapest.url || '#',
          lastUpdated: new Date(),
        } : undefined,
        genericAlternatives: [],
        savings: r.savings || 0,
      }));

      setResults(formattedResults);
      setScanStatus('completed');

      if (formattedResults.length > 0) {
        toast.success(`Found prices for ${formattedResults.length} medicines!`);
      } else if (result.medicines.length > 0) {
        toast.warning('Medicines identified but no prices found. Try manual search.');
        // Still show extracted medicines even if no prices
        setExtractedMedicines(result.medicines.map((m: any) =>
          `${m.name}${m.dosage ? ' ' + m.dosage : ''}`
        ));
      } else {
        toast.error('No medicines detected. Please try a clearer image.');
      }

    } catch (error) {
      console.error("Prescription processing error:", error);
      setErrorMessage(error instanceof Error ? error.message : 'Processing failed');
      setScanStatus('completed');
      toast.error(error instanceof Error ? error.message : 'Failed to process prescription');
    }
  }, []);

  // Handle manual medicine search - SIMPLE VERSION (no streaming)
  const handleManualSearch = useCallback(async (medicines: string[]) => {
    console.log("Manual search for medicines:", medicines);
    setIsManualSearching(true);
    setErrorMessage(null);
    setResults([]);
    setExtractedMedicines(medicines);
    setScanStatus('searching');

    try {
      toast.info(`Searching prices for ${medicines.length} medicine(s). This may take 1-5 minutes...`);

      // Search each medicine
      const searchResults = await Promise.all(
        medicines.map(med => searchMedicine(med))
      );

      // Convert to frontend format
      const formattedResults: MedicineSearchResult[] = searchResults.map((r: any) => ({
        medicine: {
          id: r.search_id || `med_${Date.now()}_${Math.random()}`,
          name: r.medicine_name || 'Unknown',
          genericName: r.cheapest?.generic_name || '',
          dosage: r.dosage || '',
          form: 'tablet',
          manufacturer: '',
          composition: r.cheapest?.generic_name || '',
          isGeneric: false,
        },
        prices: (r.prices || []).map((p: any, idx: number) => ({
          pharmacyId: p.pharmacy_id || `pharmacy_${Date.now()}_${idx}`,
          pharmacyName: p.pharmacy_name || 'Unknown',
          pharmacyLogo: '',
          price: p.price || 0,
          originalPrice: p.original_price,
          discount: p.discount,
          packSize: p.pack_size || '1 Unit',
          inStock: p.in_stock !== false,
          deliveryDays: p.delivery_days || 2,
          url: p.url || '#',
          lastUpdated: new Date(),
        })),
        cheapestPrice: r.cheapest ? {
          pharmacyId: r.cheapest.pharmacy_id,
          pharmacyName: r.cheapest.pharmacy_name,
          pharmacyLogo: '',
          price: r.cheapest.price || 0,
          packSize: r.cheapest.pack_size || '1 Unit',
          inStock: r.cheapest.in_stock !== false,
          url: r.cheapest.url || '#',
          lastUpdated: new Date(),
        } : undefined,
        genericAlternatives: [],
        savings: r.savings || 0,
      }));

      setResults(formattedResults);
      setScanStatus('completed');
      setIsManualSearching(false);

      const totalSavings = formattedResults.reduce((sum, r) => sum + (r.savings || 0), 0);
      toast.success(`Found prices! Potential savings: ₹${totalSavings.toFixed(0)}`);

    } catch (error) {
      console.error("Manual search error:", error);
      setErrorMessage(error instanceof Error ? error.message : 'Search failed');
      setScanStatus('completed');
      setIsManualSearching(false);
      toast.error(error instanceof Error ? error.message : 'Failed to search medicines');
    }
  }, []);

  const handleSelectHistory = useCallback((search: SearchHistory) => {
    setIsHistoryOpen(false);
    // TODO: Load saved results from API
    toast.info('Loading search history...');
  }, []);

  const handleReset = useCallback(() => {
    setScanStatus(null);
    setResults([]);
    setExtractedMedicines([]);
    setPrescriptionId(null);
    setErrorMessage(null);
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main>
        {/* Hero Section */}
        <HeroSection onUploadClick={scrollToUpload} />

        {/* Upload Section */}
        <div ref={uploadSectionRef}>
          <PrescriptionUpload
            onUpload={handleUpload}
            isProcessing={scanStatus === 'processing' || scanStatus === 'extracting' || scanStatus === 'searching'}
          />
        </div>

        {/* OR Divider */}
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-background px-4 text-muted-foreground font-medium">
                OR type medicine names manually
              </span>
            </div>
          </div>
        </div>

        {/* Manual Medicine Input Section */}
        <div className="max-w-4xl mx-auto px-4 pb-8">
          <ManualMedicineInput
            onSearch={handleManualSearch}
            isSearching={isManualSearching || scanStatus === 'searching'}
          />
        </div>

        {/* AI Agent Status Panel - Shows during processing */}
        {(scanStatus === 'processing' || scanStatus === 'extracting' || scanStatus === 'searching' || agentUpdates.length > 0) && (
          <div className="max-w-4xl mx-auto px-4 pb-8">
            <AgentStatusPanel
              updates={agentUpdates}
              isProcessing={scanStatus !== null && scanStatus !== 'completed'}
            />
          </div>
        )}

        {/* Error Message */}
        {errorMessage && (
          <div className="max-w-4xl mx-auto px-4 py-4">
            <div className="bg-destructive/10 border border-destructive/30 rounded-lg p-4 text-destructive">
              <p className="font-medium">Error: {errorMessage}</p>
              <button
                onClick={handleReset}
                className="mt-2 text-sm underline hover:no-underline"
              >
                Try again
              </button>
            </div>
          </div>
        )}

        {/* Results Section */}
        {scanStatus && (
          <ResultsSection
            results={results}
            status={scanStatus}
            extractedMedicines={extractedMedicines}
          />
        )}

        {/* Features Section */}
        <FeaturesSection />

        {/* Pharmacies Section */}
        <PharmaciesSection />
      </main>

      <Footer />

      {/* Search History Sidebar */}
      <SearchHistorySidebar
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        history={searchHistory}
        onSelectSearch={handleSelectHistory}
      />
    </div>
  );
};

export default Index;
