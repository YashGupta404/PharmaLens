import type { MedicineSearchResult, SearchHistory } from "@/types/pharmalens";

export const mockSearchResults: MedicineSearchResult[] = [
  {
    medicine: {
      id: "med-1",
      name: "Crocin 650mg",
      genericName: "Paracetamol",
      dosage: "650mg",
      frequency: "3 times daily",
      quantity: 15,
      isGeneric: false
    },
    prices: [
      {
        pharmacyId: "ph-1",
        pharmacyName: "1mg",
        price: 28,
        originalPrice: 35,
        discount: 20,
        packSize: "Strip of 15 tablets",
        inStock: true,
        deliveryDays: 2,
        url: "https://1mg.com",
        lastUpdated: new Date()
      },
      {
        pharmacyId: "ph-2",
        pharmacyName: "PharmEasy",
        price: 31,
        originalPrice: 35,
        discount: 11,
        packSize: "Strip of 15 tablets",
        inStock: true,
        deliveryDays: 1,
        url: "https://pharmeasy.com",
        lastUpdated: new Date()
      },
      {
        pharmacyId: "ph-3",
        pharmacyName: "Netmeds",
        price: 33,
        originalPrice: 35,
        discount: 6,
        packSize: "Strip of 15 tablets",
        inStock: true,
        deliveryDays: 3,
        url: "https://netmeds.com",
        lastUpdated: new Date()
      },
      {
        pharmacyId: "ph-4",
        pharmacyName: "Apollo Pharmacy",
        price: 35,
        packSize: "Strip of 15 tablets",
        inStock: false,
        url: "https://apollopharmacy.com",
        lastUpdated: new Date()
      }
    ],
    cheapestPrice: null,
    genericAlternatives: [
      {
        id: "gen-1",
        name: "Dolo 650",
        composition: "Paracetamol 650mg",
        priceRange: { min: 22, max: 30 },
        pharmaciesCount: 12
      },
      {
        id: "gen-2",
        name: "P-650",
        composition: "Paracetamol 650mg",
        priceRange: { min: 18, max: 25 },
        pharmaciesCount: 8
      }
    ],
    savings: 7
  },
  {
    medicine: {
      id: "med-2",
      name: "Azithral 500",
      genericName: "Azithromycin",
      dosage: "500mg",
      frequency: "Once daily",
      quantity: 3,
      isGeneric: false
    },
    prices: [
      {
        pharmacyId: "ph-2",
        pharmacyName: "PharmEasy",
        price: 85,
        originalPrice: 120,
        discount: 29,
        packSize: "Strip of 3 tablets",
        inStock: true,
        deliveryDays: 1,
        url: "https://pharmeasy.com",
        lastUpdated: new Date()
      },
      {
        pharmacyId: "ph-1",
        pharmacyName: "1mg",
        price: 92,
        originalPrice: 120,
        discount: 23,
        packSize: "Strip of 3 tablets",
        inStock: true,
        deliveryDays: 2,
        url: "https://1mg.com",
        lastUpdated: new Date()
      },
      {
        pharmacyId: "ph-5",
        pharmacyName: "Tata 1mg",
        price: 95,
        originalPrice: 120,
        discount: 21,
        packSize: "Strip of 3 tablets",
        inStock: true,
        deliveryDays: 2,
        url: "https://tata1mg.com",
        lastUpdated: new Date()
      },
      {
        pharmacyId: "ph-3",
        pharmacyName: "Netmeds",
        price: 105,
        originalPrice: 120,
        discount: 12,
        packSize: "Strip of 3 tablets",
        inStock: true,
        deliveryDays: 3,
        url: "https://netmeds.com",
        lastUpdated: new Date()
      }
    ],
    cheapestPrice: null,
    genericAlternatives: [
      {
        id: "gen-3",
        name: "Zithromax Generic",
        composition: "Azithromycin 500mg",
        priceRange: { min: 65, max: 85 },
        pharmaciesCount: 10
      }
    ],
    savings: 35
  },
  {
    medicine: {
      id: "med-3",
      name: "Pan-D",
      genericName: "Pantoprazole + Domperidone",
      dosage: "40mg + 30mg",
      frequency: "Before breakfast",
      quantity: 15,
      isGeneric: false
    },
    prices: [
      {
        pharmacyId: "ph-3",
        pharmacyName: "Netmeds",
        price: 125,
        originalPrice: 165,
        discount: 24,
        packSize: "Strip of 15 capsules",
        inStock: true,
        deliveryDays: 2,
        url: "https://netmeds.com",
        lastUpdated: new Date()
      },
      {
        pharmacyId: "ph-1",
        pharmacyName: "1mg",
        price: 132,
        originalPrice: 165,
        discount: 20,
        packSize: "Strip of 15 capsules",
        inStock: true,
        deliveryDays: 2,
        url: "https://1mg.com",
        lastUpdated: new Date()
      },
      {
        pharmacyId: "ph-2",
        pharmacyName: "PharmEasy",
        price: 138,
        originalPrice: 165,
        discount: 16,
        packSize: "Strip of 15 capsules",
        inStock: true,
        deliveryDays: 1,
        url: "https://pharmeasy.com",
        lastUpdated: new Date()
      },
      {
        pharmacyId: "ph-4",
        pharmacyName: "Apollo Pharmacy",
        price: 155,
        originalPrice: 165,
        discount: 6,
        packSize: "Strip of 15 capsules",
        inStock: true,
        deliveryDays: 1,
        url: "https://apollopharmacy.com",
        lastUpdated: new Date()
      },
      {
        pharmacyId: "ph-6",
        pharmacyName: "MedPlus",
        price: 160,
        originalPrice: 165,
        discount: 3,
        packSize: "Strip of 15 capsules",
        inStock: true,
        deliveryDays: 2,
        url: "https://medplusmart.com",
        lastUpdated: new Date()
      }
    ],
    cheapestPrice: null,
    genericAlternatives: [
      {
        id: "gen-4",
        name: "Pantocid-D",
        composition: "Pantoprazole 40mg + Domperidone 30mg",
        priceRange: { min: 95, max: 130 },
        pharmaciesCount: 15
      }
    ],
    savings: 40
  }
];

// Set cheapest price for each result
mockSearchResults.forEach(result => {
  const sorted = [...result.prices].sort((a, b) => a.price - b.price);
  result.cheapestPrice = sorted[0] || null;
});

export const mockSearchHistory: SearchHistory[] = [
  {
    id: "hist-1",
    query: "Crocin 650mg, Azithral 500, Pan-D",
    medicinesCount: 3,
    totalSavings: 82,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2) // 2 hours ago
  },
  {
    id: "hist-2",
    query: "Metformin 500mg, Ecosprin 75",
    medicinesCount: 2,
    totalSavings: 45,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24) // 1 day ago
  },
  {
    id: "hist-3",
    query: "Vitamin D3 60K, Calcium tablets",
    medicinesCount: 2,
    totalSavings: 120,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3) // 3 days ago
  },
  {
    id: "hist-4",
    query: "Amoxicillin 500mg, Cetirizine 10mg",
    medicinesCount: 2,
    totalSavings: 35,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 7) // 1 week ago
  }
];

export const mockExtractedMedicines = [
  "Crocin 650mg",
  "Azithral 500",
  "Pan-D 40mg"
];
