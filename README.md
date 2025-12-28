<p align="center">
  <img src="https://img.shields.io/badge/PharmaLens-AI%20Powered-0ea5e9?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiPjxwYXRoIGQ9Ik0xMiA1djE0TTE1IDhIMTAuNUE1LjUgNS41IDAgMCAwIDEwLjUgMTlIMTUiLz48L3N2Zz4=&logoColor=white" alt="PharmaLens" height="40"/>
</p>

<h1 align="center">🔬 PharmaLens</h1>

<p align="center">
  <strong>AI-Powered Prescription Scanner & Medicine Price Comparison Platform</strong>
</p>

<p align="center">
  <a href="https://pharma-lens-yg.vercel.app">
    <img src="https://img.shields.io/badge/🚀_Live_Demo-Visit_App-0ea5e9?style=for-the-badge" alt="Live Demo"/>
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/React-18.3.1-61DAFB?style=flat-square&logo=react&logoColor=white" alt="React"/>
  <img src="https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/TypeScript-5.8-3178C6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript"/>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/TailwindCSS-3.4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white" alt="TailwindCSS"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Google_Cloud_Vision-OCR-4285F4?style=flat-square&logo=googlecloud&logoColor=white" alt="Google Vision"/>
  <img src="https://img.shields.io/badge/Groq-Llama_3.3-F55036?style=flat-square&logo=meta&logoColor=white" alt="Groq"/>
  <img src="https://img.shields.io/badge/LangChain-Agents-1C3C3C?style=flat-square&logo=langchain&logoColor=white" alt="LangChain"/>
  <img src="https://img.shields.io/badge/Supabase-Database-3FCF8E?style=flat-square&logo=supabase&logoColor=white" alt="Supabase"/>
