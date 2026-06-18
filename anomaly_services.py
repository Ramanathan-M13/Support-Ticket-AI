import pandas as pd
import numpy as np

from database.database import initialize_database

conn = initialize_database()


def clean_for_json(df: pd.DataFrame) -> list[dict]:

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.astype(object).where(pd.notnull(df), None)
    return df.to_dict(orient="records")


def detect_anomalies():
    query = "SELECT * FROM tickets"
    df = pd.read_sql_query(query, conn)

    slow_resolution = df[df["resolution_time_hrs"] > 24]

    unresolved_high_priority = df[
        (df["priority"].isin(["High", "Critical"]))
        & (df["status"].isin(["Open", "Escalated"]))
    ]

    agent_ratings = (
        df.groupby("agent_id")["customer_rating"]
        .mean()
        .reset_index()
    )

    avg_rating = agent_ratings["customer_rating"].mean()

    low_rated_agents = agent_ratings[
        agent_ratings["customer_rating"] < avg_rating
    ]

    return {
"summary": {
    "slow_resolution_tickets": len(slow_resolution),
    "unresolved_high_priority_tickets": len(unresolved_high_priority),
    "low_rated_agents": len(low_rated_agents),
},
"slow_resolution_tickets": clean_for_json(slow_resolution),
"unresolved_high_priority_tickets": clean_for_json(unresolved_high_priority),
"low_rated_agents": clean_for_json(low_rated_agents),
}