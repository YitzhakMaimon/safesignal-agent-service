# SafeSignal — Digital Distress Detection System

SafeSignal is an AI-powered web application that identifies and assesses signs of emotional distress, cyberbullying, social exclusion, and suicidal ideation in online content — posts, comments, and chat messages.

The system is designed to assist educators, social workers, and community organizations in identifying individuals who may require attention or intervention.

> **Disclaimer:** SafeSignal is a decision-support tool. It does not provide medical diagnoses and should not replace professional mental health assessment or emergency intervention.

---

## Architecture Overview

```
User (Browser)
     │ HTTP POST
     ▼
Flask App (safe_signal.py)
     │ invoke_agent()
     ▼
Bedrock Agent (INDHHZGRD2 · alias E4SR5MTKOO)
     │
     ├── STEP 1 (always): RAG → Knowledge Base (S3 + OpenSearch)
     │         retrieves official guidance documents
     │
     └── STEP 2 (conditional): Action Groups
               ├── λ log_incident  → DynamoDB (SafeSignalHistory)
               └── λ send_alert    → Amazon SES → email to responders
```

**Architecture rules:**
1. Flask never invokes Lambda directly — only the Bedrock Agent triggers Lambdas via Action Groups
2. The Agent always queries RAG first; only then decides whether to invoke Action Groups
3. `log_incident` runs on every distress detection; `send_alert` runs for categories 1, 2, and 3
4. `/history` reads DynamoDB directly via `boto3.scan()` — read-only, no Lambda needed

---

## Distress Categories

| Category | Label | Action |
|---|---|---|
| **1** | Suicide Risk | Immediate action — ERAN 1201, MDA 101, Police 100 |
| **2** | Mental Distress | Help required — ERAN 1201, MDA 101, Hotline 105 |
| **3** | Cyberbullying | Identify & Assist — Hotline 105, Sahar, Police 100 |

Each category triggers a `send_alert` Lambda → SES email to the configured responder, and displays a full support resources panel in the UI.

---

## Key Features

- **Bedrock Agent + RAG** — Semantic retrieval from curated knowledge base documents (Ministry of Health, ERAN, Hotline 105) combined with agent-based orchestration
- **3-tier distress classification** — Categories 1–3 with category-specific response banners and support resources
- **Recurring distress detection** — Warns when a user has submitted 3+ distress posts (tracked in DynamoDB per `user_id`)
- **Automated email alerts** — `send_alert` Lambda sends SES emails on every categorized incident
- **Incident history** — `/history` page shows all logged incidents from DynamoDB
- **Live status bar** — Polls `/status` every 30 seconds: EC2 connectivity, Bedrock Agent, Email Alert state
- **Radar dashboard UI** — Cyber-themed interface with animated radar, category banners, and support resource panel

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask |
| Frontend | HTML5, CSS3, Jinja2 |
| AI Orchestration | Amazon Bedrock Agent (Nova Micro) |
| RAG | Bedrock Knowledge Base (S3 + OpenSearch) |
| Incident Logging | AWS Lambda + DynamoDB |
| Alert Delivery | AWS Lambda + Amazon SES |
| Data Processing | pandas (CSV export), JSON |
| Cloud SDK | boto3 |
| Containerization | Docker, Docker Compose |

---

## Project Structure

```
├── safe_signal.py          # Flask app — agent invocation, trace parsing, routing
├── templates/
│   ├── index.html          # Main dashboard — radar, category banners, resources
│   └── history.html        # Incident history page
├── static/
│   └── style.css           # Styling and animations
├── architecture.html       # Interactive system flow diagram
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## Environment Configuration

Create a `.env` file in the project root:

```env
AWS_ACCESS_KEY_ID=<YOUR_KEY>
AWS_SECRET_ACCESS_KEY=<YOUR_SECRET>

AGENT_ID=INDHHZGRD2               # Replace with your own Bedrock Agent ID
AGENT_ALIAS_ID=E4SR5MTKOO        # Replace with your production alias; use TSTALIASID only for testing

KNOWLEDGE_BASE_ID=<YOUR_KB_ID>
MODEL_ARN=arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-micro-v1:0

ALERT_EMAIL=<RESPONDER_EMAIL>
RESEND_API_KEY=<YOUR_RESEND_KEY>  # Used internally by the send_alert Lambda (not by Flask)
SECRET_KEY=<FLASK_SESSION_SECRET>
```

> **Important:** Always use `AGENT_ALIAS_ID=E4SR5MTKOO` (production alias) in deployment. The test alias (`TSTALIASID`) points to the DRAFT version and will reflect any in-progress edits in the Bedrock console immediately.

> **Email delivery:** `RESEND_API_KEY` is stored in the Lambda's environment — not in Flask. The `send_alert` function is triggered **exclusively by the Bedrock Agent** via its Action Group. Flask never calls this Lambda directly and never sends email.

---

## Running the Application

### Prerequisites

- Python 3.11+ (for local development)
- Docker + Docker Compose (for containerized deployment)
- An AWS account with Bedrock, DynamoDB, and SES configured (see [AWS Infrastructure](#aws-infrastructure))

### 1. Configure environment variables

Copy the template below into a `.env` file in the project root and fill in your values (see [Environment Configuration](#environment-configuration) for details):

```env
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AGENT_ID=...
AGENT_ALIAS_ID=...
KNOWLEDGE_BASE_ID=...
MODEL_ARN=arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-micro-v1:0
ALERT_EMAIL=...
RESEND_API_KEY=...
SECRET_KEY=...
```

### 2a. Run with Docker (recommended)

```bash
docker-compose up --build
```

### 2b. Run locally without Docker

```bash
pip install -r requirements.txt
python safe_signal.py
```

### 3. Open the app

Visit `http://localhost:5000` in your browser.  
The incident history is available at `http://localhost:5000/history`.

---

## AWS Infrastructure

> **Note:** The IDs below are example values from the reference deployment. Replace them with your own when deploying independently.

| Resource | Name / ID |
|---|---|
| Bedrock Agent | `INDHHZGRD2` |
| Production Alias | `E4SR5MTKOO` (alias-safesignal-user1) |
| Lambda — logging | `safesignal-log-incident` |
| Lambda — alerts | `safesignal-send-alert` |
| Lambda — emergency | `safesignal-activate-emergency` *(planned — future development)* |
| DynamoDB Table | `SafeSignalHistory` |
| SES Quota | 200 emails/day (sandbox), 1 msg/sec |

---

## Email Limits (SES)

The system uses Amazon SES (Sandbox mode):
- **200 emails per 24 hours**
- **1 email per second** max send rate
- Emails can only be sent to verified addresses in sandbox mode

---

## Responsible AI

SafeSignal uses retrieval-grounded generation to reduce hallucinations and improve transparency. All assessments are anchored to official guidance documents from the Israeli Ministry of Health, ERAN, and Hotline 105.

The system is designed to support human decision-making and must not be used as the sole basis for emergency, medical, legal, or psychological decisions.

---

## Author

**Developed by:** Yitzhak Maimon  
Mid-Course Project — AI-Augmented Software Engineering Training