</p>

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🛠️ Tech Stack](#️-tech-stack)
- [🤖 AI & Agentic Tools](#-ai--agentic-tools)
- [📦 Installation](#-installation)
- [🚀 Running Locally](#-running-locally)
- [🌐 Deployment](#-deployment)
- [📖 How It Works](#-how-it-works)
- [🔧 API Endpoints](#-api-endpoints)
- [📂 Project Structure](#-project-structure)
- [⚠️ Disclaimer](#️-disclaimer)
- [📄 License](#-license)
- [🤝 Contributing](#-contributing)

---

## 🎯 Overview

**PharmaLens** is a full-stack web application that leverages cutting-edge AI technologies to scan medical prescriptions and find the cheapest available medicine prices across major Indian online pharmacies. 

Upload a prescription, let our AI extract the medicines, and instantly compare prices across **PharmEasy**, **1mg**, **Netmeds**, and **Apollo Pharmacy** — saving users up to **80%** on their medicine costs.

### 🌟 Why PharmaLens?

- 💰 **Save Money**: Compare prices across 4+ pharmacies instantly
- 🤖 **AI-Powered**: State-of-the-art OCR and NLP for accurate extraction
- ⚡ **Real-time Streaming**: Get results as they come in — no waiting!
- 💊 **Generic Alternatives**: Discover affordable generic options
- 🔒 **Privacy First**: No prescription data is stored

---

## ✨ Features

### Core Features

| Feature | Description | Status |
|---------|-------------|--------|
| 📸 **Prescription Upload** | Drag & drop or click to upload prescription images | ✅ Complete |
| 🔍 **AI OCR Extraction** | Google Cloud Vision extracts text from prescriptions | ✅ Complete |
| 💊 **Medicine Parsing** | Groq Llama 3.3 identifies medicines, dosages & quantities | ✅ Complete |
| 💵 **Price Comparison** | Real-time price scraping from multiple pharmacies | ✅ Complete |
| 📊 **Streaming Results** | Server-Sent Events for instant result delivery | ✅ Complete |
| 🏪 **Multi-Pharmacy Search** | PharmEasy, 1mg, Netmeds, Apollo Pharmacy | ✅ Complete |

### Advanced Features

| Feature | Description | Status |
|---------|-------------|--------|
| 🧪 **Generic Alternatives** | AI suggests cheaper generic medicine options | ✅ Complete |
| 🤖 **AI Agent Chat** | LangChain-powered conversational medicine search | ✅ Complete |
| 🔐 **User Authentication** | Supabase-based secure user auth | ✅ Complete |
| 📱 **Responsive Design** | Works seamlessly on mobile and desktop | ✅ Complete |
| 🌙 **Dark Mode** | Eye-friendly dark theme support | ✅ Complete |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │   React + TypeScript + Vite + TailwindCSS + shadcn/ui   │    │
│  │                                                         │    │
│  │   ┌──────────┐  ┌──────────┐  ┌───────────────────┐    │    │
│  │   │   Auth   │  │  Upload  │  │  Results Display  │    │    │
│  │   │  Pages   │  │  Scanner │  │  + SSE Streaming  │    │    │
│  │   └──────────┘  └──────────┘  └───────────────────┘    │    │
│  └─────────────────────────────────────────────────────────┘    │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS / SSE
┌────────────────────────────▼────────────────────────────────────┐
│                         BACKEND                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              FastAPI + Python 3.11+                      │    │
│  │                                                         │    │
│  │   ┌────────────────┐    ┌─────────────────────────┐     │    │
│  │   │   OCR Service  │    │   AI Parser Service     │     │    │
│  │   │ (Google Vision)│    │   (Groq + Llama 3.3)    │     │    │
│  │   └────────────────┘    └─────────────────────────┘     │    │
│  │                                                         │    │
│  │   ┌─────────────────────────────────────────────────┐   │    │
│  │   │           Pharmacy Scrapers                      │   │    │
│  │   │  ┌──────────┐ ┌────────┐ ┌───────┐ ┌────────┐   │   │    │
│  │   │  │PharmEasy │ │  1mg   │ │Netmeds│ │ Apollo │   │   │    │
│  │   │  │  (HTTP)  │ │ (HTTP) │ │(Play) │ │ (HTTP) │   │   │    │
│  │   │  └──────────┘ └────────┘ └───────┘ └────────┘   │   │    │
│  │   └─────────────────────────────────────────────────┘   │    │
│  │                                                         │    │
│  │   ┌────────────────────────────────────────────────┐    │    │
│  │   │        LangChain AI Agent (Groq LLM)           │    │    │
│  │   │     Agentic search + summarization             │    │    │
│  │   └────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
  ┌──────────┐        ┌──────────┐         ┌──────────┐
  │ Supabase │        │Cloudinary│         │   Groq   │
  │    DB    │        │  Images  │         │   LLM    │
  └──────────┘        └──────────┘         └──────────┘
```

---

## 🛠️ Tech Stack

### Frontend

| Technology | Purpose | Version |
|------------|---------|---------|
| ⚛️ **React** | UI Framework | 18.3.1 |
| 📘 **TypeScript** | Type Safety | 5.8.3 |
| ⚡ **Vite** | Build Tool | 5.4.19 |
| 🎨 **TailwindCSS** | Styling | 3.4.17 |
| 🧩 **shadcn/ui** | Component Library | Latest |
| 📡 **TanStack Query** | Data Fetching | 5.83.0 |
| 🔗 **React Router** | Navigation | 6.30.1 |
| 📝 **React Hook Form** | Forms | 7.61.1 |
| ✅ **Zod** | Validation | 3.25.76 |
| 🔔 **Sonner** | Notifications | 1.7.4 |

### Backend

| Technology | Purpose | Version |
|------------|---------|---------|
| 🚀 **FastAPI** | API Framework | 0.109+ |
| 🐍 **Python** | Runtime | 3.11+ |
| 🔐 **Pydantic** | Data Validation | 2.5+ |
| 🌐 **HTTPX** | Async HTTP Client | 0.26+ |
| 🎭 **Playwright** | Browser Automation | 1.40+ |
| 🍲 **BeautifulSoup4** | HTML Parsing | 4.12+ |
| 🗄️ **Supabase** | Database & Auth | 2.3+ |
| ☁️ **Cloudinary** | Image Storage | 1.38+ |

---

## 🤖 AI & Agentic Tools

PharmaLens leverages state-of-the-art AI and agentic technologies:

### 🔍 OCR & Vision

| Tool | Description |
|------|-------------|
| **Google Cloud Vision API** | Enterprise-grade OCR for prescription text extraction with 99%+ accuracy |

### 🧠 Large Language Models

| Tool | Model | Purpose |
|------|-------|---------|
| **Groq** | Llama 3.3 70B | Medicine extraction, parsing, and generic alternative suggestions |
| **OpenAI** | GPT-4 (fallback) | Alternative LLM for complex parsing scenarios |

### 🤖 Agentic AI Framework

| Tool | Purpose |
|------|---------|
| **LangChain** | Orchestration framework for building AI agents |
| **LangChain Core** | Core abstractions for chains, prompts, and memory |
| **LangChain Groq** | Groq LLM integration for fast inference |

### 🕵️ Agentic Capabilities

```python
# PharmaLens AI Agent Features:
- 🔄 Multi-step reasoning for medicine name resolution
- 🔍 Parallel pharmacy search across 4+ sources
- 📊 Intelligent result aggregation and comparison
- 💬 Natural language query understanding
- 🎯 Context-aware generic medicine suggestions
- 🔁 Automatic retry with alternative search terms
```

---

## 📦 Installation

### Prerequisites

- **Node.js** >= 18.x
- **Python** >= 3.11
- **npm** or **bun** package manager
- **Git**

### Clone the Repository

```bash
git clone https://github.com/YashGupta404/PharmaLens.git
cd PharmaLens
```

---

## 🚀 Running Locally

### 1️⃣ Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for Netmeds scraping)
playwright install chromium

# Create .env file (copy from example and fill in values)
cp .env.example .env
```

#### Backend Environment Variables (`.env`)

```env
# Application
APP_ENV=development
DEBUG=true

# Groq AI (Free tier available)
GROQ_API_KEY=your_groq_api_key

# Google Cloud Vision (for OCR)
GOOGLE_APPLICATION_CREDENTIALS=./credentials/google-vision.json
# OR for production:
GOOGLE_CREDENTIALS_BASE64=base64_encoded_credentials

# Cloudinary (for image uploads)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Supabase (for database & auth)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

#### Run Backend Server

```bash
# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at: `http://localhost:8000`  
API Documentation (Swagger): `http://localhost:8000/docs`

---

### 2️⃣ Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (using npm)
npm install

# OR using bun (faster)
bun install

# Create .env file
cp .env.example .env
```

#### Frontend Environment Variables (`.env`)

```env
# Backend API URL
VITE_API_URL=http://localhost:8000/api

# Supabase Configuration
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

#### Run Frontend Development Server

```bash
# Start the Vite dev server
npm run dev

# OR using bun
bun dev
```

The frontend will be available at: `http://localhost:5173`

---

## 🌐 Deployment

### Live Demo

🚀 **Frontend (Vercel)**: [https://pharma-lens-yg.vercel.app](https://pharma-lens-yg.vercel.app)

### Deploy Your Own

#### Frontend (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

#### Backend (Render/Railway)

1. Push your code to GitHub
2. Connect to Render/Railway
3. Set environment variables
4. Deploy with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## 📖 How It Works

<p align="center">
  <img src="https://mermaid.ink/img/pako:eNp9kk1uwzAMhK9CcJ0c4O6LrLprF0URSQ6VuJBlO3_o3UvZTlO0RbSSNJ-GIzE3x6IizjK-FpYaNgk3SLkNLBKXvGzhaD1djCYWtBBJpCaFt8aRTt7Ox_d3z88P0Rl7sJpOWrGH45HvvRXDIjlLhfJsZHlqtCPj-6RB41CHJT1m5zqptKDJR1x51hn7N1feeG0_Nd3nVmhNpBDyZ0HH0W1KZPRkPKfLzAd6R6Q853UpNbWeSJFDLG2pI-8q6bUlWYfEpULHySrlVJuQTsY6rmjxJ5m2phCOStnWOtQxJJmM4VIYy29ZPGhLvAhVLI2qQlYFFxHWIdROaB2i3NWGu4Dny4t_-RuQMpFH?type=png" alt="How It Works Flow" width="800"/>
</p>

### Step-by-Step Process

1. **📸 Upload Prescription**
   - User uploads a prescription image (JPEG, PNG, PDF)
   - Image is uploaded to Cloudinary for processing

2. **🔍 OCR Text Extraction**
   - Google Cloud Vision API extracts all text from the prescription
   - Handwritten and printed text are both supported

3. **💊 AI Medicine Parsing**
   - Groq's Llama 3.3 70B model analyzes the extracted text
   - Identifies medicine names, dosages, quantities, and frequencies
   - Suggests generic alternatives where available

4. **🔎 Real-time Price Search**
   - Concurrent scraping across 4 pharmacies using async I/O
   - Results stream to the frontend via Server-Sent Events (SSE)
   - Each pharmacy result appears instantly as it's fetched

5. **📊 Price Comparison**
   - Results are aggregated and sorted by price
   - Cheapest option is highlighted
   - Direct links to purchase are provided

6. **💰 Save Money!**
   - User views the best deals and clicks to purchase
   - Average savings: 30-80% compared to local pharmacy prices

---

## 🔧 API Endpoints

### Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/ping` | Simple ping test |

### Prescriptions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/prescriptions/upload` | Upload prescription image |
| `POST` | `/api/prescriptions/analyze` | Analyze prescription with OCR + AI |

### Medicine Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/search/medicine/{name}` | Search medicine by name |
| `GET` | `/api/search/stream/{name}` | SSE stream for real-time results |

### AI Agent

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/agent/query` | Natural language medicine query |
| `POST` | `/api/agent/search` | Agent-powered pharmacy search |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/signup` | User registration |
| `POST` | `/api/auth/login` | User login |
| `POST` | `/api/auth/logout` | User logout |

---

## 📂 Project Structure

```
PharmaLens/
├── 📁 frontend/                    # React Frontend Application
│   ├── 📁 src/
│   │   ├── 📁 components/          # Reusable UI components
│   │   │   ├── 📁 ui/              # shadcn/ui components
│   │   │   └── ...                 # App-specific components
│   │   ├── 📁 pages/               # Page components
│   │   │   ├── Index.tsx           # Home page with scanner
│   │   │   ├── Auth.tsx            # Authentication page
│   │   │   └── HowItWorks.tsx      # How it works page
│   │   ├── 📁 hooks/               # Custom React hooks
│   │   ├── 📁 lib/                 # Utility functions
│   │   ├── 📁 context/             # React context providers
│   │   └── 📁 types/               # TypeScript type definitions
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── vite.config.ts
│   └── vercel.json
│
├── 📁 backend/                     # FastAPI Backend Application
│   ├── 📁 app/
│   │   ├── 📁 api/
│   │   │   └── 📁 routes/          # API route handlers
│   │   │       ├── health.py       # Health check routes
│   │   │       ├── prescriptions.py # Prescription routes
│   │   │       ├── search.py       # Medicine search routes
│   │   │       ├── auth.py         # Authentication routes
│   │   │       └── agent.py        # AI agent routes
│   │   ├── 📁 services/            # Business logic services
│   │   │   ├── ocr.py              # Google Vision OCR
│   │   │   ├── ai_parser.py        # Groq AI medicine parsing
│   │   │   ├── price_search.py     # Price aggregation
│   │   │   └── 📁 scrapers/        # Pharmacy scrapers
│   │   │       ├── pharmeasy.py    # PharmEasy scraper
│   │   │       ├── onemg_http.py   # 1mg scraper
│   │   │       ├── netmeds_http.py # Netmeds scraper
│   │   │       └── apollo_http.py  # Apollo scraper
│   │   ├── 📁 agent/               # AI Agent modules
│   │   │   ├── agent.py            # LangChain agent
│   │   │   ├── tools.py            # Agent tools
│   │   │   └── knowledge_base.py   # Medicine knowledge base
│   │   ├── 📁 models/              # Pydantic models
│   │   ├── config.py               # App configuration
│   │   └── main.py                 # FastAPI app entry point
│   ├── 📁 credentials/             # API credentials (gitignored)
│   ├── requirements.txt
│   └── Dockerfile
│
├── .gitignore
├── LICENSE
└── README.md
```

---

## ⚠️ Disclaimer

> **🎓 EDUCATIONAL PROJECT ONLY**
> 
> This is a **non-commercial educational project** created for learning and demonstration purposes.
> 
> - ✅ All price data is sourced from **publicly available** pharmacy websites
> - ✅ Data is used solely for **price comparison** to help users find affordable medicines
> - ✅ This project does **NOT** store, redistribute, or commercially use any scraped data
> - ✅ We access only publicly visible information that any user can see in their browser
> - ✅ No login credentials, personal data, or protected content is accessed
> 
> **For Pharmacies:** If you represent one of the pharmacy websites and have concerns, please reach out. We respect your data and will comply with reasonable requests.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 PharmaLens

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/YashGupta404/PharmaLens/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YashGupta404/PharmaLens/discussions)

---

<p align="center">
  <strong>Made with ❤️ for affordable healthcare in India</strong>
</p>

<p align="center">
  <a href="#-pharmalens">⬆️ Back to Top</a>
</p>
