import streamlit as st
import pandas as pd
import numpy as np
from openai import OpenAI
import matplotlib.pyplot as plt
from data.tickets import get_all_tickets
from user_handling.db import connect_database

st.set_page_config(page_title="🎟️📊📈Tickets Analytics📈📊🎟️", page_icon="📊📈", layout="wide")

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




st.header("🎟️📊📈Tickets Analytics📈📊🎟️")



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


col1, col2 = st.columns(2)

with col1:
    #getting the data
    df = get_all_tickets()

    #first graph
    st.subheader("Tickets by Priority")
    #getting every unique priority
    available_priorities = df["priority"].unique()
    #letting user choose the priority
    selected_priorities = st.multiselect(
        "Choose which priorities to include:",
        available_priorities,
        default=list(available_priorities)
    )
    #filtering df to selected priorities
    filtered_df1 = df[df["priority"].isin(selected_priorities)]
    #counting unique priorities
    priority_count = filtered_df1["priority"].value_counts()
    #displaying graph
    st.bar_chart(priority_count)


    #second graph
    st.subheader("2️⃣ Tickets Created Over Time")
    #converting the date values
    df2 = df
    df2["created_date"] = pd.to_datetime(df2["created_date"])
    #finding min, max dates
    min_date = df2["created_date"].min()
    max_date = df2["created_date"].max()
    #letting the user choose the date range
    date_range = st.date_input(
    "Select time range:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
    )


    #making sure the program doesnt give errors before the user inputs the end date
    if len(date_range) < 2:
        start_date = date_range[0]
        end_date = max_date
    else:
        #variables for dates
        start_date, end_date = date_range
        
    

    #filtering df according to the user input
    filtered_df2 = df[(df["created_date"] >= pd.to_datetime(start_date)) &
                (df["created_date"] <= pd.to_datetime(end_date))]
    #grouping by
    by_day = filtered_df2.groupby("created_date").size()
    #displaying the graph
    st.line_chart(by_day)


    #third graph
    st.subheader("Tickets by Status")
    #letting user choose the type of graph
    chart_type = st.selectbox(
        "Choose chart type:",
        ["Bar Chart", "Area Chart"]
    )
    #counting unique status values
    status_count = df["status"].value_counts()
    #displaying based on the user input
    if chart_type == "Bar Chart":
        st.bar_chart(status_count)
    else:
        st.area_chart(status_count)


    #GRAPHS WITH MATPLOTLIB

    #first graph
    st.subheader("Number of Tickets by Priority")
    #getting count of each unique priority
    priority_count = df["priority"].value_counts()
    #creating the graph
    graph1, ax1 = plt.subplots()
    ax1.bar(priority_count.index, priority_count.values, color="skyblue")
    #setting the description
    ax1.set_xlabel("Priority")
    ax1.set_ylabel("Count")
    ax1.set_title("Tickets by Priority")
    #displaying
    st.pyplot(graph1)

    #second graph
    st.subheader("Tickets Created Per Year")

    df["year"] = pd.to_datetime(df["created_date"]).dt.year
    year_count = df["year"].value_counts().sort_index()
    #creating the graph
    graph2, ax2 = plt.subplots()
    ax2.plot(year_count.index, year_count.values, marker="o", color="green")
    #setting the description
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Tickets")
    ax2.set_title("Tickets Created Per Year")
    #displaying
    st.pyplot(graph2)


    #third graph
    st.subheader("Tickets by Status")
    #counting unique status values
    status_count = df["status"].value_counts()
    #creating graph
    graph3, ax3 = plt.subplots()
    ax3.pie(status_count.values, labels=status_count.index, autopct="%1.1f%%")
    #setting title
    ax3.set_title("Ticket Status Distribution")
    #displaying
    st.pyplot(graph3)


# AI analyst
with col2:  
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    st.title("🔍 AI Tickets Analyzer")

    # ═══════════════════════════════════════════════# STEP 1: Fetch tickets from Week 8 database# ═══════════════════════════════════════════════
    tickets = get_all_tickets()
    conn = connect_database()

    tickets = tickets.to_dict(orient="records") 
    if tickets:
        # Let user select an incident
        ticket_options = [
            f"{t['ticket_id']}: {t['subject']} ({t['category']}) - {t['priority']}" 
            for t in tickets
        ]
        
        selected_idx = st.selectbox(
            "Select a ticket to analyze:",
            range(len(tickets)),
            format_func=lambda i: ticket_options[i]
        )
        
        ticket = tickets[selected_idx]
        
        # Display dataset details
        st.subheader("📋 Ticket Details")
        st.write(f"**Ticket ID:** {ticket['ticket_id']}")
        st.write(f"**Priority:** {ticket['priority']}")
        st.write(f"**Status:** {ticket['status']}")
        st.write(f"**Category:** {ticket['category']}")
        st.write(f"**Subject:** {ticket['subject']}")
        st.write(f"**Description:** {ticket['description']}")
        st.write(f"**Created Date:** {ticket['created_date']}")
        st.write(f"**Resolved Date:** {ticket.get('resolved_date', 'N/A')}")
        st.write(f"**Assigned To:** {ticket['assigned_to']}")
        
        # ═══════════════════════════════════════════════# STEP 2: Analyze with AI# ═══════════════════════════════════════════════
        if st.button("🤖 Analyze with AI", type="primary"):
            with st.spinner("AI analyzing ticket..."):
                
                # Create analysis prompt
                analysis_prompt = f"""You are an IT support expert. Analyze this IT ticket:

            Ticket ID: {ticket['ticket_id']}
            Priority: {ticket['priority']}
            Status: {ticket['status']}
            Category: {ticket['category']}
            Subject: {ticket['subject']}
            Description: {ticket['description']}
            Created Date: {ticket['created_date']}
            Resolved Date: {ticket.get('resolved_date', 'N/A')}
            Assigned To: {ticket['assigned_to']}

            Provide:
            1. Recommended troubleshooting or resolution steps
            2. Root cause analysis (if possible)
            3. Risk assessment or potential escalation
            4. Suggestions for process improvement or automation
            5. Any other insights relevant for IT operations
            """
                # Call ChatGPT API
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an IT support and operations expert."
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
            

