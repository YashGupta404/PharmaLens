// PharmaLens Type Definitions

export interface Medicine {
  id: string;
  name: string;
  genericName?: string;
  dosage: string;
  frequency?: string;
  quantity?: number;
  isGeneric: boolean;
}

export interface PharmacyPrice {
  pharmacyId: string;
  pharmacyName: string;
  pharmacyLogo?: string;
  price: number;
  originalPrice?: number;
  discount?: number;
  packSize: string;
  inStock: boolean;
  deliveryDays?: number;
  url: string;
  lastUpdated: Date;
}

export interface MedicineSearchResult {
  medicine: Medicine;
  prices: PharmacyPrice[];
  cheapestPrice: PharmacyPrice | null;
  genericAlternatives?: GenericAlternative[];
  savings?: number;
}

export interface GenericAlternative {
  id: string;
  name: string;
  composition: string;
  priceRange: {
    min: number;
    max: number;
  };
  pharmaciesCount: number;
}

export interface PrescriptionScan {
  id: string;
  imageUrl: string;
  extractedText: string;
  medicines: Medicine[];
  status: ScanStatus;
  createdAt: Date;
  results?: MedicineSearchResult[];
}

export type ScanStatus = 
  | 'uploading'
  | 'processing'
  | 'extracting'
  | 'searching'
  | 'completed'
  | 'error';

export interface SearchHistory {
  id: string;
  query: string;
  medicinesCount: number;
  totalSavings: number;
  createdAt: Date;
  prescriptionScan?: PrescriptionScan;
}

export interface Pharmacy {
  id: string;
  name: string;
  logo: string;
  rating: number;
  reviewsCount: number;
  deliveryInfo: string;
  isVerified: boolean;
}
