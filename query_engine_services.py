from llm.llm_services import OLLAMA_URL, OLLAMA_MODEL , generate_sql 
from database.database import initialize_database
import pandas as pd
import requests
import json
import re

conn = initialize_database()


def build_summary():
    df = pd.read_sql_query("SELECT * FROM tickets", conn)

    status_counts = df["status"].value_counts().to_dict()
    priority_counts = df["priority"].value_counts().to_dict()
    category_counts = df["category"].value_counts().to_dict()

    avg_response = round(df["response_time_hrs"].mean(), 2)
    avg_resolution = round(df["resolution_time_hrs"].mean(), 2)
    avg_rating = round(df["customer_rating"].mean(), 2)

    top_agents = (
        df[df["status"] == "Resolved"]
        .groupby("agent_id").size()
        .sort_values(ascending=False)
        .head(5).to_dict()
    )

    agent_ratings = df.groupby("agent_id")["customer_rating"].mean().round(2).to_dict()

    rated_agents = {k: v for k, v in agent_ratings.items() if pd.notna(v)}

    if rated_agents:
        worst_agent = min(rated_agents, key=rated_agents.get)
        best_agent = max(rated_agents, key=rated_agents.get)
    else:
        worst_agent = best_agent = None

    open_critical = int(((df["priority"] == "Critical") & (df["status"] != "Resolved")).sum())
    slow_tickets = int((df["resolution_time_hrs"] > 24).sum())

   
    cat_ratings = df.groupby("category")["customer_rating"].mean().round(2).to_dict()
    
    agent_resolved = (
        df[df["status"] == "Resolved"]
        .groupby("agent_id").size()
        .to_dict()
    )
    
    df["created_at"] = pd.to_datetime(df["created_at"])

    latest_month = df["created_at"].dt.to_period("M").max()

    monthly_agent_resolved = (
        df[
            (df["status"] == "Resolved")
            & (df["created_at"].dt.to_period("M") == latest_month)
        ]
        .groupby("agent_id")
        .size()
        .sort_values(ascending=False)
        .to_dict()
    )
    

    summary = f"""Total tickets: {len(df)}
    Status: {status_counts}
    Priority: {priority_counts}
    Category: {category_counts}
    Avg response time: {avg_response} hrs
    Avg resolution time: {avg_resolution} hrs
    Avg customer rating: {avg_rating}/5
    Category wise avg rating: {cat_ratings}
    Top 5 agents by resolved tickets: {top_agents}
    All agent resolved counts: {agent_resolved}
    All agent ratings: {agent_ratings}
    Monthly resolved counts: {monthly_agent_resolved}
    Best rated agent: {best_agent} ({agent_ratings[best_agent]}/5)
    Worst rated agent: {worst_agent} ({agent_ratings[worst_agent]}/5)
    Open or escalated Critical tickets: {open_critical}
    Tickets with resolution time over 24 hrs: {slow_tickets}"""

    return summary

def execute_sql_query(question: str):

    sql = generate_sql(question)


    if not sql.lower().startswith("select"):
        raise Exception("Non-SELECT query generated")

    df = pd.read_sql_query(sql, conn)

    if len(df) == 0:
        raise Exception("No rows returned")

    return {
    "question": question,
    "generated_sql": sql,
    "rows": df.fillna("").to_dict(orient="records"),
    "confidence": "high"
}
        
def execute_query(question: str):
    
    try:
        return execute_sql_query(question)

    except Exception as e:

        print("\nSQL PATH FAILED")
        print(str(e))
    
    q = question.lower()

    if (
        "critical" in q
        and "12" in q
        and ("not resolved" in q or "unresolved" in q)
    ):
        df = pd.read_sql_query("SELECT * FROM tickets", conn)

        result = df[
            (df["priority"] == "Critical")
            &
            (
                (df["status"] != "Resolved")
                |
                (df["resolution_time_hrs"] > 12)
            )
        ]

        tickets = (
            result[
                [
                    "ticket_id",
                    "status",
                    "resolution_time_hrs",
                    "agent_id"
                ]
            ]
            .fillna("")
            .to_dict(orient="records")
        )

        return {
    "question": question,
    "answer": f"Found {len(tickets)} matching tickets.",
    "tickets": tickets,
    "confidence": "high"
    }
        
    summary = build_summary()

    prompt = f"""You are a data analyst for a support team.

    Here is the full dataset summary:
        {summary}

        Important: This dataset is from 2024. Do not filter by current date or week. Analyse all available data.

        Answer this question using only the data above.

        If the question asks to SHOW tickets, return the matching ticket IDs and relevant details.
            {question}

            Reply ONLY with this JSON (no markdown, no extra text):
                {{"answer": "...", "key_numbers": [...], "confidence": "high/medium/low"}}"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0}
        },
        timeout=180
    )
    data = response.json()

    if "response" not in data:
        return {
    "answer": data.get("error", "LLM error"),
    "key_numbers": [],
    "confidence": "low"
    }

    raw = data["response"].strip()
    raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()

    try:
        result = json.loads(raw)
    except Exception:
        result = {"answer": raw, "key_numbers": [], "confidence": "medium"}

    result["question"] = question
    return result