import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# ================= LOAD DATA =================
try:
    df = pd.read_csv("expenses.csv")
except:
    df = pd.DataFrame(columns=["Date","Category","Amount","Type","Description"])

# ================= CUSTOM CSS =================
st.markdown("""
<style>
.big-font {font-size:30px !important; font-weight:bold;}
.card {
    padding: 20px;
    border-radius: 10px;
    background-color: #111827;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
st.sidebar.title("📊 Expense Tracker")

menu = st.sidebar.radio("Navigation", ["Dashboard", "Add Transaction"])

# ================= ADD TRANSACTION =================
if menu == "Add Transaction":
    st.header("➕ Add New Transaction")

    amount = st.number_input("Amount", min_value=0.0)

    category = st.selectbox(
        "Category",
        ["Food","Travel","Shopping","Bills","Entertainment","Salary","Other"]
    )

    type_option = st.selectbox("Type", ["Expense","Income"])

    desc = st.text_input("Description")

    date = st.date_input("Date")

    if st.button("Add Transaction"):
        new_data = pd.DataFrame(
            [[date, category, amount, type_option, desc]],
            columns=df.columns
        )
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv("expenses.csv", index=False)
        st.success("Transaction Added Successfully!")

# ================= DASHBOARD =================
if menu == "Dashboard":

    st.markdown('<p class="big-font">💰 Expense Tracker Dashboard</p>', unsafe_allow_html=True)

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
            st.subheader("🥧 Category Distribution")
            cat = df.groupby("Category")["Amount"].sum().reset_index()
            fig2 = px.pie(cat, names="Category", values="Amount", hole=0.5)
            st.plotly_chart(fig2, use_container_width=True)

    # ================= BUDGET =================
    st.subheader("💸 Budget Status")

    budget = st.number_input("Set Monthly Budget", value=5000.0)

    spent_percent = (expense / budget * 100) if budget > 0 else 0

    st.progress(min(spent_percent/100, 1.0))
    st.write(f"Spent: ₹{expense:.2f} / ₹{budget:.2f} ({spent_percent:.1f}%)")

    if expense > budget:
        st.error("🚨 Budget Exceeded!")
    else:
        st.success("✅ Within Budget")

    # ================= CATEGORY SUGGESTION =================
    if not df.empty:
        top_cat = df.groupby("Category")["Amount"].sum().idxmax()
        st.info(f"💡 You spend most on: {top_cat}")

    # ================= RECENT =================
    st.subheader("📋 Recent Transactions")
    st.dataframe(df.tail(5), use_container_width=True)
