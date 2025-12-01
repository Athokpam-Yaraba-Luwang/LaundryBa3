# LaundryBa Enterprise

A comprehensive laundry management system powered by AI agents, consisting of a Business App and a Customer App.

deployed in google cloud visit
customer app: https://laundryba-customer-984388967128.us-central1.run.app/

bussiness app: https://laundryba-business-984388967128.us-central1.run.app/intake

## 📂 Project Structure

```
LaundryBa3/
├── agents/                 # AI Agents & Shared Logic
│   ├── memory_bank.py      # Database Access Layer (SQLite)
│   ├── vision_agent.py     # Image Analysis (Gemini)
│   ├── fabric_expert_agent.py
│   └── ...
├── business_app/           # Business Dashboard (Flask)
│   ├── api/                # API Blueprints
│   ├── templates/          # HTML Templates (Tailwind)
│   ├── static/             # Static Assets
│   ├── Dockerfile          # Cloud Run Config
│   └── app.py              # Entrypoint
├── customer_app/           # Customer Portal (Flask)
│   ├── api/                # API Blueprints
│   ├── templates/          # HTML Templates (Tailwind)
│   ├── Dockerfile          # Cloud Run Config
│   └── app.py              # Entrypoint
├── google/                 # Local ADK Shims
├── docs/                   # Documentation
├── scripts/                # Helper Scripts
├── config.py               # Centralized Configuration
├── cloudbuild.yaml         # CI/CD Pipeline
├── docker-compose.yml      # Local Development
└── requirements.txt        # Python Dependencies
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Google Cloud Project with Vertex AI API enabled
- Gemini API Key

### Local Development

1.  **Setup Environment**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Configure Environment Variables**
    Create a `.env` file:
    ```env
    GOOGLE_API_KEY=your_api_key
    GEMINI_API_KEY=your_api_key
    ```

3.  **Run Locally**
    ```bash
    ./scripts/start_local.sh
    ```
    - Business App: http://localhost:5000
    - Customer App: http://localhost:5001

## ☁️ Deployment (Google Cloud Run)

This project is configured for **Google Cloud Build**.

1.  **Trigger**: Push to `main` branch on GitHub.
2.  **Config**: `cloudbuild.yaml` handles building and deploying both apps.
3.  **Permissions**: Ensure the Cloud Build service account has permissions to deploy to Cloud Run.

### Manual Deployment
```bash
gcloud run deploy laundryba-business --source .
gcloud run deploy laundryba-customer --source .
```

## 🧠 AI Agents
The system uses a multi-agent architecture:
- **Vision Agent**: Detects clothing items from images.
- **Fabric Expert**: Analyzes fabric type and care instructions.
- **Offer Agent**: Generates personalized discounts.
- **Analytics Agent**: Provides business insights.

## 📄 License
Proprietary software.
