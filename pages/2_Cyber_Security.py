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
cyber_model = SecurityIncident(incident_id=0, incident_type="Phishing", severity="High", status="Open", description="User received a suspicious email requesting credentials.", reported_by="John Doe", created_at="2025-01-01 10:00:00", db=db)
#making sure all incidents are migrated
cyber_model.migrate_incidents()

#Loading incidents into df
if ("incidents_loaded") or ("incidents") not in st.session_state:
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

st.header("🛡️📋Cyber Security Dashboard📋🛡️")

#creating tabs to show different functions
tab_dashboard, tab_CRUD, tab_ai = st.tabs(["Dashboard", "CRUD Functions", "AI Assistant"])

with tab_dashboard:
    #getting the df
    df = df
    #displaying the df
    with st.expander("DataFrame"):
        st.dataframe(df)
    #FIRST GRAPH
    st.subheader("Numeric aggregation by category")

    #letting user select graph type
    graph_type = st.selectbox(
        "Choose graph type",
        ["Bar Chart", "Line Chart", "Area Chart"], key="graph1"
    )

    #choose X-axis (categorical)
    x_axis = st.selectbox("Select X-axis (categorical)", ["incident_type", "severity", "status"])

    #choose Y-axis (numeric)
    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    y_axis = st.selectbox("Y-axis (numeric)", numeric_columns)

    #aggregate numeric values per category
    plot_data = df[[x_axis, y_axis]].groupby(x_axis).sum()

    #displaying chart based on user input
    st.subheader(f"{graph_type} of {y_axis} by {x_axis}")
    if graph_type == "Bar Chart":
        st.bar_chart(plot_data)
    elif graph_type == "Line Chart":
        st.line_chart(plot_data)
    elif graph_type == "Area Chart":
        st.area_chart(plot_data)

    #SECOND GRAPH
    st.subheader("Categorical distribution (Pie chart)")

    #select categorical column
    categorical_columns = ["incident_type", "severity", "status", "reported_by"]
    group_column = st.selectbox("Select categorical column for Pie chart", categorical_columns, key="graph2")

    #top N categories to display
    max_items = df[group_column].nunique()
    top_n = st.slider("Select number of top categories to display", 1, max_items, 5)

    #counting categories
    counts = df[group_column].value_counts().head(top_n)

    #creating pie chart
    graph2, ax = plt.subplots()
    ax.pie(counts.values, labels=counts.index,)
    ax.set_title(f"Top {top_n} {group_column} distribution")
    st.pyplot(graph2)

with tab_CRUD:
    pass

# ====================
# AI assistance
# ====================

with tab_ai:
    #checking if the key exists
    if "OPENAI_API_KEY" not in st.secrets:
        st.error("❌ OpenAI API key is missing from Streamlit secrets.")
        st.stop()
    #calling AI instance
    AI = CyberSecurityAI(api_key=st.secrets["OPENAI_API_KEY"])

    with st.sidebar:
        st.subheader("🤖 AI Controls")
        choice = st.selectbox(
            "Choose Assistant",
            ["Analyst", "Assistant"]
        )

    #getting all datasets
    df = cyber_model.get_all_incidents()

    #Choice Analyst
    if choice == "Analyst":
        st.header("🤖 AI Incident Analyst")
        st.text("This AI assistant gives you analysis of a incident of your choice.")

        #INCIDENTS ANALYTICS
        if df.empty:
            st.warning("❌ No Incidents found in the database. ❌")
        else:
            #letting the user select an incident
            incident_options = [
                f"{d["incident_type"]} ({d["severity"]}) - {d["status"]}" 
                for _, d in df.iterrows()
            ]
            selected_idx = st.selectbox(
                "Select incident to analyze:",
                range(len(incident_options)),
                format_func=lambda i: incident_options[i]
            )
            incident = df.iloc[selected_idx].to_dict()

            #display dataset info
            st.subheader("📋 Incident Details")
            st.write(f"**Incident Type:** {incident["incident_type"]}")
            st.write(f"**Date:** {incident["date"]}")
            st.write(f"**Severity:** {incident["severity"]}")
            st.write(f"**Status:** {incident["status"]}")
            st.write(f"**Description:** {incident["description"]}")
            st.write(f"**Reported by:** {incident["reported_by"]}")

            # Button to analyze with AI
            if st.button("🤖 Analyze with AI"):
                with st.spinner("AI analyzing incident..."):
                    ai_response = AI.analyze_incident(incident)
                    st.subheader("🧠 AI Analysis")
                    st.write(ai_response)

    #Choice Assistant
    else:
        st.header("💬 AI Cyber Security Assistant")

        if "AICS" not in st.session_state:
            st.session_state.AICS = CyberSecurityAI(api_key=st.secrets["OPENAI_API_KEY"])

        AI = st.session_state.AICS

        if "messages_CS" not in st.session_state:
            st.session_state.messages_CS = []  # stores conversation history

        # Display previous messages
        for message in st.session_state.messages_CS:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.write(message["content"])

        # a container
        chat_container = st.container() 

        # User input
        user_input = st.chat_input("Ask me anything...")

        if user_input:
            # Add the new user message immediately to the container
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(user_input)

                with st.chat_message("assistant") as assistant_chat:
                    assistant_placeholder = st.empty()

            # Append user message to session after rendering
            st.session_state.messages_CS.append({"role": "user", "content": user_input})

            # Prepare AI history
            AI._AIAssistant__history = [{"role": "system", "content": AI._AIAssistant__system_prompt}] + st.session_state.messages_CS

            # Stream AI response
            full_response = ""
            for chunk in AI.stream_message(user_input):
                full_response += chunk
                assistant_placeholder.markdown(full_response + "▌")  # streaming cursor

            # Save final assistant response
            st.session_state.messages_CS.append({"role": "assistant", "content": full_response})
            assistant_placeholder.markdown(full_response)  # remove cursor


        with st.sidebar:
            st.subheader("💬 Chat controls")
            # Show message count
            message_count = sum(1 for message in st.session_state.get("messages_CS", []) if message["role"] in ["user", "assistant"])
            st.metric("Messages", message_count)
            # Clear chat history
            if st.button("🗑️ Clear Chat History"):
                AI.clear_history()
                st.session_state.messages_CS = []
                st.rerun()


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
