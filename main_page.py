import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import io
import base64

items_per_page = 10


# Function to connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('pez_collection.db')
    conn.row_factory = sqlite3.Row  # Allows accessing rows as dictionaries
    return conn


# Function to fetch PEZ items with filters
def fetch_filtered_pez_items(full_name, series, year, country, patent, leg, leg_color, offset, limit):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM pez_collection WHERE 1=1"
    params = []

    # Adding filters to the query
    if full_name:
        query += " AND full_name LIKE ?"
        params.append(f"%{full_name}%")
    if series:
        query += " AND series = ?"
        params.append(series)
    if year:
        query += " AND year_of_manufacture = ?"
        params.append(year)
    if country:
        query += " AND country_of_manufacture = ?"
        params.append(country)
    if patent:
        query += " AND patent = ?"
        params.append(patent)
    if leg:
        query += " AND leg = ?"
        params.append(leg)
    if leg_color:
        query += " AND leg_color = ?"
        params.append(leg_color)

    query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


# Function to fetch distinct values for filters
def fetch_distinct_values(column_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT DISTINCT {column_name} FROM pez_collection")
    values = [row[column_name] for row in cursor.fetchall()]
    conn.close()
    return values


def delete_pez_item(pez_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pez_collection WHERE id = ?", (pez_id,))
    conn.commit()
    conn.close()


# Function to fetch the total count of PEZ items with filters
def fetch_filtered_pez_count(full_name, series, year, country, patent, leg, leg_color):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM pez_collection WHERE 1=1"
    params = []

    # Adding filters to the query
    if full_name:
        query += " AND full_name LIKE ?"
        params.append(f"%{full_name}%")
    if series:
        query += " AND series = ?"
        params.append(series)
    if year:
        query += " AND year_of_manufacture = ?"
        params.append(year)
    if country:
        query += " AND country_of_manufacture = ?"
        params.append(country)
    if patent:
        query += " AND patent = ?"
        params.append(patent)
    if leg:
        query += " AND leg = ?"
        params.append(leg)
    if leg_color:
        query += " AND leg_color = ?"
        params.append(leg_color)

    cursor.execute(query, params)
    total_count = cursor.fetchone()[0]
    conn.close()
    return total_count


# Function to display images properly in a DataFrame
def image_to_base64(img_data, max_width=150):
    img = Image.open(io.BytesIO(img_data))
    aspect_ratio = img.width / img.height
    new_width = max_width
    new_height = int(new_width / aspect_ratio)
    img = img.resize((new_width, new_height))

    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    return f'<img src="data:image/png;base64,{img_base64}" style="width:{new_width}px;height:auto;"/>'


# Function to prepare DataFrame from PEZ items with delete buttons for admins
def prepare_pez_dataframe(pez_items, is_admin):
    data = []
    for item in pez_items:
        if item['image']:
            img_html = image_to_base64(item['image'])
        else:
            img_html = "No image available."

        delete_button = ''
        if is_admin:
            # Add delete button as HTML in the DataFrame for each item
            delete_button = f'<button onclick="window.location.href=\'/?delete_id={item["id"]}\'" style="color: red; cursor: pointer;">X</button>'

        data.append({
            "Image": img_html,
            "Full Name": item['full_name'],
            "Series": item['series'],
            "Pup Name": item['pup_name'],
            "Year of Manufacture": item['year_of_manufacture'],
            "Country of Manufacture": item['country_of_manufacture'],
            "Patent": item['patent'],
            "Leg": item['leg'],
            "Leg Color": item['leg_color'] if item['leg'] in ["with", "thin"] else "N/A",
            "Delete": delete_button if is_admin else ''  # Only show delete button for admins
        })

    # Convert list of dictionaries to a DataFrame
    df = pd.DataFrame(data)
    return df


# Function to handle pagination controls and display
def display_pagination_controls(total_pages):
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Previous", disabled=st.session_state.current_page_main_number == 0):
            st.session_state.current_page_main_number -= 1
            st.experimental_rerun()
    with col2:
        st.write(f"Page {st.session_state.current_page_main_number + 1} of {total_pages}")
    with col3:
        if st.button("Next", disabled=(st.session_state.current_page_main_number + 1) >= total_pages):
            st.session_state.current_page_main_number += 1
            st.experimental_rerun()


# Main page function to display all PEZ items in a table
def main_page():
    st.title("PEZ Collection")

    # Display the current user's role
    if st.session_state.get('is_admin', False):
        st.markdown("### **Status:** Admin")
    else:
        st.markdown("### **Status:** Viewer")

    # Initialize session state for pagination
    if 'current_page_main_number' not in st.session_state:
        st.session_state.current_page_main_number = 0

    # Ensure current_page_main_number is an integer
    if not isinstance(st.session_state.current_page_main_number, int):
        st.session_state.current_page_main_number = 0

    # Check for delete action in query parameters
    query_params = st.experimental_get_query_params()
    if 'delete_id' in query_params:
        delete_id = query_params['delete_id'][0]
        if st.session_state.get(f'confirm_delete_{delete_id}', None) is None:
            st.session_state[f'confirm_delete_{delete_id}'] = st.radio(
                f"Are you sure you want to delete this item?",
                ('No', 'Yes'), key=f"confirm_{delete_id}"
            )
        elif st.session_state[f'confirm_delete_{delete_id}'] == 'Yes':
            delete_pez_item(delete_id)
            st.success(f"PEZ item with ID {delete_id} deleted successfully!")
            # Remove delete_id from query params and rerun
            st.experimental_set_query_params()
            st.experimental_rerun()
        elif st.session_state[f'confirm_delete_{delete_id}'] == 'No':
            st.experimental_set_query_params()

    # Add filters and search options
    st.sidebar.header("Filter and Search Options")
    full_name = st.sidebar.text_input("Search by Full Name")
    series = st.sidebar.selectbox("Filter by Series", [""] + fetch_distinct_values("series"))
    year = st.sidebar.selectbox("Filter by Year of Manufacture", [""] + fetch_distinct_values("year_of_manufacture"))
    country = st.sidebar.selectbox("Filter by Country of Manufacture", [""] + fetch_distinct_values("country_of_manufacture"))
    patent = st.sidebar.selectbox("Filter by Patent", [""] + fetch_distinct_values("patent"))
    leg = st.sidebar.selectbox("Filter by Leg", [""] + fetch_distinct_values("leg"))
    leg_color = st.sidebar.selectbox("Filter by Leg Color", [""] + fetch_distinct_values("leg_color"))

    # Fetch filtered item count and calculate pagination
    total_items = fetch_filtered_pez_count(full_name, series, year, country, patent, leg, leg_color)
    total_pages = (total_items - 1) // items_per_page + 1
    start_idx = st.session_state.current_page_main_number * items_per_page

    # Fetch and prepare filtered PEZ items for display
    pez_items = fetch_filtered_pez_items(full_name, series, year, country, patent, leg, leg_color, start_idx, items_per_page)
    if pez_items:
        df = prepare_pez_dataframe(pez_items, st.session_state.get('is_admin', False))
        df.index = df.index + 1 + (st.session_state.current_page_main_number * items_per_page)

        # Display DataFrame with images using st.markdown
        st.markdown(df.to_html(escape=False, index=True), unsafe_allow_html=True)

        # Display pagination controls
        display_pagination_controls(total_pages)
    else:
        st.write("No PEZ items found in the collection.")

    # Admin-specific features
    if st.session_state.get('is_admin', False):
        st.subheader("Admin Features")

        # Button to navigate to the Add PEZ page
        if st.button("Add New PEZ"):
            st.session_state.current_page = "add_pez"
            st.experimental_rerun()

        # Logout button
        if st.button("Logout"):
            # Reset admin privileges and redirect to main page
            st.session_state.is_admin = False
            st.experimental_rerun()
    else:
        st.write("You are viewing as a guest.")

        # Add the login button for non-admin users
        if st.button("Login as Admin"):
            st.session_state.current_page = "login"
            st.experimental_rerun()


if __name__ == "__main__":
    main_page()
