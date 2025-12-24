/**
 * API Client
 * 
 * HTTP client for communicating with the PharmaLens backend API.
 */

// Backend API URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Types
export interface UploadResponse {
    success: boolean;
    message: string;
    prescription_id: string;
    image_url: string | null;
    optimized_url: string | null;
}

export interface OCRResponse {
    success: boolean;
    prescription_id: string;
    extracted_text: string;
    confidence: number;
    word_count: number;
}

export interface Medicine {
    id: string;
    name: string;
    generic_name?: string;
    dosage: string;
    frequency?: string;
    quantity?: number;
    is_generic: boolean;
}

export interface ExtractionResponse {
    success: boolean;
    prescription_id: string;
    medicines: Medicine[];
    raw_text: string;
}

export interface PharmacyPrice {
    pharmacy_id: string;
    pharmacy_name: string;
    product_name: string;
    price: number;
    original_price?: number;
    discount?: number;
    pack_size: string;
    in_stock: boolean;
    delivery_days?: number;
    url: string;
    image_url?: string;
    last_updated: string;
}

export interface SearchResult {
    success: boolean;
    medicine_name: string;
    dosage: string | null;
    total_results: number;
    pharmacies_searched: string[];
    prices: PharmacyPrice[];
    cheapest: PharmacyPrice | null;
    savings: number;
    search_id?: string;
}

export interface PrescriptionSearchResult {
    success: boolean;
    medicines_count: number;
    results: SearchResult[];
    total_savings: number;
    search_id?: string;
    prescription_id?: string;
}

// Helper function for API calls
async function apiCall<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const response = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
}

// API Functions

/**
 * Upload a prescription image
 */
export async function uploadPrescription(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/prescriptions/upload`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
        throw new Error(error.detail || 'Failed to upload prescription');
    }

    return response.json();
}

/**
 * Extract text from prescription using OCR
 */
export async function extractText(prescriptionId: string): Promise<OCRResponse> {
    return apiCall(`/prescriptions/${prescriptionId}/ocr`, {
        method: 'POST',
    });
}

/**
 * Extract medicines from prescription text using AI
 */
export async function extractMedicines(prescriptionId: string): Promise<ExtractionResponse> {
    return apiCall(`/prescriptions/${prescriptionId}/extract`, {
        method: 'POST',
    });
}

/**
 * Search for medicine prices
 */
export async function searchMedicine(
    medicineName: string,
    dosage?: string
): Promise<SearchResult> {
    return apiCall('/search/medicine', {
        method: 'POST',
        body: JSON.stringify({
            medicine_name: medicineName,
            dosage: dosage || null,
        }),
    });
}

/**
 * Search prices for all medicines in a prescription
 */
export async function searchPrescription(prescriptionId: string): Promise<PrescriptionSearchResult> {
    return apiCall(`/search/prescription/${prescriptionId}`, {
        method: 'POST',
    });
}

/**
 * Get prescription details
 */
export async function getPrescription(prescriptionId: string) {
    return apiCall(`/prescriptions/${prescriptionId}`);
}

/**
 * Full prescription processing pipeline
 */
export async function processPrescription(
    file: File,
    onProgress?: (step: string, data?: any) => void
): Promise<{
    prescription_id: string;
    image_url: string;
    extracted_text: string;
    medicines: Medicine[];
    search_results: PrescriptionSearchResult;
}> {
    // Step 1: Upload
    onProgress?.('uploading');
    const uploadResult = await uploadPrescription(file);

    if (!uploadResult.success) {
        throw new Error('Failed to upload prescription');
    }

    const prescriptionId = uploadResult.prescription_id;
    onProgress?.('uploaded', { prescription_id: prescriptionId, image_url: uploadResult.image_url });

    // Step 2: OCR
    onProgress?.('extracting');
    const ocrResult = await extractText(prescriptionId);
    onProgress?.('ocr_complete', { text: ocrResult.extracted_text, confidence: ocrResult.confidence });

    // Step 3: AI Extraction
    onProgress?.('parsing');
    const extractionResult = await extractMedicines(prescriptionId);
    onProgress?.('extraction_complete', { medicines: extractionResult.medicines });

    // Step 4: Price Search
    onProgress?.('searching');
    const searchResults = await searchPrescription(prescriptionId);
    onProgress?.('search_complete', { results: searchResults });

    return {
        prescription_id: prescriptionId,
        image_url: uploadResult.image_url || '',
        extracted_text: ocrResult.extracted_text,
        medicines: extractionResult.medicines,
        search_results: searchResults,
    };
}

/**
 * Health check
 */
export async function checkHealth() {
    return apiCall('/health');
}

// =====================================
// AI Crew (Multi-Agent System) API
// =====================================

export interface AgentStatus {
    agent: string;
    status: 'idle' | 'working' | 'completed' | 'error';
    message: string;
    progress: number;
}

export interface CrewProcessResponse {
    success: boolean;
    identified_medicines: Array<{
        name: string;
        generic: string;
        category: string;
        uses: string;
        confidence: number;
    }>;
    price_comparison: Array<{
        medicine: string;
        generic: string;
        prices: Array<{
            pharmacy: string;
            price: number;
            product: string;
            pack_size: string;
        }>;
        cheapest?: {
            pharmacy: string;
            price: number;
        };
    }>;
    agent_updates: AgentStatus[];
    error?: string;
}

/**
 * Process text with AI Crew (multi-agent system)
 */
export async function processWithCrew(ocrText: string): Promise<CrewProcessResponse> {
    return apiCall('/crew/process', {
        method: 'POST',
        body: JSON.stringify({ ocr_text: ocrText }),
    });
}

/**
 * Get AI Crew status info
 */
export async function getCrewStatus() {
    return apiCall('/crew/status');
}

// =====================================
// Search History API
// =====================================

export interface SearchHistoryItem {
    id: string;
    user_id: string;
    medicine_name: string;
    search_type: 'prescription' | 'manual';
    results_count: number;
    cheapest_price: number | null;
    cheapest_pharmacy: string | null;
    prescription_image_url: string | null;
    created_at: string;
}

export interface SaveSearchRequest {
    medicine_name: string;
    search_type?: 'prescription' | 'manual';
    results_count?: number;
    cheapest_price?: number;
    cheapest_pharmacy?: string;
    prescription_image_url?: string;
}

/**
 * Get user's search history
 */
export async function getSearchHistory(limit: number = 50): Promise<SearchHistoryItem[]> {
    return apiCall(`/history?limit=${limit}`);
}

/**
 * Save a search to history
 */
export async function saveSearchToHistory(search: SaveSearchRequest): Promise<SearchHistoryItem> {
    return apiCall('/history', {
        method: 'POST',
        body: JSON.stringify(search),
    });
}

/**
 * Delete a search from history
 */
export async function deleteSearchFromHistory(searchId: string): Promise<void> {
    return apiCall(`/history/${searchId}`, {
        method: 'DELETE',
    });
}
