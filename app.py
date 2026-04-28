import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(layout="wide")

# Load data
try:
    df = pd.read_csv("expenses.csv")
except:
    df = pd.DataFrame(columns=["Date","Category","Amount","Type","Description"])

st.title("💰 Expense Tracker Dashboard")

# ================= SIDEBAR =================
st.sidebar.title("📊 Expense Tracker")

st.sidebar.header("Add Transaction")

amount = st.sidebar.number_input("Amount", min_value=0.0)

category = st.sidebar.selectbox(
    "Category",
    ["Food","Travel","Shopping","Bills","Entertainment","Salary","Other"]
)

type_option = st.sidebar.selectbox("Type", ["Expense","Income"])

desc = st.sidebar.text_input("Description")

date = st.sidebar.date_input("Date")

if st.sidebar.button("Add Transaction"):
    new_data = pd.DataFrame(
        [[date, category, amount, type_option, desc]],
        columns=df.columns
    )
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv("expenses.csv", index=False)
    st.sidebar.success("Added successfully!")

# ================= KPI =================
total = len(df)
income = df[df["Type"]=="Income"]["Amount"].sum()
expense = df[df["Type"]=="Expense"]["Amount"].sum()
net = income - expense

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Transactions", total)
col2.metric("Total Income", f"₹{income:.2f}")
col3.metric("Total Expenses", f"₹{expense:.2f}")
col4.metric("Net Savings", f"₹{net:.2f}")

# ================= CHARTS =================
if not df.empty:
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

# ================= BUDGET =================
st.sidebar.header("Set Monthly Budget")
budget = st.sidebar.number_input("Budget", value=5000.0)

st.subheader("💸 Budget Status")

spent_percent = (expense / budget * 100) if budget > 0 else 0

st.progress(min(spent_percent/100, 1.0))
st.write(f"Spent: ₹{expense:.2f} / ₹{budget:.2f} ({spent_percent:.1f}%)")

# Budget Alert
if expense > budget:
    st.error("🚨 Budget Exceeded!")
else:
    st.success("✅ You are within budget")

# ================= CATEGORY SUGGESTION =================
if not df.empty:
    top_cat = df.groupby("Category")["Amount"].sum().idxmax()
    st.info(f"💡 You are spending most on: **{top_cat}**")

# ================= RECENT TRANSACTIONS =================
st.subheader("📋 Recent Transactions")
st.dataframe(df.tail(5), use_container_width=True)
