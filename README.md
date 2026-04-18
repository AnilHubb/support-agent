# Customer Support Chatbot

Full-stack order-support chatbot powered by **FastAPI + LangChain + Mistral AI** (backend)
and **React + Vite** (frontend).

---

## Project structure

```
AL/
├── backend/
│   ├── main.py          ← FastAPI app (routes: /login, /chat, /session)
│   ├── agent.py         ← LangChain agent with Mistral AI + order tools
│   ├── database.py      ← SQLite setup + seed data
│   ├── models.py        ← Pydantic request/response models
│   ├── auth.py          ← Password hashing + session management
│   ├── requirements.txt
│   └── .env.example     ← Copy → .env, add MISTRAL_API_KEY
└── ui/
    ├── index.html
    ├── vite.config.js
    ├── package.json
    └── src/
        ├── App.jsx
        ├── api.js
        ├── styles.css
        ├── index.jsx
        └── components/
            ├── Login.jsx
            └── Chat.jsx
```

---

## Prerequisites

| Tool    | Version  |
|---------|----------|
| Python  | 3.11+    |
| Node.js | 18+      |
| npm     | 9+       |

---

## 1 – Get a Mistral API key

1. Sign up at <https://console.mistral.ai/>
2. Create an API key in **API Keys** section.

---

## 2 – Backend setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and set: MISTRAL_API_KEY=your_key_here

# Start the server
uvicorn main:app --reload --port 8000
```

API is now running at **http://localhost:8000**  
Interactive docs: **http://localhost:8000/docs**

---

## 3 – Frontend setup

```bash
cd ui

npm install
npm run dev
```

App is now running at **http://localhost:5173**

---

## Demo credentials

| Username | Password   | Orders              |
|----------|-----------|---------------------|
| alice    | alice123  | ORD-001, ORD-002, ORD-006, ORD-010 |
| bob      | bob123    | ORD-003, ORD-004, ORD-007          |
| charlie  | charlie123| ORD-005, ORD-008, ORD-009          |

---

## Sample order statuses

| Order   | Product             | Status           |
|---------|---------------------|------------------|
| ORD-001 | Wireless Headphones | shipped          |
| ORD-002 | Smart Watch         | delivered        |
| ORD-003 | Laptop Stand        | out_for_delivery |
| ORD-004 | Gaming Mouse        | delayed          |
| ORD-005 | Mechanical Keyboard | shipped          |
| ORD-006 | USB Hub             | processing       |
| ORD-007 | Monitor             | delivered        |
| ORD-008 | Office Chair        | out_for_delivery |
| ORD-009 | Standing Desk       | delayed          |
| ORD-010 | Phone Case          | cancelled        |

---

## API endpoints

| Method | Path                    | Description              |
|--------|-------------------------|--------------------------|
| POST   | /login                  | Authenticate user        |
| POST   | /chat                   | Send message to AI agent |
| GET    | /session/{session_id}   | Retrieve chat history    |
| GET    | /health                 | Health check             |

---

## Example chat queries

- *"Show all my orders"*
- *"Where is my order ORD-001?"*
- *"When will ORD-005 arrive?"*
- *"My order ORD-004 is delayed, what should I do?"*
- *"Has ORD-002 been delivered?"*
