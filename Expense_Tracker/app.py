import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector
import bcrypt
from datetime import datetime
import calendar

# ---- MySQL Connection ----
DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PASSWORD = 'Hanju@1993'
DB_NAME = 'expense_tracker'

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

get_db_connection()

# ---- Database Setup ----
def setup_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(100) NOT NULL
        )
    """)
    # Expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            category VARCHAR(50),
            expense_name VARCHAR(100),
            amount FLOAT,
            due_date DATE,
            debited BOOLEAN DEFAULT FALSE,
            created_at DATETIME,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    # Credits table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS credits (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            credit_type VARCHAR(50),
            amount FLOAT,
            created_at DATETIME,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

setup_database()

# ---- User Authentication ----
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def register_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return False, "Username already exists."
    hashed = hash_password(password)
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed.decode()))
    conn.commit()
    cursor.close()
    conn.close()
    return True, "Registration successful."

def authenticate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE username=%s", (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result and check_password(password, result[1]):
        return True, result[0]
    return False, None

# ---- Data Operations ----
def add_expense(user_id, category, expense_name, amount, due_day):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO expenses (user_id, category, expense_name, amount, due_day, debited, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (user_id, category, expense_name, amount, due_day, False, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()

def edit_expense(expense_id, user_id, category, expense_name, amount, due_day):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE expenses
        SET category=%s, expense_name=%s, amount=%s, due_day=%s
        WHERE id=%s AND user_id=%s
    """, (category, expense_name, amount, due_day, expense_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()

def delete_expense(expense_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=%s AND user_id=%s", (expense_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()

def update_expense_debited(expense_id, user_id, debited):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE expenses SET debited=%s WHERE id=%s AND user_id=%s", (debited, expense_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()



def get_expenses(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM expenses WHERE user_id=%s ORDER BY due_date ASC
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def add_credit(user_id, credit_type, amount):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO credits (user_id, credit_type, amount, created_at)
        VALUES (%s, %s, %s, %s)
    """, (user_id, credit_type, amount, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()

def get_credits(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM credits WHERE user_id=%s", (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows



# ---- Streamlit App ----
st.set_page_config(page_title="Expense Tracker", layout="wide")

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None

if not st.session_state.authenticated:
    st.title("Login or Register")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            success, user_id = authenticate_user(username, password)
            if success:
                st.session_state.authenticated = True
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
    with tab2:
        new_username = st.text_input("New Username", key="reg_user")
        new_password = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Register"):
            ok, msg = register_user(new_username, new_password)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
else:
    st.sidebar.write(f"Logged in as **{st.session_state.username}**")
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()

    st.title("Personal Expense Dashboard")

    # --- Add Expense ---
    with st.expander("Add Expense"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            category = st.selectbox("Category", ["Credit Cards", "Loans", "Pay Later", "Investments", "Necessities", "Other"])
        with col2:
            expense_name = st.text_input("Expense Name")
        with col3:
            amount = st.number_input("Amount", min_value=0.0, step=1.0)
        with col4:
            due_day = st.number_input("Payment Day (1-31)", min_value=1, max_value=31, value=datetime.now().day)
        if st.button("Add Expense"):
            if expense_name and amount >= 0:
                add_expense(st.session_state.user_id, category, expense_name, amount, due_day)
                st.success("Expense added!")
                st.rerun()
            else:
                st.error("Please provide valid expense details.")

    # --- Add Credit ---
    with st.expander("Add Credit"):
        credit_type = st.selectbox("Credit Type", ["Salary", "SWP", "Money from outside", "Other"])
        credit_amount = st.number_input("Credit Amount", min_value=0.0, step=1.0)
        if st.button("Add Credit"):
            if credit_amount >= 0:
                add_credit(st.session_state.user_id, credit_type, credit_amount)
                st.success("Credit added!")
                st.rerun()
            else:
                st.error("Please enter a valid credit amount.")

    # --- Load Data ---
    expenses = get_expenses(st.session_state.user_id)
    credits = get_credits(st.session_state.user_id)
    df_exp = pd.DataFrame(expenses)
    df_cred = pd.DataFrame(credits)

    # --- KPIs ---
    st.subheader("Overview")
    total_expenses = df_exp['amount'].sum() if not df_exp.empty else 0
    total_credits = df_cred['amount'].sum() if not df_cred.empty else 0
    savings = total_credits - total_expenses
    yet_to_pay = df_exp.loc[df_exp['debited'] == 0, 'amount'].sum() if not df_exp.empty else 0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Expenses", f"₹{total_expenses:,.2f}")
    kpi2.metric("Total Credits", f"₹{total_credits:,.2f}")
    kpi3.metric("Savings", f"₹{savings:,.2f}")
    kpi4.metric("Yet to Pay", f"₹{yet_to_pay:,.2f}")

    category_colors = {
        "Credit Cards": "#FF6384",
        "Loans": "#36A2EB",
        "Pay Later": "#E7735F",
        "Investments": "#4BC0C0",
        "Necessities": "#9966FF",
        "Other": "#E7790B"
    }

    # --- Pie Chart ---
    if not df_exp.empty:
        pie = px.pie(
            df_exp,
            names='category',
            values='amount',
            title="Expense Categories",
            color='category',
            color_discrete_map=category_colors
        )
        st.plotly_chart(pie, use_container_width=True)

        # --- Category-wise KPIs ---
        st.subheader("Total by Category")
        categories = df_exp['category'].unique()
        cat_cols = st.columns(len(categories))
        for i, cat in enumerate(categories):
            total = df_exp[df_exp['category'] == cat]['amount'].sum()
            color = category_colors.get(cat, "#333333")
            cat_cols[i].markdown(
                f"<div style='color:{color};font-weight:bold'>{cat}</div>",
                unsafe_allow_html=True
            )
            cat_cols[i].metric("", f"₹{total:,.2f}")

     # --- Edit Expense Table ---
    st.subheader("Your Expenses")
    if not df_exp.empty:
        # If you have a 'due_day' column, use it; otherwise, extract from 'due_date'
        if 'due_day' in df_exp.columns:
            due_days = df_exp['due_day']
        else:
            due_days = pd.to_datetime(df_exp['due_date']).dt.day

        # Generate due date for current or previous month based on due_day
        now = datetime.now()
        last_day = calendar.monthrange(now.year, now.month)[1]

        due_dates_this_month = []
        for day in due_days:
            if day > 26:
                # Go to previous month
                prev_month = now.month - 1 if now.month > 1 else 12
                prev_year = now.year if now.month > 1 else now.year - 1
                prev_last_day = calendar.monthrange(prev_year, prev_month)[1]
                safe_day = min(day, prev_last_day)
                due_date = datetime(prev_year, prev_month, safe_day).strftime('%d-%b-%Y')
            else:
                safe_day = min(day, last_day)
                due_date = datetime(now.year, now.month, safe_day).strftime('%d-%b-%Y')
            due_dates_this_month.append(due_date)

        df_exp['Due Date (This Month)'] = due_dates_this_month

        df_exp['Due Date'] = pd.to_datetime(df_exp['due_date']).dt.strftime('%d-%b-%Y')
        df_exp['Debited Amount'] = df_exp.apply(lambda row: row['amount'] if row['debited'] else 0, axis=1)
        df_exp = df_exp.rename(columns={
            'category': 'Category',
            'expense_name': 'Expense',
            'amount': 'Amount',
            'Due Date': 'Due Date',
            'debited': 'Debited'
        })
        df_exp_display = df_exp[['id', 'Category', 'Expense', 'Amount', 'Due Date (This Month)', 'Debited', 'Debited Amount']]
        df_exp_display = df_exp_display.sort_values('Category')

        # Add this block:
        if 'due_day' in df_exp.columns:
            df_exp_display['Due Day'] = df_exp['due_day']
        else:
            df_exp_display['Due Day'] = pd.to_datetime(df_exp['due_date']).dt.day

        if 'edit_row_id' not in st.session_state:
            st.session_state.edit_row_id = None

        for idx, row in df_exp_display.iterrows():
            cols = st.columns([1,2,1,1,1,1,1,1])
            cols[0].write(row['Category'])
            cols[1].write(row['Expense'])
            cols[2].write(f"₹{row['Amount']:,.2f}")
            cols[3].write(row['Due Date (This Month)'])  # Show current month's due date
            paid = cols[4].checkbox("Paid", value=bool(row['Debited']), key=f"paid_{row['id']}")
            if paid != bool(row['Debited']):
                update_expense_debited(row['id'], st.session_state.user_id, paid)
                st.rerun()
            cols[5].write(f"₹{row['Debited Amount']:,.2f}")

            # Edit button sets the row to be edited
            if cols[6].button("✏️", key=f"edit_{row['id']}"):
                st.session_state.edit_row_id = row['id']
                st.rerun()

            # Only show the form for the row being edited
            if st.session_state.edit_row_id == row['id']:
                with st.form(f"edit_form_{row['id']}", clear_on_submit=False):
                    new_category = st.selectbox(
                        "Category",
                        ["Credit Cards", "Loans", "Pay Later", "Investments", "Necessities", "Other"],
                        index=["Credit Cards", "Loans", "Pay Later", "Investments", "Necessities", "Other"].index(row['Category']),
                        key=f"edit_category_{row['id']}"
                    )
                    new_expense_name = st.text_input("Expense Name", value=row['Expense'], key=f"edit_expense_{row['id']}")
                    new_amount = st.number_input("Amount", min_value=0.0, step=1.0, value=row['Amount'], key=f"edit_amount_{row['id']}")
                    new_due_day = st.number_input("Payment Day (1-31)", min_value=1, max_value=31, value=row['Due Day'], key=f"edit_due_{row['id']}")
                    submitted = st.form_submit_button("Save")
                    if submitted:
                        edit_expense(row['id'], st.session_state.user_id, new_category, new_expense_name, new_amount, new_due_day)
                        st.success("Expense updated!")
                        st.session_state.edit_row_id = None
                        st.rerun()
                # Optionally, add a cancel button
                if st.button("Cancel", key=f"cancel_edit_{row['id']}"):
                    st.session_state.edit_row_id = None
                    st.rerun()

            if cols[7].button("❌", key=f"del_{row['id']}"):
                delete_expense(row['id'], st.session_state.user_id)
                st.rerun()
    else:
        st.info("No expenses added yet.")


    # --- Unpaid Expenses Table ---
    st.subheader("Unpaid Expenses (Yet to Pay)")
    unpaid_exp = df_exp_display[df_exp_display['Debited'] == 0].reset_index(drop=True)

    if not unpaid_exp.empty:
        unpaid_exp = unpaid_exp.copy()
        unpaid_exp['Due Day'] = pd.to_datetime(unpaid_exp['Due Date (This Month)'], format='%d-%b-%Y').dt.day
        st.dataframe(
            unpaid_exp[['Category', 'Expense', 'Amount', 'Due Day']],
            use_container_width=True
        )
    else:
        st.info("No unpaid expenses!")

    # --- Credits Table ---
    st.subheader("Your Credits")
    if not df_cred.empty:
        df_cred['Date'] = pd.to_datetime(df_cred['created_at']).dt.strftime('%d-%b-%Y')
        st.dataframe(df_cred[['credit_type', 'amount', 'Date']].rename(
            columns={'credit_type':'Credit Type', 'amount':'Amount'}), use_container_width=True)
    else:
        st.info("No credits added yet.")

