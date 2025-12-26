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
import { processPrescription, searchMedicine, searchMedicineStream, StreamEvent } from "@/lib/api";

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
  // Progressive pharmacy search state
  const [completedPharmacies, setCompletedPharmacies] = useState<string[]>([]);
  const [remainingPharmacies, setRemainingPharmacies] = useState<number>(0);
  const [streamMessage, setStreamMessage] = useState<string>('');
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

  // Handle manual medicine search (bypasses OCR/AI, goes straight to scrapers)
  // Uses streaming to show results as each pharmacy completes
  const handleManualSearch = useCallback(async (medicines: string[]) => {
    console.log("Manual search for medicines:", medicines);
    setIsManualSearching(true);
    setErrorMessage(null);
    setResults([]);
    setExtractedMedicines(medicines);
    setScanStatus('searching');
    setCompletedPharmacies([]);
    setRemainingPharmacies(4); // 4 pharmacies total
    setStreamMessage('Starting search...');

    try {
      toast.info(`Searching prices for ${medicines.length} medicine(s)...`);

      // For multiple medicines, search each one with streaming
      // Accumulate all prices as they come in
      const allPrices: any[] = [];
      let allCompletedPharmacies: string[] = [];

      for (const med of medicines) {
        await searchMedicineStream(
          med,
          (event: StreamEvent) => {
            // Handle streaming events
            if (event.type === 'started') {
              setStreamMessage(event.message || 'Connecting to pharmacies...');
            } else if (event.type === 'pharmacy_result') {
              // Update completed pharmacies
              if (event.completed_pharmacies) {
                setCompletedPharmacies([...event.completed_pharmacies]);
                allCompletedPharmacies = event.completed_pharmacies;
              }
              setRemainingPharmacies(event.remaining || 0);
              setStreamMessage(event.message || '');

              // Add prices to running total
              if (event.prices && event.prices.length > 0) {
                allPrices.push(...event.prices);
              }
            } else if (event.type === 'complete') {
              setStreamMessage(event.message || 'Search complete!');
            } else if (event.type === 'error') {
              console.error('Stream error:', event.error);
            }
          }
        );
      }

      // Final results from accumulated prices
      const formattedResults: MedicineSearchResult[] = medicines.map((medName, index) => {
        // Get prices for this medicine
        const medicinePrices = allPrices.filter(p =>
          p.product_name?.toLowerCase().includes(medName.toLowerCase().split(' ')[0])
        );

        const cheapest = medicinePrices.length > 0
          ? medicinePrices.reduce((min, p) => p.price < min.price ? p : min)
          : null;

        const mostExpensive = medicinePrices.length > 0
          ? medicinePrices.reduce((max, p) => p.price > max.price ? p : max)
          : null;

        const savings = cheapest && mostExpensive
          ? mostExpensive.price - cheapest.price
          : 0;

        return {
          medicine: {
            id: `med_${Date.now()}_${index}`,
            name: medName,
            genericName: '',
            dosage: '',
            form: 'tablet',
            manufacturer: '',
            composition: '',
            isGeneric: false,
          },
          prices: medicinePrices.map((p: any, idx: number) => ({
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
          cheapestPrice: cheapest ? {
            pharmacyId: cheapest.pharmacy_id,
            pharmacyName: cheapest.pharmacy_name,
            pharmacyLogo: '',
            price: cheapest.price || 0,
            packSize: cheapest.pack_size || '1 Unit',
            inStock: cheapest.in_stock !== false,
            url: cheapest.url || '#',
            lastUpdated: new Date(),
          } : undefined,
          genericAlternatives: [],
          savings: savings,
        };
      });

      setResults(formattedResults);
      setScanStatus('completed');
      setIsManualSearching(false);

      const totalSavings = formattedResults.reduce((sum, r) => sum + (r.savings || 0), 0);
      toast.success(`Found prices from ${allCompletedPharmacies.length} pharmacies! Potential savings: ₹${totalSavings.toFixed(0)}`);

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
            completedPharmacies={completedPharmacies}
            remainingPharmacies={remainingPharmacies}
            streamMessage={streamMessage}
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
