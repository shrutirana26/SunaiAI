# ⚖️ SUNI-AI
An AI-powered Legal-Tech Platform for FIR Analysis, IPC Identification & Bail Eligibility.

---

## 📋 Overview

**SUNI-AI** is a comprehensive legal-tech web application designed to make legal processes more accessible, transparent, and understandable for everyone — regardless of their legal background or language.

The platform leverages AI to analyze FIR (First Information Report) documents, automatically identify relevant IPC (Indian Penal Code) sections, assess bail eligibility, and connect users with nearby legal aid resources. With multi-language support at its core, SUNI-AI breaks down the language barrier that often prevents citizens from understanding their own legal rights.

---

## ✨ Key Features

- **📄 FIR Document Analysis:** Upload or paste FIR documents and get an instant AI-powered breakdown of the case, charges, and key details.
- **📚 IPC Section Identification:** Automatically maps FIR content to the relevant IPC sections with plain-language explanations of each charge.
- **🔓 Bail Eligibility Checker:** Analyzes the identified IPC sections and case context to provide a clear bail eligibility assessment with supporting reasoning.
- **📁 Case Dashboard:** A centralized dashboard to manage, track, and review all active and past cases in one place.
- **🗄️ Document Vault:** Securely store, organize, and retrieve legal documents, FIRs, and case files.
- **📍 Nearby Legal Aid Search:** Geolocation-based search to find lawyers, legal aid societies, and court services closest to the user.
- **🌐 Multi-Language Support:** Full support for regional languages to ensure legal help is accessible to every citizen.

---

## 🚀 Getting Started

### Prerequisites

- **[Node.js](https://nodejs.org/)** (v18+)
- **[Python](https://www.python.org/)** (v3.10+ — for the AI/NLP model server)
- **[PostgreSQL](https://www.postgresql.org/)** (Ensure your database is running and accessible)
- **[Git](https://git-scm.com/)**

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/suni-ai.git
cd suni-ai

# Install dependencies for both frontend and backend
cd backend && npm install
cd ../frontend && npm install

# Install Python dependencies for the AI model server
cd ../model && pip install -r requirements.txt
```

### Database Setup & Seeding

The application uses Prisma ORM and requires an initial dataset of IPC sections, bail conditions, and legal aid centers.

```bash
cd backend

# Create your .env file with DATABASE_URL and API keys
cp .env.example .env

# Run migrations and seed the database with IPC and legal data
npm run db:migrate
npm run db:seed
```

### Running the Project

You can start all services simultaneously using the provided script:

```bash
# From the root directory
./start.sh       # Linux / macOS
.\start.ps1      # Windows (PowerShell)
```

Alternatively, run each service separately:

- **Backend:** `cd backend && npm run dev`
- **Frontend:** `cd frontend && npm run dev`
- **AI Model Server:** `cd model && python app.py`

> By default, the application launches in **Light Mode**. You can toggle **Dark Mode** from the settings panel in the UI.

---

## 🎮 Using SUNI-AI

1. **Sign up / Log in** to your account.
2. Navigate to the **FIR Analyzer** from the sidebar.
3. **Upload a FIR document** (PDF or image) or paste the raw FIR text.
4. The AI will automatically:
   - Extract and summarize the case details.
   - Identify all applicable **IPC Sections** with descriptions.
   - Run a **Bail Eligibility** assessment.
5. Save the analysis to your **Document Vault** or share it directly.
6. Use the **Legal Aid Finder** to locate nearby lawyers or legal aid services.

---

## 📁 Project Structure
suni-ai/
├── frontend/        # React + Vite application (Zustand, Tailwind CSS, i18n)
├── backend/         # Node.js + Express REST API (Prisma, JWT Auth)
├── model/           # Python AI/NLP server (FIR parsing, IPC mapping, bail logic)
└── README.md        # You are here
---

## 🌍 Multi-Language Support

SUNI-AI currently supports the following languages:

| Language   | Code  | Status     |
|------------|-------|------------|
| English    | `en`  | ✅ Complete |
| Hindi      | `hi`  | ✅ Complete |
| Marathi    | `mr`  | ✅ Complete |
| Tamil      | `ta`  | 🚧 In Progress |
| Telugu     | `te`  | 🚧 In Progress |

To contribute a new language, see [`/frontend/src/locales/`](./frontend/src/locales/).

---

## 🤝 Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change, then submit a pull request.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](./LICENSE) file for details.

---

> *"Justice delayed is justice denied — SUNI-AI exists to make sure it's never denied because it was too hard to understand."*
