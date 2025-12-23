/**
 * Use Prescription Hook
 * 
 * React hook for prescription processing with real API calls.
 */

import { useState, useCallback } from 'react';
import {
    processPrescription,
    uploadPrescription,
    extractText,
    extractMedicines,
    searchPrescription,
    Medicine,
    PrescriptionSearchResult
} from '@/lib/api';

export type ScanStatus = 'idle' | 'uploading' | 'extracting' | 'parsing' | 'searching' | 'complete' | 'error';

interface UsePrescriptionResult {
    status: ScanStatus;
    prescriptionId: string | null;
    imageUrl: string | null;
    extractedText: string | null;
    medicines: Medicine[];
    searchResults: PrescriptionSearchResult | null;
    error: string | null;
    processFull: (file: File) => Promise<void>;
    reset: () => void;
}

export function usePrescription(): UsePrescriptionResult {
    const [status, setStatus] = useState<ScanStatus>('idle');
    const [prescriptionId, setPrescriptionId] = useState<string | null>(null);
    const [imageUrl, setImageUrl] = useState<string | null>(null);
    const [extractedText, setExtractedText] = useState<string | null>(null);
    const [medicines, setMedicines] = useState<Medicine[]>([]);
    const [searchResults, setSearchResults] = useState<PrescriptionSearchResult | null>(null);
    const [error, setError] = useState<string | null>(null);

    const processFull = useCallback(async (file: File) => {
        setError(null);
        setStatus('uploading');

        try {
            const result = await processPrescription(file, (step, data) => {
                switch (step) {
                    case 'uploading':
                        setStatus('uploading');
                        break;
                    case 'uploaded':
                        setPrescriptionId(data?.prescription_id);
                        setImageUrl(data?.image_url);
                        break;
                    case 'extracting':
                        setStatus('extracting');
                        break;
                    case 'ocr_complete':
                        setExtractedText(data?.text);
                        break;
                    case 'parsing':
                        setStatus('parsing');
                        break;
                    case 'extraction_complete':
                        setMedicines(data?.medicines || []);
                        break;
                    case 'searching':
                        setStatus('searching');
                        break;
                    case 'search_complete':
                        setSearchResults(data?.results);
                        break;
                }
            });

            setPrescriptionId(result.prescription_id);
            setImageUrl(result.image_url);
            setExtractedText(result.extracted_text);
            setMedicines(result.medicines);
            setSearchResults(result.search_results);
            setStatus('complete');
        } catch (err) {
            console.error('Prescription processing error:', err);
            setError(err instanceof Error ? err.message : 'Processing failed');
            setStatus('error');
        }
    }, []);

    const reset = useCallback(() => {
        setStatus('idle');
        setPrescriptionId(null);
        setImageUrl(null);
        setExtractedText(null);
        setMedicines([]);
        setSearchResults(null);
        setError(null);
    }, []);

    return {
        status,
        prescriptionId,
        imageUrl,
        extractedText,
        medicines,
        searchResults,
        error,
        processFull,
        reset,
    };
}
