# import streamlit as st
# import sqlite3
# import pandas as pd
# from PIL import Image
# import io
# import base64
#
# items_per_page = 10
#
#
# # Function to connect to the SQLite database
# def get_db_connection():
#     conn = sqlite3.connect('pez_collection.db')
#     conn.row_factory = sqlite3.Row  # Allows accessing rows as dictionaries
#     return conn
#
#
# # Function to fetch PEZ items from the database with pagination
# def fetch_pez_items(offset, limit):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM pez_collection LIMIT ? OFFSET ?", (limit, offset))
#     rows = cursor.fetchall()
#     conn.close()
#     return rows
#
#
# # Function to fetch the total count of PEZ items
# def fetch_total_pez_count():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT COUNT(*) FROM pez_collection")
#     total_count = cursor.fetchone()[0]
#     conn.close()
#     return total_count
#
#
# # Function to display images properly in a DataFrame
# def image_to_base64(img_data, max_width=150):
#     img = Image.open(io.BytesIO(img_data))
#     # Resize image maintaining aspect ratio
#     aspect_ratio = img.width / img.height
#     new_width = max_width
#     new_height = int(new_width / aspect_ratio)
#     img = img.resize((new_width, new_height))
#
#     buffered = io.BytesIO()
#     img.save(buffered, format="PNG")
#     img_base64 = base64.b64encode(buffered.getvalue()).decode()
#     return f'<img src="data:image/png;base64,{img_base64}" style="width:{new_width}px;height:auto;"/>'
#
#
# # Function to display PEZ items
# def display_pez_items(container, offset, limit):
#     # Clear the container first
#     # container.empty()
#     # container = st.empty()
#     data = []
#     df = pd.DataFrame(data)
#
#     container.markdown(
#         df.to_html(escape=False, index=False),
#         unsafe_allow_html=True
#     )
#     # Fetch only the items for the current page
#     pez_items = fetch_pez_items(offset, limit)
#
#     # Debugging: Print the number of items fetched
#     container.write(f"Items fetched: {len(pez_items)}")
#
#     # Prepare data for display in a DataFrame
#     if pez_items:
#         data = []
#         for item in pez_items:
#             # Convert image to base64 to display in DataFrame
#             if item['image']:
#                 img_html = image_to_base64(item['image'])
#             else:
#                 img_html = "No image available."
#
#             data.append({
#                 "Image": img_html,
#                 "Full Name": item['full_name'],
#                 "Series": item['series'],
#                 "Pup Name": item['pup_name'],
#                 "Year of Manufacture": item['year_of_manufacture'],
#                 "Country of Manufacture": item['country_of_manufacture'],
#                 "Patent": item['patent'],
#                 "Leg": item['leg'],
#                 "Leg Color": item['leg_color'] if item['leg'] in ["with", "thin"] else "N/A"
#             })
#
#         # Convert list of dictionaries to a DataFrame
#         df = pd.DataFrame(data)
#
#         # Display DataFrame with images using st.markdown
#         container.markdown(
#             df.to_html(escape=False, index=False),
#             unsafe_allow_html=True
#         )
#     else:
#         container.write("No PEZ items found in the collection.")
#
#
# # Function to update the current page for pagination
# def update_page(change,table_container):
#     st.session_state.current_page += change
#     offset = st.session_state.current_page * items_per_page
#     display_pez_items(table_container, offset, items_per_page)
#
#
# # Streamlit main page to display PEZ items with pagination
# def main_page():
#     st.title("PEZ Collection")
#
#     # Display the current user's role
#     if st.session_state.get('is_admin', False):
#         st.markdown("### **Status:** Admin")
#     else:
#         st.markdown("### **Status:** Viewer")
#
#     # Pagination setup
#     if 'current_page' not in st.session_state:
#         st.session_state.current_page = 0
#
#     # Ensure current_page is an integer, if not reset to 0
#     if not isinstance(st.session_state.current_page, int):
#         st.session_state.current_page = 0
#
#     # Fetch the total number of PEZ items
#     total_items = fetch_total_pez_count()
#     total_pages = (total_items - 1) // items_per_page + 1
#
#     # Calculate offset for the current page
#     offset = st.session_state.current_page * items_per_page
#
#     # Debugging: Print current page and offset
#     st.write(f"Current page: {st.session_state.current_page + 1}, Offset: {offset}")
#
#     # Create separate containers for table and controls
#     table_container = st.empty()
#     controls_container = st.empty()
#
#     # Display items for the current page in the table container
#     display_pez_items(table_container, offset, items_per_page)
#
#     # Pagination controls in the controls container
#     with controls_container:
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             st.button("Previous", disabled=st.session_state.current_page == 0, on_click=update_page, args=(-1,table_container))
#         with col2:
#             st.write(f"Page {st.session_state.current_page + 1} of {total_pages}")
#         with col3:
#             st.button("Next", disabled=(st.session_state.current_page + 1) >= total_pages, on_click=update_page,
#                       args=(1,table_container))
#
#     # Admin-specific features
#     if st.session_state.get('is_admin', False):
#         st.subheader("Admin Features")
#
#         # Button to navigate to the Add PEZ page
#         if st.button("Add New PEZ"):
#             st.session_state.current_page = "add_pez"
#
#         # Logout button
#         if st.button("Logout"):
#             # Reset admin privileges and redirect to main page
#             st.session_state.is_admin = False
#     else:
#         st.write("You are viewing as a guest.")
#
#         # Add the login button for non-admin users
#         if st.button("Login as Admin"):
#             st.session_state.current_page = "login"
#
#
# if __name__ == "__main__":
#     main_page()



