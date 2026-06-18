import requests
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b"

def generate_sql(question: str):
    
    prompt = f"""You are an expert SQLite query generator.


You are an expert SQLite query generator.

Table: tickets

Columns:
    ticket_id
    created_at
    category
    priority
    status
    response_time_hrs
    resolution_time_hrs
    agent_id
    customer_rating
    issue_summary

    Valid status values:
        Open
        Resolved
        Escalated

    Valid priority values:
        Low
        Medium
        High
        Critical

    Valid categories:
        Billing
        Technical
        General

        Rules:
            - Generate ONLY SQLite SELECT queries
            - Output ONLY ONE query
            - No explanations
            - No markdown
            - No comments
            - Use exact column names
            - Use exact enum values

        RULES:

            1. Generate ONLY SQLite SELECT queries.
            2. Never generate UPDATE.
            3. Never generate DELETE.
            4. Never generate DROP.
            5. Never generate INSERT.
            6. Never generate ALTER.
            7. Never generate explanations.
            8. Never generate markdown.
            9. Return SQL only.
            10. Use exact column names.
            11. Use exact enum values as provided above.
            12. When counting resolved tickets, filter using:
                status='Resolved'
            13. When counting unresolved tickets, use:
                status IN ('Open','Escalated')
            14. Ignore NULL customer ratings when calculating averages.
            
        IMPORTANT BUSINESS RULES:

        - This dataset contains historical ticket data.
        - Never use date('now').
        - Never use current system date.
        - For questions containing "this month", use the latest month available in the dataset.
        - Unresolved tickets = status IN ('Open','Escalated')
        - Resolved tickets = status='Resolved'
        - Ignore NULL customer_rating values when calculating averages.

        USER Question:
            {question}
    """

    response = requests.post(
    OLLAMA_URL,
    json={
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0
        }
    },
    timeout=180
)
    if response.status_code != 200:

        print("\nSTATUS CODE:")
        print(response.status_code)

        print("\nOLLAMA RESPONSE:")
        print(response.text)

        raise Exception(
        f"Ollama returned {response.status_code}"
        )
    
    sql = response.json()["response"].strip()

    sql = re.sub(r"```sql|```", "", sql).strip()

    matches = re.findall(
        r"SELECT[\s\S]*?(?:;|$)",
        sql,
        re.IGNORECASE
    )

    if matches:
        sql = matches[-1].strip()
           
    return sql