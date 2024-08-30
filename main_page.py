from copy import copy

import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import io
import base64

items_per_page = 10
state = None

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
        query += " AND LOWER(full_name) LIKE ?"
        params.append(f"%{full_name.lower()}%")  # Convert search term to lowercase and use wildcards for "contains"
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

# Function to delete a PEZ item from the database
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




# Function to prepare DataFrame from PEZ items
def prepare_pez_dataframe(pez_items, is_admin):
    data = []
    for item in pez_items:
        if item['image']:
            img_html = image_to_base64(item['image'])
        else:
            img_html = "No image available."

        # Include delete button only if user is admin
        if is_admin:
            delete_button_html = f'<form action="" method="get"><input type="hidden" name="delete_id" value="{item["id"]}"/><input type="submit" value="X" style="color: red; cursor: pointer;"/></form>'

            data.append({
                    "Image": img_html,
                    "Full Name": item['full_name'],
                    "Series": item['series'],
                    "Pup Name": item['pup_name'],
                    "Year of Manufacture": item['year_of_manufacture'],
                    "Country of Manufacture": item['country_of_manufacture'],
                    "Patent": item['patent'],
                    "Leg": item['leg'],
                    "Leg Color": item['leg_color'] if item['leg'] in ["with", "thin"] else "--",
                    "Delete": delete_button_html  # Add delete button HTML directly
                })
        else:
            data.append({
                "Image": img_html,
                "Full Name": item['full_name'],
                "Series": item['series'],
                "Pup Name": item['pup_name'],
                "Year of Manufacture": item['year_of_manufacture'],
                "Country of Manufacture": item['country_of_manufacture'],
                "Patent": item['patent'],
                "Leg": item['leg'],
                "Leg Color": item['leg_color'] if item['leg'] in ["with", "thin"] else "--"
            })


    df = pd.DataFrame(data)
    return df

# Function to handle pagination controls and display
def display_pagination_controls(total_pages):
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Previous", disabled=st.session_state.current_page_main_number == 0):
            st.session_state.current_page_main_number -= 1
            st.rerun()
    with col2:
        st.write(f"Page {st.session_state.current_page_main_number + 1} of {total_pages}")
    with col3:
        if st.button("Next", disabled=(st.session_state.current_page_main_number + 1) >= total_pages):
            st.session_state.current_page_main_number += 1
            st.rerun()

# Main page function to display all PEZ items in a table
def main_page():
    st.title("PEZ Collection")

    # Preserve the 'is_admin' status
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False  # Default to non-admin

    # Display the current user's role
    if st.session_state.is_admin:
        st.markdown("### **Status:** Admin")
    else:
        st.markdown("### **Status:** Viewer")

    # Admin-specific features
    if st.session_state.is_admin:
        st.subheader("Admin Features")

        # Button to navigate to the Add PEZ page
        if st.button("Add New PEZ"):
            st.session_state.current_page = "add_pez"
            st.rerun()

        # Logout button
        if st.button("Logout"):
            # Reset admin privileges and redirect to main page
            st.session_state.is_admin = False
            st.rerun()
    else:
        st.write("You are viewing as a guest.")

        # Add the login button for non-admin users
        if st.button("Login as Admin"):
            st.session_state.current_page = "login"
            st.rerun()

    # Initialize session state for pagination
    if 'current_page_main_number' not in st.session_state:
        st.session_state.current_page_main_number = 0

    # Ensure current_page_main_number is an integer
    if not isinstance(st.session_state.current_page_main_number, int):
        st.session_state.current_page_main_number = 0

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
    pez_items = fetch_filtered_pez_items(full_name, series, year, country, patent, leg, leg_color, start_idx,
                                         items_per_page)


    if pez_items:
        df = prepare_pez_dataframe(pez_items, st.session_state.get('is_admin', False))  # Pass admin status
        df.index = df.index + 1 + (st.session_state.current_page_main_number * items_per_page)

        # Display DataFrame with images using st.markdown
        st.markdown(df.to_html(escape=False, index=True), unsafe_allow_html=True)
        display_pagination_controls(total_pages)
    else:
        st.write("No PEZ items found in the collection.")

    query_params = st.query_params
    if 'delete_id' in query_params:
        delete_id = query_params['delete_id']  # Retrieve the delete_id from query parameters
        delete_pez_item(delete_id)  # Call the delete function
        st.success(f"PEZ item with ID {delete_id} deleted successfully!")
        # Clear the query parameters by setting them to an empty dictionary
        st.query_params.clear()
        st.rerun()  # Refresh the page to update the list

if __name__ == "__main__":
    main_page()

if __name__ == "__main__":
    main_page()

if __name__ == "__main__":
    main_page()