import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import io
import base64

# Function to connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('pez_collection.db')
    conn.row_factory = sqlite3.Row  # Allows accessing rows as dictionaries
    return conn

# Function to fetch all PEZ items from the database
def fetch_pez_items(offset, limit):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pez_collection LIMIT ? OFFSET ?", (limit, offset))
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_total_pez_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM pez_collection")
    total_count = cursor.fetchone()[0]
    conn.close()
    return total_count

# Function to display images properly in a DataFrame
def image_to_base64(img_data, max_width=150):
    img = Image.open(io.BytesIO(img_data))
    # Resize image maintaining aspect ratio
    aspect_ratio = img.width / img.height
    new_width = max_width
    new_height = int(new_width / aspect_ratio)
    img = img.resize((new_width, new_height))
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    return f'<img src="data:image/png;base64,{img_base64}" style="width:{new_width}px;height:auto;"/>'

# Streamlit main page to display all PEZ items in a table with pagination
def main_page():
    st.title("PEZ Collection")

    # Display the current user's role
    if st.session_state.get('is_admin', False):
        st.markdown("### **Status:** Admin")
    else:
        st.markdown("### **Status:** Viewer")

    # Fetch all PEZ items from the database

    # Pagination setup
    items_per_page = 10
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0

    # Check if current_page is an integer, if not reset to 0
    if not isinstance(st.session_state.current_page, int):
        st.session_state.current_page = 0
    total_items = fetch_total_pez_count()
    total_pages = (total_items - 1) // items_per_page + 1
    start_idx = st.session_state.current_page * items_per_page
    end_idx = start_idx + items_per_page
    if end_idx > total_items:
        end_idx = total_items
    pez_items = fetch_pez_items(start_idx,end_idx)
    # Prepare data for display in a DataFrame
    if pez_items:
        data = []
        for item in pez_items:  # Display only the current page items
            # Convert image to base64 to display in DataFrame
            if item['image']:
                img_html = image_to_base64(item['image'])  # Increase width for larger display
            else:
                img_html = "No image available."

            data.append({
                "Image": img_html,
                "Full Name": item['full_name'],
                "Series": item['series'],
                "Pup Name": item['pup_name'],
                "Year of Manufacture": item['year_of_manufacture'],
                "Country of Manufacture": item['country_of_manufacture'],
                "Patent": item['patent'],
                "Leg": item['leg'],
                "Leg Color": item['leg_color'] if item['leg'] in ["with", "thin"] else "N/A"
            })

        # Convert list of dictionaries to a DataFrame
        df = pd.DataFrame(data)

        df.index = df.index + 1
        # Display DataFrame with images using st.markdown
        st.markdown(
            df.to_html(escape=False, index=True),
            unsafe_allow_html=True
        )

        # Pagination controls
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Previous", disabled=st.session_state.current_page == 0):
                st.session_state.current_page -= 1
                st.rerun()
        with col2:
            st.write(f"Page {st.session_state.current_page + 1} of {total_pages}")
        with col3:
            if st.button("Next", disabled=(st.session_state.current_page + 1) >= total_pages):
                st.session_state.current_page += 1
                st.rerun()
    else:
        st.write("No PEZ items found in the collection.")

    # Admin-specific features
    if st.session_state.get('is_admin', False):
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
            st.session_state.current_page = "login_page"
            st.rerun()

if __name__ == "__main__":
    main_page()




