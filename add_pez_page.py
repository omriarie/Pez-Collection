import streamlit as st
import sqlite3
from PIL import Image
import io


# Function to connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('pez_collection.db')
    conn.row_factory = sqlite3.Row  # Allows accessing rows as dictionaries
    return conn


# Function to generate the next PEZ ID
def generate_next_id():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM pez_collection")
    max_id = cursor.fetchone()[0]

    if max_id:
        # Strip prefix and convert to integer, then increment
        next_id = int(max_id.replace("PEZ", "")) + 1
        new_id = f"PEZ{str(next_id).zfill(4)}"  # Format as PEZ0001, PEZ0002, etc.
    else:
        new_id = "PEZ0001"  # Start with PEZ0001 if the table is empty

    conn.close()
    return new_id


# Function to add a new PEZ to the database
def add_pez(id, full_name, series, pup_name, year_of_manufacture, country_of_manufacture, patent, leg, leg_color,
            image):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO pez_collection (id, full_name, series, pup_name, year_of_manufacture, country_of_manufacture, patent, leg, leg_color, image)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (id, full_name, series, pup_name, year_of_manufacture, country_of_manufacture, patent, leg, leg_color, image))
    conn.commit()
    conn.close()


# Function to fetch unique series from the database
def fetch_unique_series():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT series FROM pez_collection")
    series = [row['series'] for row in cursor.fetchall()]
    conn.close()
    return series


# Function to fetch unique countries based on the selected series
def fetch_countries_by_series(selected_series):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT country_of_manufacture FROM pez_collection WHERE series = ?", (selected_series,))
    countries = [row['country_of_manufacture'] for row in cursor.fetchall()]
    conn.close()
    return countries


# Function to fetch unique years based on the selected series
def fetch_years_by_series(selected_series):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT year_of_manufacture FROM pez_collection WHERE series = ?", (selected_series,))
    years = [row['year_of_manufacture'] for row in cursor.fetchall()]
    conn.close()
    return years


# Function to reset form fields
def reset_form():
    st.session_state.full_name = ''
    st.session_state.series = ''
    st.session_state.pup_name = ''
    st.session_state.year_of_manufacture = 1900
    st.session_state.country_of_manufacture = ''
    st.session_state.patent = ''
    st.session_state.leg = 'with'
    st.session_state.leg_color = ''
    st.session_state.image_file = None


# Streamlit app code for adding a PEZ item
def add_pez_page():
    st.title("Add a New PEZ")

    # Generate the next ID automatically
    pez_id = generate_next_id()
    st.write(f"Generated PEZ ID: {pez_id}")

    # Initialize session state variables for form input fields
    if 'full_name' not in st.session_state:
        reset_form()

    # Fetch existing series for the dropdown
    existing_series = fetch_unique_series()

    # Display series input fields side by side
    col1, col2 = st.columns(2)
    with col1:
        selected_series = st.selectbox("Select Series", options=[""] + existing_series)
    with col2:
        if selected_series:
            st.session_state.series = selected_series
        else:
            st.session_state.series = st.text_input("Or Add a New Series", value=st.session_state.series)

    # Fetch countries based on selected series
    if st.session_state.series:
        countries = fetch_countries_by_series(st.session_state.series)
    else:
        countries = []

    # Display country input fields side by side
    col1, col2 = st.columns(2)
    with col1:
        selected_country = st.selectbox("Country of Manufacture", options=[""] + countries)
    with col2:
        if selected_country:
            st.session_state.country_of_manufacture = selected_country
        else:
            st.session_state.country_of_manufacture = st.text_input("Or Add a New Country",
                                                                    value=st.session_state.country_of_manufacture)

    # Fetch years based on selected series
    if st.session_state.series:
        years = fetch_years_by_series(st.session_state.series)
    else:
        years = []

    # Display year input fields side by side
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("Year of Manufacture", options=[""] + [str(year) for year in years])
    with col2:
        if selected_year:
            st.session_state.year_of_manufacture = int(selected_year)
        else:
            st.session_state.year_of_manufacture = st.number_input("Or Add a New Year", min_value=1900, max_value=2100,
                                                                   step=1, value=st.session_state.year_of_manufacture)

    # Form inputs for PEZ data
    st.session_state.full_name = st.text_input("Full Name", value=st.session_state.full_name)
    st.session_state.pup_name = st.text_input("Pup Name", value=st.session_state.pup_name)
    st.session_state.patent = st.text_input("Patent", value=st.session_state.patent)
    st.session_state.leg = st.selectbox("Leg", options=["with", "without", "thin"],
                                        index=["with", "without", "thin"].index(st.session_state.leg))
    st.session_state.leg_color = st.text_input("Leg Color",
                                               value=st.session_state.leg_color) if st.session_state.leg in ["with",
                                                                                                             "thin"] else None
    st.session_state.image_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    image = st.session_state.image_file.read() if st.session_state.image_file else None

    # Button to add PEZ to the database
    if st.button("Add PEZ"):
        if st.session_state.full_name and st.session_state.pup_name and st.session_state.series:  # Ensure mandatory fields are filled
            add_pez(pez_id, st.session_state.full_name, st.session_state.series, st.session_state.pup_name,
                    st.session_state.year_of_manufacture, st.session_state.country_of_manufacture,
                    st.session_state.patent, st.session_state.leg, st.session_state.leg_color, image)
            st.success(f"PEZ item '{st.session_state.full_name}' added successfully with ID {pez_id}!")

            # Clear form fields after submission
            reset_form()
        else:
            st.error("Please fill in the mandatory fields: Full Name, Pup Name, and Series.")

    # Reset button to clear form fields
    if st.button("Reset"):
        reset_form()

    # Button to return to the main page
    if st.button("Back to Main Page"):
        st.session_state.current_page = "main"
        st.experimental_rerun()


if __name__ == "__main__":
    add_pez_page()