import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# ================= LOAD =================
try:
    df = pd.read_csv("expenses.csv")
except:
    df = pd.DataFrame(columns=["Date","Category","Amount","Type","Description"])

# ================= STYLE =================
st.markdown("""
<style>
.main {background-color:#0f172a;}
.block-container {padding-top:2rem;}

.metric-card {
    background:#1e293b;
    padding:20px;
    border-radius:12px;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
st.sidebar.title("📊 Expense Tracker")
menu = st.sidebar.radio("Navigation", ["Dashboard", "Add Transaction"])

# ================= ADD =================
if menu == "Add Transaction":
    st.title("➕ Add Transaction")

    amount = st.number_input("Amount", min_value=0.0)
    category = st.selectbox("Category",
        ["Food","Travel","Shopping","Bills","Entertainment","Salary","Other"])
    type_option = st.selectbox("Type", ["Expense","Income"])
    desc = st.text_input("Description")
    date = st.date_input("Date")

    if st.button("Add Transaction"):
        new = pd.DataFrame([[date, category, amount, type_option, desc]],
                           columns=df.columns)
        df = pd.concat([df,new], ignore_index=True)
        df.to_csv("expenses.csv", index=False)
        st.success("✅ Added successfully!")

# ================= DASHBOARD =================
if menu == "Dashboard":

    st.title("💰 Expense Tracker Dashboard")

    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])

    # ===== FILTER =====
    st.sidebar.subheader("🔎 Filter")
    if not df.empty:
        selected_cat = st.sidebar.multiselect(
            "Category Filter",
            df["Category"].unique(),
            default=df["Category"].unique()
        )
        df = df[df["Category"].isin(selected_cat)]

    # ===== KPIs =====
    total = len(df)
    income = df[df["Type"]=="Income"]["Amount"].sum()
    expense = df[df["Type"]=="Expense"]["Amount"].sum()
    net = income - expense

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Transactions", total)
    col2.metric("Income", f"₹{income:.2f}")
    col3.metric("Expense", f"₹{expense:.2f}")
    col4.metric("Savings", f"₹{net:.2f}")

    # ===== CHARTS =====
    if not df.empty:

        colA, colB = st.columns(2)

        with colA:
            st.subheader("📈 Trend")
            daily = df.groupby("Date")["Amount"].sum().reset_index()
            fig = px.line(daily, x="Date", y="Amount", markers=True)
            st.plotly_chart(fig, use_container_width=True)

        with colB:
            st.subheader("🥧 Categories")
            cat = df.groupby("Category")["Amount"].sum().reset_index()
            fig2 = px.pie(cat, names="Category", values="Amount")
            st.plotly_chart(fig2, use_container_width=True)

        # ===== BAR =====
        st.subheader("📊 Income vs Expense")
        comp = df.groupby("Type")["Amount"].sum().reset_index()
        fig3 = px.bar(comp, x="Type", y="Amount", color="Type")
        st.plotly_chart(fig3, use_container_width=True)

    else:
        st.info("📭 No data yet — add your first transaction!")

    # ===== BUDGET =====
    st.subheader("💸 Budget")

    budget = st.number_input("Monthly Budget", value=5000.0)
    percent = (expense / budget * 100) if budget > 0 else 0

    st.progress(min(percent/100,1.0))
    st.write(f"{percent:.1f}% used")

    if percent > 100:
        st.error("🚨 Budget exceeded")
    else:
        st.success("✅ Under control")

    # ===== EXPORT =====
    st.subheader("📥 Export Data")
    if not df.empty:
        csv = df.to_csv(index=False).encode()
        st.download_button("Download CSV", csv, "expenses.csv", "text/csv")

    # ===== RECENT =====
    st.subheader("📋 Recent")
    st.dataframe(df.tail(5), use_container_width=True)
