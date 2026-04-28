
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# Load data
try:
    df = pd.read_csv("expenses.csv")
except:
    df = pd.DataFrame(columns=["Date","Category","Amount","Type","Description"])

st.title("💰 Expense Tracker Dashboard")

# Sidebar
st.sidebar.title("📊 Expense Tracker")
st.sidebar.header("Add Expense")

amount = st.sidebar.number_input("Amount", min_value=0.0)
category = st.sidebar.selectbox("Category", ["Food","Travel","Shopping","Bills","Entertainment"])
desc = st.sidebar.text_input("Description")
date = st.sidebar.date_input("Date")

if st.sidebar.button("Add Expense"):
    new_data = pd.DataFrame([[date,category,amount,"Expense",desc]],
                            columns=df.columns)
    df = pd.concat([df,new_data], ignore_index=True)
    df.to_csv("expenses.csv", index=False)
    st.sidebar.success("Added!")

# KPIs
total = len(df)
income = df[df["Type"]=="Income"]["Amount"].sum()
expense = df[df["Type"]=="Expense"]["Amount"].sum()
net = income - expense

col1,col2,col3,col4 = st.columns(4)

col1.metric("Total Transactions", total)
col2.metric("Total Income", f"₹{income}")
col3.metric("Total Expenses", f"₹{expense}")
col4.metric("Net Savings", f"₹{net}")

# Charts
df["Date"] = pd.to_datetime(df["Date"])

colA, colB = st.columns(2)

with colA:
    st.subheader("📈 Expenses Over Time")
    daily = df.groupby("Date")["Amount"].sum().reset_index()
    fig = px.line(daily, x="Date", y="Amount", markers=True)
    st.plotly_chart(fig, use_container_width=True)

with colB:
    st.subheader("🥧 Expenses by Category")
    cat = df.groupby("Category")["Amount"].sum().reset_index()
    fig2 = px.pie(cat, names="Category", values="Amount", hole=0.4)
    st.plotly_chart(fig2, use_container_width=True)

# Budget System
budget = st.sidebar.number_input("Set Monthly Budget", value=5000)

st.subheader("💸 Budget Status")
spent_percent = (expense / budget) * 100 if budget > 0 else 0

st.progress(min(spent_percent/100,1.0))
st.write(f"Spent: ₹{expense} / ₹{budget} ({spent_percent:.1f}%)")

# Budget Alert
if expense > budget:
    st.error("🚨 Budget Exceeded!")
else:
    st.success("✅ You are within budget")

# Category Suggestion
if not df.empty:
    top_cat = df.groupby("Category")["Amount"].sum().idxmax()
    st.info(f"💡 You are spending most on: **{top_cat}**")
else:
    st.info("No data yet")

# Recent Transactions
st.subheader("📋 Recent Transactions")
st.dataframe(df.tail(5))
