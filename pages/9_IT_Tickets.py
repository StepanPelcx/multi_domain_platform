import streamlit as st
import pandas as pd
import numpy as np
from data.tickets import migrate_datasets, insert_ticket, get_all_tickets, update_ticket_status, delete_ticket, get_tickets_by_category_count, get_tickets_by_status
from datetime import date

st.set_page_config(page_title="🎟️Tickets Dashboard🎟️", page_icon="🎟️📋", layout="wide")

# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py") # back to the first page
    st.stop()

st.header("🎟️Tickets Dashboard🎟️")

# Sidebar logout button
with st.sidebar:
    if st.button("Log out   ➜]"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.info("You have been logged out.")
        st.switch_page("Home.py")

    if not st.session_state.logged_in:
        st.error("You must be logged in...")
        st.switch_page("Home.py")
        st.stop()

# Sidebar back to dashboard button
with st.sidebar:
    if st.button("Back to Dashboard"):
        st.switch_page("pages/1_Dashboard.py")
        

st.subheader("Migrate Tickets From CSV File")
st.info("Make sure CSV file is migrated before working with other functions.")

# Button to trigger migration
if st.button("🚀 Migrate Tickets"):
    migration = migrate_datasets()

    if migration:
        st.success("✅All tickets migrated.✅")
    else:
        st.error("❌Was not able to migrate the tickets.❌")


#============================================================================================================================================
# CRUD Functions
#============================================================================================================================================

st.subheader("Insert IT Ticket")

with st.form("ticket_form"):
    #getting input values from the user
    ticket_id = st.text_input("Ticket ID")
    priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
    status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
    category = st.text_input("Category")
    subject = st.text_input("Subject")
    description = st.text_area("Description")
    created_date = st.date_input("Created Date", value=date.today())
    resolved_date = st.date_input("Resolved Date (optional)", value=date.today())
    assigned_to = st.text_input("Assigned To")
    created_at = st.date_input("Record Created At", value=date.today())

    insert_ticket_button = st.form_submit_button("Submit Ticket")

#inserting ticket
if insert_ticket_button:
    #validate required fields
    if not ticket_id or not priority or not status or not category or not subject:
        st.error("❌ Please fill in all required fields! ❌")
    else:
        #insert ticket into DB
        ticket_row_id = insert_ticket(
            ticket_id=ticket_id,
            priority=priority,
            status=status,
            category=category,
            subject=subject,
            description=description,
            created_date=str(created_date),
            resolved_date=str(resolved_date) if resolved_date else None,
            assigned_to=assigned_to,
            created_at=str(created_at)
        )
        if ticket_row_id > 0:
            st.success(f"✅ Ticket successfully added with Row ID: {ticket_row_id}.✅")
        else:
            st.error(f"❌Was not able to insert the tickets with ID: {ticket_row_id}.❌")



st.subheader("Update Ticket Status")

with st.form("update status form"):
    #getting info from the user
    ticket_id = st.number_input("Ticket ID", min_value=1, step=1)
    new_status = st.selectbox(
        "New Status",
        ["Open", "Investigating", "Resolved", "Closed"]
    )

    update_status_button = st.form_submit_button("Update Status")

#updating the ticket
if update_status_button:
    result = update_ticket_status(
        ticket_id=ticket_id,
        new_status=new_status
    )

    if result > 0:
        st.success(f"✅Ticket {ticket_id} updated successfully to '{new_status}'.✅")
    else:
        st.error("❌No ticket found with your ID.❌")



st.subheader("Delete a Ticket")

with st.form("delete ticket form"):
    #getting incident id from the user
    ticket_id = st.number_input("Ticket ID to Delete", min_value=1, step=1)

    delete_ticket_button = st.form_submit_button("Delete Ticket")
#deleting
if delete_ticket_button:
    result = delete_ticket(ticket_id=ticket_id)
    
    if result > 0:
        st.success(f"✅Incident {ticket_id} was successfully deleted.✅")
    else:
        st.error("❌No incident found with your ID.❌")



st.subheader("Tickets by Category")

with st.form("category count form"):
    #getting the number of top N categories from the user
    st.markdown("Select the number of top categories to display:")
    top_n = st.number_input("Top N categories", min_value=1, max_value=20, value=5, step=1)
    ticket_by_category_button = st.form_submit_button("Show Chart")

if ticket_by_category_button:
    df = get_tickets_by_category_count()
    if df.empty:
        st.info("No tickets found.")
    else:
        #filtering top N categories
        df_top = df.head(top_n)
        #displaying
        st.bar_chart(df_top.set_index("category")["count"])


st.subheader("Filter Tickets by Status")

with st.form("status filter form"):
    #getting status input from the user
    status_options = ["Open", "In Progress", "Resolved", "Closed"]
    selected_status = st.selectbox("Select ticket status", status_options)
    submit = st.form_submit_button("Show Tickets")
#displaying
if submit:
    df = get_tickets_by_status(selected_status)
    if df.empty:
        st.info(f"No tickets found with status '{selected_status}'.")
    else:
        st.dataframe(df)


#all tickets
st.subheader("View All Tickets")

with st.form("view all tickets"):
    #button to display
    load_button = st.form_submit_button("Load All Tickets")
#displaying
if load_button:
    df_all = get_all_tickets()

    if df_all.empty:
        st.warning("❌No tickets found in the database.❌")
    else:
        #dataframe
        st.dataframe(df_all)