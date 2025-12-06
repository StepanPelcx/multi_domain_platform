import streamlit as st
import pandas as pd
import numpy as np
from openai import OpenAI
import matplotlib.pyplot as plt
from user_handling.db import connect_database
from data.incidents import get_incidents_by_type_count, get_high_severity_by_status, get_all_incidents

st.set_page_config(page_title="🛡️📊📈Cyber Security Analytics📈📊🛡️", page_icon="📊📈", layout="wide")

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

st.header("🛡️📊📈Cyber Security Analytics📈📊🛡️")

col1, col2= st.columns(2)


with col1:
    #getting data frame for graphs
    df = get_all_incidents()

    #first graph
    #getting count of each incident type
    type_count = df['incident_type'].value_counts()
    #reset index
    df_type_count = type_count.reset_index()
    df_type_count.columns = ['incident_type', 'count']
    #displaying the graph
    st.bar_chart(df_type_count.set_index('incident_type'))


    #second graph

    #letting the user select a date range
    start_date = st.date_input("Start date", df["date"].min())
    end_date = st.date_input("End date", df["date"].max())

    #filter the data frame based on selected date range
    filtered_df = df
    filtered_df["date"] = pd.to_datetime(filtered_df["date"])
    filtered_df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]

    #counting incidents per day
    incidents_by_day = filtered_df.groupby("date").size().reset_index(name="count")

    #displaying graph
    st.subheader("Incidents Over Time")
    st.line_chart(incidents_by_day.set_index("date"))


    #third graph

    #getting the input from user
    columns = st.multiselect(
        "Severity types",
        ['Medium', 'Critical', 'Low', 'High']
    )
    filt_df = df[df["severity"].isin(columns)]
    severity_counts = filt_df["severity"].value_counts()

    st.subheader("Incident Count by Severity")
    st.bar_chart(severity_counts)


    #GRAPHS WITH MATPLOTLIB
    #getting data frame for the graphs
    df = get_all_incidents()

    #first graph
    st.subheader("Incidents by Type")
    #getting the number of each incident type
    type_counts = df['incident_type'].value_counts()
    graph1, ax1 = plt.subplots()
    #creating the bar graph
    ax1.bar(type_counts.index, type_counts.values, color='skyblue')
    #setting labels
    ax1.set_xlabel("Incident Type")
    ax1.set_ylabel("Count")
    ax1.set_title("Number of Incidents by Type")

    #displaying graph
    st.pyplot(graph1)


    #second graph
    st.subheader("Severity Distribution")

    #getting the count of each severity type
    severity_counts = df['severity'].value_counts()
    graph2, ax2 = plt.subplots()
    #creating the pie graph, with displaying percentage 
    ax2.pie(severity_counts.values, labels=severity_counts.index, autopct='%1.1f%%', colors=['orange', 'red', 'green', 'purple'])
    #title
    ax2.set_title("Incident Severity Distribution")
    #displaying graph
    st.pyplot(graph2)

    #third graph
    st.subheader("Incident Status by Severity")
    #grouping status with severity
    status_severity = df.groupby(['severity', 'status']).size().unstack(fill_value=0)
    fig3, ax3 = plt.subplots()
    #creating the graph
    status_severity.plot(kind='bar', stacked=True, ax=ax3, colormap='viridis')
    #naming the labels
    ax3.set_xlabel("Severity")
    ax3.set_ylabel("Number of Incidents")
    ax3.set_title("Incident Status by Severity")
    #displaying the graph
    st.pyplot(fig3)



with col2:  
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    st.title("🔍 AI Incident Analyzer")

    # ═══════════════════════════════════════════════# STEP 1: Fetch incident from Week 8 database# ═══════════════════════════════════════════════
    incidents = get_all_incidents()
    conn = connect_database()

    incidents = incidents.to_dict(orient="records") 
    if incidents:
        # Let user select an incident
        incident_options = [
            f"{inc['id']}: {inc['incident_type']} - {inc['severity']}"for inc in incidents
        ]
        
        selected_idx = st.selectbox(
            "Select incident to analyze:",
            range(len(incidents)),
            format_func=lambda i: incident_options[i]
        )
        
        incident = incidents[selected_idx]
        
        # Display incident details
        st.subheader("📋 Incident Details")
        st.write(f"**Type:** {incident['incident_type']}")
        st.write(f"**Severity:** {incident['severity']}")
        st.write(f"**Description:** {incident['description']}")
        st.write(f"**Status:** {incident['status']}")
        
        # ═══════════════════════════════════════════════# STEP 2: Analyze with AI# ═══════════════════════════════════════════════
        if st.button("🤖 Analyze with AI", type="primary"):
            with st.spinner("AI analyzing incident..."):
                
                # Create analysis prompt
                analysis_prompt = f"""Analyze this cybersecurity incident:

        Type: {incident['incident_type']}
        Severity: {incident['severity']}
        Description: {incident['description']}
        Status: {incident['status']}

        Provide:
        1. Root cause analysis
        2. Immediate actions needed
        3. Long-term prevention measures
        4. Risk assessment"""
                # Call ChatGPT API
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a cybersecurity expert."
                        },
                        {
                            "role": "user",
                            "content": analysis_prompt
                        }
                    ]
                )
                
                # Display AI analysis
                st.subheader("🧠 AI Analysis")
                st.write(response.choices[0].message.content)
            



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
