import streamlit as st
import pandas as pd

# Load admin users from CSV
def load_admin_users(csv_file):
    return pd.read_csv(csv_file)

# Check if the entered username and password are in the admin users CSV
def authenticate(username, password, admin_users):
    if not admin_users.empty:
        user_row = admin_users[(admin_users['username'] == username) & (admin_users['password'] == password)]
        return not user_row.empty
    return False

def login_page():
    st.title("Admin Login")

    # Load the admin users CSV
    admin_users = load_admin_users('admin_users.csv')

    # Admin login functionality
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", key='username')
        password = st.text_input("Password", type="password", key='password')
        login_button = st.form_submit_button("Submit")

        if login_button:
            if authenticate(username, password, admin_users):
                st.success("Login successful! You have admin privileges.")
                st.session_state.is_admin = True  # Set admin status in session state
                st.session_state.current_page = "main"  # Redirect to main page
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")

    # Button to navigate back to the main page
    if st.button("Back to Main Page"):
        st.session_state.current_page = "main"
        st.experimental_rerun()

if __name__ == "__main__":
    login_page()
