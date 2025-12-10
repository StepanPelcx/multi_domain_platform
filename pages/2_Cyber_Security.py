import streamlit as st
import matplotlib.pyplot as plt
from services.database_manager import DatabaseManager
from services.ai_assistant import CyberSecurityAI
from models.security_incident import SecurityIncident



st.set_page_config(page_title="🛡️📋Cyber Security Dashboard📋🛡️", page_icon="🛡️📋", layout="wide")

# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

#connecting database through DatabaseManager class
db = DatabaseManager()
#creating an instance of a incident
cyber_model = SecurityIncident(incident_id=0, incident_type="Phishing", severity="High", status="Open", description="User received a suspicious email requesting credentials.", reported_by="John Doe", db=db)
#making sure all incidents are migrated
cyber_model.migrate_incidents()

#Loading incidents into df
if "incidents_loaded" not in st.session_state:
    st.session_state.incidents_loaded = True
    df = cyber_model.get_all_incidents()
    st.session_state.incidents = df
else:
    df = st.session_state.incidents

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