import streamlit as st
import matplotlib.pyplot as plt
from services.database_manager import DatabaseManager
from services.ai_assistant import ITTicketsAI
from models.it_ticket import ITTicket

st.set_page_config(page_title="🎟️Tickets Dashboard🎟️", page_icon="🎟️📋", layout="wide")

# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

#connecting database through DatabaseManager class
db = DatabaseManager()
#creating an instance of a ticket
ticket_model = ITTicket(ticket_id=0, title="Cannot connect to VPN", priority="High", status="Open", assighned_to="Alice Smith", db=db)
#making sure all tickets are migrated
ticket_model.migrate_tickets()

#Loading tickets into df
if "tickets_loaded" not in st.session_state:
    st.session_state.tickets_loaded = True
    df = ticket_model.get_all_tickets()
    st.session_state.tickets = df
else:
    df = st.session_state.tickets

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