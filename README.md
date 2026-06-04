# SafeSignal: Digital Resilience Assistant for Youth 🛡️🤖

SafeSignal is an AI-powered web application designed to identify and assess potential signs of emotional distress, cyberbullying, social exclusion, and suicidal ideation in online content such as posts, comments, and chat messages.

Built as an end-to-end AI-augmented software solution, SafeSignal combines Retrieval-Augmented Generation (RAG) with official guidance from public support organizations to generate structured, evidence-grounded risk assessment reports. The system is intended to assist educators, social workers, support teams, and community organizations in identifying individuals who may require attention or intervention.

> **Disclaimer:** SafeSignal is designed as a decision-support system and does not provide medical diagnoses or replace professional mental health assessment or intervention.

---

## 🚀 Key Features

### Advanced RAG Architecture
Connects seamlessly with Amazon Bedrock Knowledge Bases and vector-based retrieval systems to generate grounded assessments based on official guidance and trusted source documents.

### HQ Operational Dashboard
Features a cyber-inspired command center interface with responsive layouts, real-time monitoring visuals, animated system indicators, and streamlined report presentation.

### Specialized Safety Guardrails
Implements domain-specific filtering and validation mechanisms to keep the model focused on distress detection scenarios while reducing irrelevant responses and hallucinations.

### Automated Threat Flagging (`[ALERT: TRUE]`)
Highlights potentially critical situations when strong indicators of self-harm, suicidal ideation, severe distress, or cyberbullying are detected within the analyzed content.

### Source Attribution & Fallback Logic
Extracts supporting citations from retrieved knowledge base documents and presents them alongside generated assessments. Includes fallback guidance when retrieval results are unavailable or incomplete.

### Containerized Deployment
Fully Dockerized architecture enabling simple deployment, portability, and reproducible execution across environments.

---

## 🛠️ Architecture & Technologies


| Layer            | Technology              |
| ---------------- | ----------------------- |
| Backend          | Python 3.11, Flask      |
| Frontend         | HTML5, CSS3, Jinja2     |
| AI Engine        | Amazon Bedrock          |
| RAG Service      | Bedrock Knowledge Bases |
| Foundation Model | amazon.nova-micro-v1:0  |
| Cloud SDK        | boto3                   |
| Containerization | Docker, Docker Compose  |

---

## 🏗️ System Workflow

1. User submits online content (post, comment, message, or chat transcript).
2. The system performs preliminary safety checks and risk indicator analysis.
3. Relevant guidance is retrieved from the Amazon Bedrock Knowledge Base.
4. The LLM generates a structured risk assessment report using retrieved evidence.
5. Risk level is classified and emergency indicators are evaluated.
6. Supporting sources and recommended actions are presented to the operator.

---

## 📂 Project Structure

```text
├── safe_signal.py         # Main Flask application and route handling
├── templates/
│   └── index.html         # Dashboard interface and report rendering
├── static/
│   └── style.css          # Styling, animations, and responsive layouts
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container configuration
└── docker-compose.yml     # Local deployment orchestration
```

---

## ⚙️ Prerequisites

Before running the application, ensure the following components are available:
* Docker
* Docker Compose
* AWS Account with Amazon Bedrock access
* Configured AWS credentials
* Active Amazon Bedrock Knowledge Base containing approved guidance documents

---

## 🔧 Environment Configuration

Create a `.env` file in the project root:

```env
AWS_ACCESS_KEY_ID=<YOUR_AWS_ACCESS_KEY>
AWS_SECRET_ACCESS_KEY=<YOUR_AWS_SECRET_KEY>

KNOWLEDGE_BASE_ID=GGJ7PMZUMP

MODEL_ARN=arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-micro-v1:0
```

---

## 🐳 Running the Application

Build and launch the entire stack:

```bash
docker-compose up --build
```

Once started, the application will be available at:
```text
http://localhost:5000
```

---

## 📊 Assessment Protocol

For every submitted text, SafeSignal generates a structured report that may include:

### Risk Classification
* Critical
* High
* Medium
* Low

### Emergency Indicator
```text
[ALERT: TRUE]
```
Displayed when strong indicators of immediate risk are identified.

### Evidence-Based Explanation
Provides a concise justification supported by retrieved guidance and source references.

### Support Recommendations
Presents appropriate referral information and recommended next steps based on the identified category of concern.

---

## 🔒 Responsible AI Considerations

SafeSignal follows a retrieval-grounded approach to reduce hallucinations and improve transparency. The system relies on curated guidance documents and provides source attribution whenever possible.

The application is intended to support human decision-making and should not be used as the sole basis for emergency, medical, legal, or psychological decisions.

---

## 👨‍💻 Author

**Developed by:** Yitzhak Maimon

Mid-Course Project – AI-Augmented Software Engineering Training
