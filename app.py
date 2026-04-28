import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
body {
    background-color: #f5f7fb;
}
.block-container {
    padding: 2rem 2rem;
}
.metric-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
}
.section-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
    margin-top: 10px;
}
.sidebar .sidebar-content {
    background: #ffffff;
}
</style>
""", unsafe_allow_html=True)

# ---------- LOAD DATA ----------
try:
    df = pd.read_csv("expenses.csv")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
except:
    df = pd.DataFrame(columns=["Date","Category","Amount","Type","Description"])

# ---------- SIDEBAR ----------
st.sidebar.title("💰 Expense Tracker")

menu = st.sidebar.radio("Navigation", ["Dashboard", "Add Transaction"])

# ---------- ADD ----------
if menu == "Add Transaction":
    st.title("➕ Add Transaction")

    amount = st.number_input("Amount", 0.0)
    category = st.selectbox("Category",
        ["Food","Shopping","Transport","Bills","Entertainment","Salary","Other"]
    )
    t_type = st.selectbox("Type", ["Expense","Income"])
    desc = st.text_input("Description")
    date = st.date_input("Date")

    if st.button("Add"):
        new = pd.DataFrame({
            "Date":[date],
            "Category":[category],
            "Amount":[amount],
            "Type":[t_type],
            "Description":[desc]
        })
        df = pd.concat([df, new], ignore_index=True)
        df.to_csv("expenses.csv", index=False)
        st.success("Added!")

# ---------- DASHBOARD ----------
if menu == "Dashboard":

    st.markdown("## Dashboard")

    if df.empty:
        st.info("Add some transactions")
        st.stop()

    df = df.dropna(subset=["Date"])
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    income = df[df["Type"]=="Income"]["Amount"].sum()
    expense = df[df["Type"]=="Expense"]["Amount"].sum()
    savings = income - expense

    # ---------- CARDS ----------
    c1,c2,c3,c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
        <h4>Total Transactions</h4>
        <h2>{len(df)}</h2>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
        <h4>Total Income</h4>
        <h2>₹{income:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
        <h4>Total Expenses</h4>
        <h2>₹{expense:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
        <h4>Net Savings</h4>
        <h2>₹{savings:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

    # ---------- CHARTS ----------
    col1, col2, col3 = st.columns(3)

    df_sorted = df.sort_values("Date")

    df_sorted["Signed"] = df_sorted.apply(
        lambda x: x["Amount"] if x["Type"]=="Income" else -x["Amount"], axis=1
    )

    balance = df_sorted.groupby("Date")["Signed"].sum().cumsum().reset_index()

    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Balance Over Time")
        fig1 = px.line(balance, x="Date", y="Signed")
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Expenses by Category")
        exp_cat = df[df["Type"]=="Expense"].groupby("Category")["Amount"].sum().reset_index()
        if not exp_cat.empty:
            fig2 = px.pie(exp_cat, names="Category", values="Amount")
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Expenses Trend")
        exp_df = df[df["Type"]=="Expense"]
        if not exp_df.empty:
            fig3 = px.line(exp_df, x="Date", y="Amount")
            st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------- TABLE ----------
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Recent Transactions")
    st.dataframe(df.sort_values("Date", ascending=False))
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- BUDGET ----------
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Budget Status")

    budget = st.number_input("Monthly Budget", value=50000.0)

    used = (expense / budget * 100) if budget > 0 else 0

    st.progress(min(int(used),100))
    st.write(f"{used:.1f}% used")

    if used > 80:
        st.error("⚠ Budget Alert!")
    else:
        st.success("Good control")

    st.markdown('</div>', unsafe_allow_html=True)
