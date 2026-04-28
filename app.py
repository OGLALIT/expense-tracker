import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Expense Tracker", layout="wide")

# ---------- LOAD DATA ----------
try:
    df = pd.read_csv("expenses.csv")
except:
    df = pd.DataFrame(columns=["Date","Category","Amount","Type","Description"])

if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"])

# ---------- SIDEBAR ----------
st.sidebar.title("📊 Expense Tracker")

menu = st.sidebar.radio("Navigation", ["Dashboard", "Add Transaction"])

st.sidebar.markdown("## 🔎 Filter")

if not df.empty:
    selected_cat = st.sidebar.multiselect(
        "Category Filter",
        options=df["Category"].unique(),
        default=df["Category"].unique()
    )
    filtered_df = df[df["Category"].isin(selected_cat)]
else:
    filtered_df = df

# ---------- ADD TRANSACTION ----------
if menu == "Add Transaction":
    st.title("➕ Add Transaction")

    amount = st.number_input("Amount", min_value=0.0)
    category = st.selectbox(
        "Category",
        ["Salary","Food","Shopping","Travel","Bills","Entertainment"]
    )
    t_type = st.selectbox("Type", ["Income","Expense"])
    desc = st.text_input("Description")
    date = st.date_input("Date")

    if st.button("Add Transaction"):
        new_data = pd.DataFrame(
            [[date, category, amount, t_type, desc]],
            columns=df.columns
        )
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv("expenses.csv", index=False)
        st.success("✅ Transaction Added!")

# ---------- DASHBOARD ----------
if menu == "Dashboard":

    st.title("💰 Expense Tracker Dashboard")

    # ---------- KPIs ----------
    total = len(filtered_df)
    income = filtered_df[filtered_df["Type"]=="Income"]["Amount"].sum()
    expense = filtered_df[filtered_df["Type"]=="Expense"]["Amount"].sum()
    savings = income - expense

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Transactions", total)
    col2.metric("Income", f"₹{income:.2f}")
    col3.metric("Expense", f"₹{expense:.2f}")
    col4.metric("Savings", f"₹{savings:.2f}")

    # ---------- WELCOME INSIGHT ----------
    if total == 0:
        st.info("👋 Welcome! Start by adding your first transaction.")
    elif savings > 0:
        st.success(f"💰 Great! You're saving ₹{savings:.0f}. Keep it up!")
    else:
        st.warning(f"⚠️ You are overspending by ₹{abs(savings):.0f}.")

    # ---------- QUICK SUMMARY ----------
    st.subheader("⚡ Quick Summary")

    colA, colB, colC = st.columns(3)

    colA.info(f"💵 Total Income: ₹{income:.0f}")
    colB.warning(f"💸 Total Expense: ₹{expense:.0f}")
    colC.success(f"🏦 Savings: ₹{savings:.0f}")

    # ---------- MONTHLY INSIGHT ----------
    st.subheader("📅 Monthly Insight")

    if not filtered_df.empty:
        filtered_df["Month"] = filtered_df["Date"].dt.to_period("M").astype(str)

        monthly = filtered_df.groupby(["Month","Type"])["Amount"].sum().reset_index()

        fig_month = px.bar(
            monthly,
            x="Month",
            y="Amount",
            color="Type",
            barmode="group",
            title="Monthly Income vs Expense"
        )

        st.plotly_chart(fig_month, use_container_width=True)
    else:
        st.info("No data for monthly analysis")

    # ---------- EXPENSE TREND ----------
    colA, colB = st.columns(2)

    with colA:
        st.subheader("📈 Expense Trend")

        if not filtered_df.empty:
            trend = filtered_df[filtered_df["Type"]=="Expense"] \
                .groupby("Date")["Amount"].sum().reset_index()

            fig = px.line(trend, x="Date", y="Amount", markers=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data")

    with colB:
        st.subheader("🥧 Expense Categories")

        if not filtered_df.empty:
            cat = filtered_df[filtered_df["Type"]=="Expense"] \
                .groupby("Category")["Amount"].sum().reset_index()

            fig2 = px.pie(cat, names="Category", values="Amount", hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No data")

    # ---------- INCOME VS EXPENSE ----------
    st.subheader("📊 Income vs Expense")

    compare = pd.DataFrame({
        "Type": ["Income", "Expense"],
        "Amount": [income, expense]
    })

    fig3 = px.bar(compare, x="Type", y="Amount", color="Type")
    st.plotly_chart(fig3, use_container_width=True)

    # ---------- BUDGET ----------
    st.subheader("💸 Budget")

    budget = st.number_input("Monthly Budget", value=5000.0)

    percent = (expense / budget) * 100 if budget > 0 else 0

    st.progress(min(percent/100, 1.0))
    st.write(f"{percent:.1f}% used")

    if expense > budget:
        st.error("🚨 Budget Exceeded")
    else:
        st.success("✅ Under control")

    # ---------- EXPORT ----------
    st.subheader("📥 Export Data")

    if not filtered_df.empty:
        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "expenses.csv", "text/csv")

    # ---------- TABLE ----------
    st.subheader("📋 Recent Transactions")

    if not filtered_df.empty:
        filtered_df = filtered_df.sort_values(by="Date", ascending=False)
        st.dataframe(filtered_df)
    else:
        st.info("No data yet")

    # ---------- CLEAR DATA ----------
    if st.button("⚠️ Clear All Data"):
        df = pd.DataFrame(columns=df.columns)
        df.to_csv("expenses.csv", index=False)
        st.success("All data cleared!")
