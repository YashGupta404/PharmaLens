# PharmaLens

🔬 **AI-Powered Prescription Scanner & Medicine Price Comparison Platform**

PharmaLens is a full-stack web application that scans medical prescriptions and finds the cheapest available medicine prices across Indian pharmacies.

## 🏗️ Project Structure

```
pharma-lens/
├── frontend/          # React + Vite + TypeScript frontend
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
├── backend/           # Python FastAPI backend (coming soon)
│   ├── app/
│   ├── requirements.txt
│   └── ...
├── docker-compose.yml # Local development orchestration
└── README.md
```

## 🚀 Features

### Phase 1 – Core MVP
- ✅ Upload prescription image
- 🔄 OCR text extraction
- 🔄 Extract medicine names + dosage using AI/LLM
- 🔄 Search prices across multiple pharmacy websites
- 🔄 Compare prices + suggest cheapest option
- 🔄 Show links + price breakdown

### Phase 2 – Agent Intelligence
- 🔄 Extract generic alternatives
- 🔄 Re-run search if medicine not found
- 🔄 Retry failed websites and fallback sites
- 🔄 Detect duplicates + filter noise
- 🔄 Save search history
- 🔄 Provide explanation for recommendation

Legend: ✅ Complete | 🔄 In Progress | ⏳ Planned

## 🛠️ Tech Stack

### Frontend
- **Framework**: React + Vite + TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: TanStack Query

### Backend
- **Framework**: FastAPI (Python)
- **Authentication**: Firebase Auth
- **Database**: Firestore
- **OCR**: Tesseract / PaddleOCR
- **AI/LLM**: OpenAI GPT
- **Scraping**: Playwright / BeautifulSoup

### DevOps
- **Containerization**: Docker
- **Frontend Hosting**: Vercel
- **Backend Hosting**: AWS

## 📦 Getting Started

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## ⚠️ Disclaimer

> **EDUCATIONAL PROJECT ONLY**
> 
> This is a **non-commercial educational project** created for learning purposes. 
> 
> - All price data is sourced from **publicly available** pharmacy websites
> - Data is used solely for **price comparison** to help users find affordable medicines
> - This project does **NOT** store, redistribute, or commercially use any scraped data
> - We access only publicly visible information that any user can see in their browser
> - No login credentials, personal data, or protected content is accessed
> 
> **For Pharmacies:** If you represent one of the pharmacy websites and have concerns, please reach out. We respect your data and will comply with reasonable requests.

## 📄 License

MIT License

