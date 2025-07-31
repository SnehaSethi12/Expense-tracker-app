import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import io

# Initialize session state
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Category", "Description", "Amount"])
if 'budget' not in st.session_state:
    st.session_state.budget = None

# Sidebar navigation
st.sidebar.title("💼 Personal Expense Tracker")
page = st.sidebar.radio("MENU", ["🏠 Home", "➕ Add Expense", "📊 View Summary", "🧹 Edit/Delete", "⚠️ Budget Alert", "📤 Export"])

# Helper functions
def add_expense(date, category, description, amount):
    new_expense = pd.DataFrame([[date, category, description, amount]],
                              columns=["Date", "Category", "Description", "Amount"])
    st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], ignore_index=True)

def delete_expense(index):
    st.session_state.expenses = st.session_state.expenses.drop(index=index).reset_index(drop=True)

# Pages
if page == "🏠 Home":
    st.title("Welcome to your Personal Expense Tracker 💼")
    st.write("Track your expenses, analyze spending, and stay on budget.")
    
    if not st.session_state.expenses.empty:
        st.write("### Recent Expenses")
        st.dataframe(st.session_state.expenses.tail(5))
        
        if st.session_state.budget:
            total_spent = st.session_state.expenses["Amount"].sum()
            remaining = st.session_state.budget - total_spent
            st.metric("Monthly Budget", f"₹{st.session_state.budget}", f"₹{remaining:.2f} remaining")

elif page == "➕ Add Expense":
    st.title("Add Expense")
    
    with st.form("expense_form"):
        date = st.date_input("Date", datetime.now())
        category = st.text_input("Category")
        description = st.text_input("Description")
        amount = st.number_input("Amount", min_value=0.0, step=0.01, format="%.2f")
        
        submitted = st.form_submit_button("Add Expense")
        if submitted:
            if not category or not description:
                st.error("Please fill in all fields")
            else:
                add_expense(date, category, description, amount)
                st.success("Expense added successfully!")
                st.rerun()

elif page == "📊 View Summary":
    st.title("Expense Summary")
    
    if st.session_state.expenses.empty:
        st.warning("No expenses to show")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Spending by Category")
            cat_sum = st.session_state.expenses.groupby("Category")["Amount"].sum()
            fig1, ax1 = plt.subplots()
            ax1.pie(cat_sum, labels=cat_sum.index, autopct='%1.1f%%')
            st.pyplot(fig1)
        
        with col2:
            st.write("### Daily Expenses")
            daily = st.session_state.expenses.groupby("Date")["Amount"].sum()
            fig2, ax2 = plt.subplots()
            daily.plot(kind="bar", ax=ax2)
            plt.xticks(rotation=45)
            st.pyplot(fig2)
        
        st.write("### All Expenses")
        st.dataframe(st.session_state.expenses)

elif page == "🧹 Edit/Delete":
    st.title("Edit/Delete Expenses")
    
    if st.session_state.expenses.empty:
        st.warning("No expenses to edit")
    else:
        edited_df = st.data_editor(
            st.session_state.expenses,
            num_rows="dynamic",
            column_config={
                "Date": st.column_config.DateColumn("Date"),
                "Amount": st.column_config.NumberColumn("Amount", format="%.2f")
            }
        )
        
        if st.button("Save Changes"):
            st.session_state.expenses = edited_df
            st.success("Changes saved!")
            st.rerun()
        
        if st.button("Clear All Expenses", type="primary"):
            st.session_state.expenses = pd.DataFrame(columns=["Date", "Category", "Description", "Amount"])
            st.success("All expenses cleared!")
            st.rerun()

elif page == "⚠️ Budget Alert":
    st.title("Set Monthly Budget")
    
    current_budget = st.session_state.budget or 0.0
    new_budget = st.number_input("Enter monthly budget amount", 
                                min_value=0.0, 
                                value=float(current_budget),
                                step=100.0,
                                format="%.2f")
    
    if st.button("Save Budget"):
        st.session_state.budget = new_budget
        st.success(f"Budget set to ₹{new_budget:.2f}")
    
    if st.session_state.budget:
        total_spent = st.session_state.expenses["Amount"].sum()
        remaining = st.session_state.budget - total_spent
        st.metric("Budget Status", 
                 f"₹{total_spent:.2f} spent", 
                 f"₹{remaining:.2f} remaining")
        
        if remaining < 0:
            st.error("You've exceeded your budget!")
        elif remaining < (st.session_state.budget * 0.2):
            st.warning("You're close to exceeding your budget!")

elif page == "📤 Export":
    st.title("Export Data")
    
    if st.session_state.expenses.empty:
        st.warning("No data to export")
    else:
        export_format = st.radio("Export format", ["Excel", "CSV"])
        
        if export_format == "Excel":
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer) as writer:
                st.session_state.expenses.to_excel(writer, index=False)
            st.download_button(
                label="Download Excel",
                data=buffer,
                file_name="expenses.xlsx",
                mime="application/vnd.ms-excel"
            )
        else:
            csv = st.session_state.expenses.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="expenses.csv",
                mime="text/csv"
            )