import streamlit as st
import pandas as pd
import numpy as np
import datetime
from data.schema import create_all_tables

st.set_page_config(page_title="Dashboard", page_icon="📋", layout="wide")

# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

#Ensure all tables exist
create_all_tables()

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
    st.switch_page("pages/12_Settings.py")
        

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

with col1:
    st.subheader("🛡️Cyber Security🛡️")
    security = st.button("Choose", key="security")
    st.text('Click "Choose" to be redirected to Cyber Security page.')
    st.image("images/security.jpg", use_container_width=True)
    if security:
        st.switch_page("pages/3_Cyber_Security_Dashboard.py")

with col2:
    st.subheader("📁Datasets📁")
    datasets = st.button("Choose", key="datasets")
    st.text('Click "Choose" to be redirected to Datasets page.')
    st.image("images/datasets.jpg", use_container_width=True)
    if datasets:
        st.switch_page("pages/6_Datasets_Dashboard.py")

with col3:
    st.subheader("🎟️Tickets🎟️")
    tickets = st.button("Choose", key="tickets")
    st.text('Click "Choose" to be redirected to Tickets page.')
    st.image("images/tickets.jpg", use_container_width=True)
    if tickets:
        st.switch_page("pages/9_Tickets_Dashboard.py")

