import streamlit as st
from main_page import main_page
from login_page import login_page
from add_pez_page import add_pez_page  # Import the new page


st.set_page_config(layout="wide")

# Initialize session state for page navigation and admin privileges
if 'current_page' not in st.session_state:
    st.session_state.current_page = "main"
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

# Display the current page based on session state
if st.session_state.current_page == "main":
    main_page()
elif st.session_state.current_page == "login":
    login_page()
elif st.session_state.current_page == "add_pez":  # New page condition
    add_pez_page()
