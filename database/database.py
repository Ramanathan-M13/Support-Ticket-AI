import sqlite3
import pandas as pd


def initialize_database():
    try:
        df = pd.read_csv(
            "support_tickets.csv",
            parse_dates=["created_at"]
        )


        conn = sqlite3.connect(
            "tickets.db",
            check_same_thread=False
        )

        df.to_sql(
            "tickets",
            conn,
            if_exists="replace",
            index=False
        )

        return conn

    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise