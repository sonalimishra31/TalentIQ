import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Admin Dashboard", layout="wide")

st.title("🛠 TalentIQ AI – Admin Dashboard")

conn = sqlite3.connect("users.db")

# -------- METRICS --------
users = pd.read_sql("SELECT * FROM users", conn)
history = pd.read_sql("SELECT * FROM analysis_history", conn)

col1, col2 = st.columns(2)
col1.metric("👥 Total Users", len(users))
col2.metric("📄 Total Analyses", len(history))

st.divider()

# -------- PIE CHART --------
st.subheader("🥧 Job Role Distribution")
if not history.empty:
    role_counts = history["best_role"].value_counts()
    fig1, ax1 = plt.subplots()
    ax1.pie(role_counts, labels=role_counts.index, autopct="%1.1f%%")
    st.pyplot(fig1)

st.divider()

# -------- LINE TREND --------
st.subheader("📈 Resume Analysis Trend")
if not history.empty:
    history["timestamp"] = pd.to_datetime(history["timestamp"])
    trend = history.groupby(history["timestamp"].dt.date).size()
    st.line_chart(trend)

st.divider()

# -------- TABLE --------
st.subheader("🕒 Full Analysis History")
st.dataframe(history, use_container_width=True)

conn.close()
