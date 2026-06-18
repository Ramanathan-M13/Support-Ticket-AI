# Support Ticket AI System

A FastAPI-based AI application that enables users to query support ticket data using plain English. The system uses a locally hosted Llama 3.1 model through Ollama to convert natural language questions into SQL queries, execute them against a SQLite database, and return structured answers. It also provides anomaly detection capabilities for identifying operational issues within support ticket workflows.

---

# Setup Instructions

## 1. Install Ollama

Download and install Ollama from:

https://ollama.com

Pull the required model:

```bash
ollama pull llama3.1:8b
```

---

## 2. Start Ollama

Run the Ollama server:

```bash
ollama serve
```

Verify the model is available:

```bash
ollama list
```

Expected output:

```text
llama3.1:8b
```

---

## 3. Install Python Dependencies

Install all required packages:

```bash
pip install -r requirements.txt
```

---

## 4. Start the Application

Run the FastAPI server:

```bash
uvicorn main:app --reload
```

Application will be available at:

```text
http://localhost:8000
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

---

# Architecture Overview

The application follows a Natural Language → SQL → Database Query workflow.

```text
                    User
                      │
                      ▼
               FastAPI Endpoint
                      │
                      ▼
              Query Engine Service
                      │
                      ▼
          Llama 3.1 (Ollama Local)
                      │
          Generates SQL Query
                      │
                      ▼
              SQLite Database
                      │
              Executes Query
                      │
                      ▼
               Query Results
                      │
                      ▼
                JSON Response
```

For anomaly detection:

```text
User
 │
 ▼
/anomalies
 │
 ▼
Anomaly Service
 │
 ├── Slow Resolution Detection
 ├── SLA Violation Detection
 ├── Critical Ticket Analysis
 └── Resolution Time Outlier Detection
 │
 ▼
JSON Response
```

---

# System Components

## FastAPI Layer

Provides REST API endpoints for:

* Ticket analytics
* Natural language querying
* Anomaly reporting
* Health monitoring

---

## Database Layer

The ticket dataset is loaded from CSV and stored in a SQLite database.

Responsibilities:

* Data persistence
* Query execution
* Aggregations
* Filtering
* Reporting

---

## LLM Service

Uses Llama 3.1 8B through Ollama.

Responsibilities:

* Interpret user questions
* Generate SQL queries
* Understand business language
* Support flexible querying

Example:

User Question:

```text
Which agent handled ticket TKT-238?
```

Generated SQL:

```sql
SELECT *
FROM tickets
WHERE ticket_id='TKT-238';
```

---

## Query Engine Service

Acts as the bridge between the LLM and the database.

Workflow:

1. Receive question
2. Generate SQL using Llama 3.1
3. Validate SQL
4. Execute SQL against SQLite
5. Return structured JSON response

---

## Anomaly Detection Service

Performs rule-based operational analysis.

Detects:

* Excessive resolution times
* Critical unresolved tickets
* SLA violations
* Resolution-time outliers

---

# Data Flow

```text
support_tickets.csv
          │
          ▼
    SQLite Database
          │
          ▼
    User Question
          │
          ▼
       Llama 3.1
          │
          ▼
     Generated SQL
          │
          ▼
   SQLite Execution
          │
          ▼
      Query Result
          │
          ▼
      JSON Output
