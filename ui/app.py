import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("🎫 Support Ticket AI")

question = st.text_input(
    "Ask a question about support tickets"
)

if st.button("Ask"):

    response = requests.post(
        f"{API_URL}/query",
        json={"question": question}
    )

    if response.status_code == 200:
        st.json(response.json())
    else:
        st.error("Failed to get response")

st.divider()

if st.button("Show Anomalies"):

    response = requests.get(
        f"{API_URL}/anomalies"
    )

    if response.status_code == 200:
        st.json(response.json())
        