import { useState, useCallback, useRef } from "react";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { HeroSection } from "@/components/sections/HeroSection";
import { PrescriptionUpload } from "@/components/sections/PrescriptionUpload";
import { FeaturesSection } from "@/components/sections/FeaturesSection";
import { PharmaciesSection } from "@/components/sections/PharmaciesSection";
import { ResultsSection } from "@/components/medicine/ResultsSection";
import { SearchHistorySidebar } from "@/components/layout/SearchHistorySidebar";
import { mockSearchResults, mockSearchHistory, mockExtractedMedicines } from "@/data/mockData";
import type { ScanStatus, MedicineSearchResult, SearchHistory } from "@/types/pharmalens";

const Index = () => {
  const [scanStatus, setScanStatus] = useState<ScanStatus | null>(null);
  const [results, setResults] = useState<MedicineSearchResult[]>([]);
  const [extractedMedicines, setExtractedMedicines] = useState<string[]>([]);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [searchHistory] = useState<SearchHistory[]>(mockSearchHistory);
  const uploadSectionRef = useRef<HTMLDivElement>(null);

  const scrollToUpload = useCallback(() => {
    uploadSectionRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  const simulateScan = useCallback(async () => {
    // Start processing
    setScanStatus('processing');
    await delay(1500);

    // OCR extraction
    setScanStatus('extracting');
    await delay(2000);

    // Set extracted medicines
    setExtractedMedicines(mockExtractedMedicines);
    setScanStatus('searching');
    await delay(2500);

    // Complete with results
    setResults(mockSearchResults);
    setScanStatus('completed');
  }, []);

  const handleUpload = useCallback((file: File) => {
    console.log("Uploaded file:", file.name);
    simulateScan();
  }, [simulateScan]);

  const handleSelectHistory = useCallback((search: SearchHistory) => {
    setIsHistoryOpen(false);
    // In a real app, this would load the saved results
    setResults(mockSearchResults);
    setExtractedMedicines(mockExtractedMedicines);
    setScanStatus('completed');
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
            isProcessing={scanStatus === 'processing' || scanStatus === 'extracting'}
          />
        </div>

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

// Helper function
function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export default Index;
