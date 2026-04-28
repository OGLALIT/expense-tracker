import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Expense Tracker", layout="wide")

# ---------- LOAD DATA ----------
try:
    df = pd.read_csv("expenses.csv")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
except:
    df = pd.DataFrame(columns=["Date","Category","Amount","Type","Description"])

# ---------- SIDEBAR ----------
st.sidebar.title("📊 Expense Tracker")

page = st.sidebar.radio("Navigation", ["Dashboard", "Add Transaction"])

st.sidebar.markdown("## 🔎 Filter")

selected_cat = st.sidebar.multiselect(
    "Category",
    options=df["Category"].unique() if not df.empty else []
)

selected_type = st.sidebar.multiselect(
    "Type",
    options=["Income", "Expense"]
)

# ---------- FILTER LOGIC ----------
filtered_df = df.copy()

if selected_cat:
    filtered_df = filtered_df[filtered_df["Category"].isin(selected_cat)]

if selected_type:
    filtered_df = filtered_df[filtered_df["Type"].isin(selected_type)]

# ---------- ADD TRANSACTION ----------
if page == "Add Transaction":
    st.title("➕ Add Transaction")

    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    category = st.selectbox("Category", ["Food","Shopping","Travel","Salary","Other"])
    t_type = st.selectbox("Type", ["Expense","Income"])
    desc = st.text_input("Description")
    date = st.date_input("Date")

    if st.button("Add Transaction"):
        new_data = pd.DataFrame({
            "Date":[date],
            "Category":[category],
            "Amount":[amount],
            "Type":[t_type],
            "Description":[desc]
        })

        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv("expenses.csv", index=False)

        st.success("✅ Transaction Added!")

# ---------- DASHBOARD ----------
if page == "Dashboard":

    st.title("💰 Expense Tracker Dashboard")

    if df.empty:
        st.info("No data yet — add your first transaction!")
        st.stop()

    # ---------- CALCULATIONS ----------
    income = df[df["Type"] == "Income"]["Amount"].sum()
    expense = df[df["Type"] == "Expense"]["Amount"].sum()
    savings = income - expense

    # ---------- METRICS ----------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Transactions", len(df))
    col2.metric("Income", f"₹{income:.2f}")
    col3.metric("Expense", f"₹{expense:.2f}")
    col4.metric("Savings", f"₹{savings:.2f}")

    # ---------- SMART MESSAGE ----------
    if savings > 0:
        st.success(f"💸 Great! You're saving ₹{savings:.0f}")
    else:
        st.error("⚠️ You're overspending!")

    # ---------- QUICK SUMMARY ----------
    st.subheader("⚡ Quick Summary")
    c1, c2, c3 = st.columns(3)

    c1.info(f"💰 Total Income: ₹{income:.0f}")
    c2.warning(f"💸 Total Expense: ₹{expense:.0f}")
    c3.success(f"🏦 Savings: ₹{savings:.0f}")

    # ---------- USE FILTERED DATA FOR CHARTS ----------
    if filtered_df.empty:
        st.warning("No data after applying filters")
    else:
        # ---------- TREND ----------
        st.subheader("📈 Trend")

        trend_df = filtered_df.copy()
        trend_df["Date"] = pd.to_datetime(trend_df["Date"], errors="coerce")

        fig1 = px.line(
            trend_df,
            x="Date",
            y="Amount",
            color="Type",
            title="Income vs Expense Trend"
        )
        st.plotly_chart(fig1, use_container_width=True)

        # ---------- CATEGORY PIE ----------
        st.subheader("🍕 Category Breakdown")

        exp_df = filtered_df[filtered_df["Type"] == "Expense"]

        if not exp_df.empty:
            fig2 = px.pie(
                exp_df,
                names="Category",
                values="Amount",
                title="Expense Distribution"
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No expense data for selected filter")

    # ---------- MONTHLY INSIGHT ----------
    st.subheader("📅 Monthly Insight")

    monthly = df.copy()
    monthly["Month"] = monthly["Date"].dt.to_period("M").astype(str)

    monthly_summary = monthly.groupby(["Month","Type"])["Amount"].sum().reset_index()

    fig3 = px.bar(
        monthly_summary,
        x="Month",
        y="Amount",
        color="Type",
        barmode="group",
        title="Monthly Income vs Expense"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ---------- BUDGET ----------
    st.subheader("💳 Budget")

    budget = st.number_input("Monthly Budget", value=5000.0)

    used_percent = (expense / budget * 100) if budget > 0 else 0

    st.progress(min(int(used_percent),100))

    st.write(f"{used_percent:.1f}% used")

    if used_percent < 80:
        st.success("✅ Under control")
    elif used_percent < 100:
        st.warning("⚠️ Near limit")
    else:
        st.error("🚨 Budget exceeded!")

    # ---------- EXPORT ----------
    st.subheader("📤 Export Data")

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "data.csv", "text/csv")

    # ---------- TABLE ----------
    st.subheader("📋 Recent Transactions")
    st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)
