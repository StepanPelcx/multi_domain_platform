import streamlit as st
import pandas as pd
import numpy as np
from openai import OpenAI
from pathlib import Path
from user_handling.db import connect_database
from data.incidents import insert_incident, get_all_incidents, update_incident_status, delete_incident, get_incidents_by_type_count, get_high_severity_by_status, get_incident_types_with_many_cases, migrate_incidents


st.set_page_config(page_title="🛡️📋Cyber Security Dashboard📋🛡️", page_icon="🛡️📋", layout="wide")

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


st.header("🛡️📋Cyber Security Dashboard📋🛡️")


st.subheader("Migrate Incidents From CSV File")
st.info("Make sure CSV file is migrated before working with other functions.")

# Button to trigger migration
if st.button("🚀 Migrate Incidents"):
    migration = migrate_incidents()

    if migration:
        st.success("✅All incidents migrated.✅")
    else:
        st.error("❌Was not able to migrate the incidents.❌")


#============================================================================================================================================
# CRUD Functions
#============================================================================================================================================

st.subheader("Insert Incident")

with st.form("incident form"):
    #getting info from the user
    date = st.date_input("Incident Date")
    incident_type = st.text_input("Incident Type")
    severity = st.selectbox("Severity Level", ["Low", "Medium", "High", "Critical"])
    status = st.selectbox("Status", ["Open", "Investigating", "Resolved", "Closed"])
    description = st.text_area("Incident Description")
    reported_by = st.text_input("Reported By (optional)")

    insert_incident_button = st.form_submit_button("Submit Incident")
#inserting
if insert_incident_button:
    if not date or not incident_type or not severity or not status:
        st.error("❌Please enter values for all required inputs.❌")
    else:
        incident_id = insert_incident(
        date=str(date),
        incident_type=incident_type,
        severity=severity,
        status=status,
        description=description,
        reported_by=reported_by if reported_by else None
    )

        st.success(f"✅Incident successfully added with ID: {incident_id}✅")


st.subheader("Update Incident Status")

with st.form("update status form"):
    #getting info from the user
    incident_id = st.number_input("Incident ID", min_value=1, step=1)
    new_status = st.selectbox(
        "New Status",
        ["Open", "Investigating", "Resolved", "Closed"]
    )

    update_status_button = st.form_submit_button("Update Status")
#updating
if update_status_button:
    result = update_incident_status(
        incident_id=incident_id,
        new_status=new_status
    )

    if result > 0:
        st.success(f"✅Incident {incident_id} updated successfully to '{new_status}'.✅")
    else:
        st.error("❌No incident found with your ID.❌")


st.subheader("Delete an Incident")

with st.form("delete incident form"):
    #getting incident id from the user
    incident_id = st.number_input("Incident ID to Delete", min_value=1, step=1)

    delete_incident_button = st.form_submit_button("Delete Incident")
#deleting
if delete_incident_button:
    result = delete_incident(incident_id=incident_id)
    
    if result > 0:
        st.success(f"✅Incident {incident_id} was successfully deleted.✅")
    else:
        st.error("❌No incident found with your ID.❌")



st.subheader("Get Incidents by Type Count")


with st.form("incident type count form"):
    #button, if the user wants to show
    get_incidents_by_type_button = st.form_submit_button("Show Incident Type Counts")
#displaying df
if get_incidents_by_type_button:
    df = get_incidents_by_type_count()

    if df.empty:
        st.warning("❌No incidents found in the database.❌")
    else:
        st.subheader("Incidents Grouped by Type")
        st.dataframe(df)

        #chart
        st.subheader("Visualization")
        st.bar_chart(df.set_index("incident_type"))


st.subheader("Get High Severity by Incident Status")


with st.form("high severity status form"):
    #button, if the user wants to show
    submit_btn = st.form_submit_button("Show High Severity Stats")
#displaying
if submit_btn:
    df = get_high_severity_by_status()

    if df.empty:
        st.warning("❌No high severity incidents found.❌")
    else:
        st.subheader("High Severity Incidents Grouped by Status")
        st.dataframe(df)

        #Visualization
        st.subheader("Chart")
        st.bar_chart(df.set_index("status"))


st.subheader("Get Incident Types With Many Cases")


with st.form("incident types many cases form"):
    #asking the user for how many cases
    min_count = st.number_input(
        "Show incident types with more than X cases:",
        min_value=1,
        value=5,
        step=1
    )

    incident_many_cases_button = st.form_submit_button("Show Results")
#displaying
if incident_many_cases_button:
    df = get_incident_types_with_many_cases(min_count)

    if df.empty:
        st.warning(f"❌No incident types found with more than {min_count} cases.❌")
    else:
        st.subheader(f"Incident Types With More Than {min_count} Cases")
        st.dataframe(df)
        #visualization
        st.subheader("Chart")
        st.bar_chart(df.set_index("incident_type"))