```

---

# Model and Tools Used

## Large Language Model

### Llama 3.1 8B

* Hosted locally using Ollama
* No external API dependency
* Offline execution
* Natural language understanding
* SQL generation

---

## Frameworks and Libraries

### FastAPI

Used to build REST APIs.

### SQLite

Stores support ticket information and executes SQL queries.

### Pandas

Used for:

* CSV ingestion
* Data preprocessing
* Aggregations
* Statistical analysis
* Anomaly detection

### Ollama

Hosts and serves the Llama 3.1 model locally.

### Requests

Used for communication with the Ollama API.

---

# API Endpoints

| Method | Endpoint   | Description                      |
| ------ | ---------- | -------------------------------- |
| GET    | /health    | Application health check         |
| POST   | /query     | Natural language ticket querying |
| GET    | /anomalies | Generate anomaly report          |

---

# Example Queries

## Query 1

Input

```json
{
  "question": "How many tickets are currently open?"
}
```

Output

```json
{
  "question": "How many tickets are currently open?",
  "generated_sql": "SELECT COUNT(*) AS open_tickets FROM tickets WHERE status='Open';",
  "rows": [
    {
      "open_tickets": 111
    }
  ],
  "confidence": "high"
}
```

---

## Query 2

Input

```json
{
  "question": "Which agent resolved the most tickets?"
}
```

Output

```json
{
  "question": "Which agent resolved the most tickets?",
  "generated_sql": "SELECT agent_id, COUNT(*) AS resolved_count FROM tickets WHERE status='Resolved' GROUP BY agent_id ORDER BY resolved_count DESC LIMIT 1;",
  "rows": [
    {
      "agent_id": "AGT-09",
      "resolved_count": 37
    }
  ],
  "confidence": "high"
}
```

---

## Query 3

Input

```json
{
  "question": "Which agent handled ticket TKT-238?"
}
```

Output

```json
{
  "question": "Which agent handled ticket TKT-238?",
  "generated_sql": "SELECT * FROM tickets WHERE ticket_id='TKT-238';",
  "rows": [
    {
      "ticket_id": "TKT-238",
      "agent_id": "AGT-12",
      "status": "Resolved"
    }
  ],
  "confidence": "high"
}
```

---

## Query 4

Input

```json
{
  "question": "What is the average customer rating for Technical category tickets?"
}
```

Output

```json
{
  "question": "What is the average customer rating for Technical category tickets?",
  "generated_sql": "SELECT ROUND(AVG(customer_rating),2) AS avg_rating FROM tickets WHERE category='Technical';",
  "rows": [
    {
      "avg_rating": 3.74
    }
  ],
  "confidence": "high"
}
```

---

## Query 5

Input

```json
{
  "question": "Show me all Critical tickets not resolved within 12 hours."
}
```

Output

```json
{
  "question": "Show me all Critical tickets not resolved within 12 hours.",
  "tickets": [
    {
      "ticket_id": "TKT-060",
      "status": "Escalated",
      "agent_id": "AGT-06"
    }
  ],
  "confidence": "high"
}
```

---

# Example Anomaly Output

Input

```text
Are there any anomalies in resolution times?
```

Output

```json
{
  "answer": "Yes, anomalies were detected.",
  "key_numbers": [
    {
      "ticket_id": "TKT-238",
      "resolution_time_hrs": 53.4
    },
    {
      "ticket_id": "TKT-255",
      "resolution_time_hrs": 66.6
    },
    {
      "ticket_id": "TKT-446",
      "resolution_time_hrs": 60.6
    }
  ],
  "confidence": "high"
}
```

---

# Design Decisions

1. SQLite was chosen because it is lightweight and sufficient for the ticket dataset size.

2. Llama 3.1 was selected because it can run locally without requiring cloud APIs or API keys.

3. Natural language questions are translated into SQL rather than querying raw data directly, providing flexibility and scalability.

4. Read-only SQL generation is enforced to prevent database modifications.

5. Anomaly detection is implemented separately from the LLM to ensure deterministic and reliable outputs.

---

# Known Limitations

1. Ollama must be running before the FastAPI server starts.

2. First model response may be slower due to model loading.

3. SQL generation quality depends on the Llama 3.1 model.

4. Very large datasets may increase response times.

5. The current anomaly detection module is rule-based and does not use machine learning models.

6. Historical datasets may require special handling for relative date queries such as "this month" or "this week".

7. The system currently supports a single ticket dataset schema.

8. Only read-only SQL queries are allowed for security purposes.

---

# Future Improvements

* Retrieval-Augmented Generation (RAG)
* Multi-table database support
* Authentication and role-based access
* Interactive dashboards
* Machine-learning-based anomaly detection
* Query caching and optimization
* Advanced reporting and visualization
