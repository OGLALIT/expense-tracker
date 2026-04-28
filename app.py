import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# ---------- LOAD DATA ----------
try:
    df = pd.read_csv("expenses.csv")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
except:
    df = pd.DataFrame(columns=["Date","Category","Amount","Type","Description"])

# ---------- SIDEBAR ----------
st.sidebar.title("💰 Expense Tracker")
menu = st.sidebar.radio("", ["Dashboard", "Add Transaction"])

# ---------- ADD TRANSACTION ----------
if menu == "Add Transaction":
    st.title("➕ Add Transaction")

    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    category = st.selectbox("Category", ["Food","Shopping","Transport","Bills","Entertainment","Salary","Other"])
    t_type = st.selectbox("Type", ["Expense","Income"])
    desc = st.text_input("Description")
    date = st.date_input("Date")

    if st.button("Add"):
        new = pd.DataFrame({
            "Date":[pd.to_datetime(date)],
            "Category":[category],
            "Amount":[amount],
            "Type":[t_type],
            "Description":[desc]
        })

        df = pd.concat([df, new], ignore_index=True)
        df.to_csv("expenses.csv", index=False)
        st.success("✅ Transaction Added!")

# ---------- DASHBOARD ----------
if menu == "Dashboard":

    st.title("📊 Dashboard")

    if df.empty:
        st.info("Add transactions first")
        st.stop()

    # ---------- CLEAN DATA ----------
    df = df.dropna(subset=["Date"])
    df = df.sort_values("Date")
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    # ---------- CALCULATIONS ----------
    income = df[df["Type"]=="Income"]["Amount"].sum()
    expense = df[df["Type"]=="Expense"]["Amount"].sum()
    savings = income - expense

    # ---------- TOP CARDS ----------
    c1,c2,c3,c4 = st.columns(4)

    c1.metric("Transactions", len(df))
    c2.metric("Income", f"₹{income:.2f}")
    c3.metric("Expense", f"₹{expense:.2f}")
    c4.metric("Savings", f"₹{savings:.2f}")

    # ---------- SMART MESSAGE ----------
    if savings > 0:
        st.success(f"💸 You're saving ₹{savings:.0f}")
    else:
        st.error("⚠️ You're overspending!")

    st.markdown("---")

    # ---------- GROUP DATA (IMPORTANT FIX) ----------
    daily = df.groupby(["Date","Type"])["Amount"].sum().reset_index()

    income_df = daily[daily["Type"]=="Income"]
    expense_df = daily[daily["Type"]=="Expense"]

    # ---------- BALANCE ----------
    df["Signed"] = df.apply(
        lambda x: x["Amount"] if x["Type"]=="Income" else -x["Amount"], axis=1
    )

    balance = df.groupby("Date")["Signed"].sum().cumsum().reset_index()

    # ---------- CHARTS ----------
    col1, col2, col3 = st.columns(3)

    # Balance Chart (FIXED)
    fig1 = px.line(
        balance,
        x="Date",
        y="Signed",
        title="Account Balance Over Time",
        markers=True
    )
    col1.plotly_chart(fig1, use_container_width=True)

    # Category Chart (FIXED)
    exp_cat = df[df["Type"]=="Expense"].groupby("Category")["Amount"].sum().reset_index()

    if not exp_cat.empty:
        fig2 = px.pie(
            exp_cat,
            names="Category",
            values="Amount",
            title="Expenses by Category"
        )
        col2.plotly_chart(fig2, use_container_width=True)
    else:
        col2.info("No expense data")

    # Expense Trend (FIXED)
    if not expense_df.empty:
        fig3 = px.line(
            expense_df,
            x="Date",
            y="Amount",
            title="Daily Expenses",
            markers=True
        )
        col3.plotly_chart(fig3, use_container_width=True)
    else:
        col3.info("No expense data")

    st.markdown("---")

    # ---------- BUDGET ----------
    st.subheader("💳 Budget")

    budget = st.number_input("Monthly Budget", value=5000.0)

    used = (expense / budget * 100) if budget > 0 else 0

    st.progress(min(int(used),100))
    st.write(f"{used:.1f}% used")

    if used < 80:
        st.success("Under control")
    elif used < 100:
        st.warning("Near limit")
    else:
        st.error("Budget exceeded")

    # ---------- EXPORT ----------
    st.subheader("📤 Export Data")

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "data.csv", "text/csv")

    # ---------- TABLE ----------
    st.subheader("📋 Recent Transactions")
    st.dataframe(df.sort_values("Date", ascending=False), use_container_width=True)
