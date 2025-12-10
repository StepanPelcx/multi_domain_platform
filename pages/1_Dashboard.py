import streamlit as st
import datetime
from services.database_manager import DatabaseManager

st.set_page_config(page_title="Dashboard", page_icon="📋", layout="wide")

# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

#connecting database through DatabaseManager class
db = DatabaseManager()
#ensure all tables are created
db.create_all_tables()

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

# If logged in, show dashboard content
st.title("☰Dashboard☰ ")

now = datetime.datetime.now()

st.markdown(
    f"📅{now.strftime("%A %dth %B %Y")}   \n"
    f"⏰{now.strftime("%H:%M")}"
)
#button for swithing to settings
if st.button("⚙️Settings⚙️"):
    st.switch_page("pages/5_Settings.py")
        

#Showing success login only once
if st.session_state.show_login_success:
    #Making sure all the tables are created
    st.success(f"Hello, **{st.session_state.username}**! You are logged in.")
    #making sure success login message shows only once
    st.session_state.show_login_success = False

#main image
st.image("images/header.jpg")

st.subheader("Please choose which data you want to work with")

#columns for user to choose between dataset
col1, col2, col3 = st.columns(3)

#Cyber incidents column
with col1:
    st.subheader("🛡️Cyber Security🛡️")
    #button for selection
    choose_security = st.button("Choose", key="security")
    st.text('Click "Choose" to be redirected to Cyber Security page.')
    st.image("images/security.jpg", use_container_width=True)
    if choose_security:
        st.switch_page("pages/2_Cyber_Security.py")

#Datasets column
with col2:
    st.subheader("📁Datasets📁")
    #button for selection
    choose_datasets = st.button("Choose", key="datasets")
    st.text('Click "Choose" to be redirected to Datasets page.')
    st.image("images/datasets.jpg", use_container_width=True)
    if choose_datasets:
        st.switch_page("pages/3_Datasets_Metadata.py")

#IT Tickets column
with col3:
    st.subheader("🎟️Tickets🎟️")
    #button for selection
    choose_tickets = st.button("Choose", key="tickets")
    st.text('Click "Choose" to be redirected to Tickets page.')
    st.image("images/tickets.jpg", use_container_width=True)
    if choose_tickets:
        st.switch_page("pages/4_IT_Tickets.py")

