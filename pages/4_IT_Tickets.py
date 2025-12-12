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
if ("tickets_loaded") or ("tickets") not in st.session_state:
    st.session_state.tickets_loaded = True
    df = ticket_model.get_all_tickets()
    st.session_state.tickets = df
else:
    df = st.session_state.tickets

# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the IT Tickets.")
    if st.button("Go to login page"):
        st.switch_page("Home.py") # back to the first page
    st.stop()

st.header("🎟️Tickets Dashboard🎟️")

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

    graph_type = st.selectbox(
        "Choose graph type",
        ["Bar Chart", "Line Chart", "Area Chart"], key="ticket_graph1"
    )

    #categorical columns - x axis
    categorical_cols = ["priority", "status", "category", "assigned_to"]
    x_axis = st.selectbox("Select X-axis (categorical)", categorical_cols)

    #numeric columns - y axis
    numeric_cols = df.select_dtypes(include=["int64","float64"]).columns.tolist()
    y_axis = st.selectbox("Select Y-axis (numeric)", numeric_cols)

    #aggregate numeric values per category
    plot_data = df[[x_axis, y_axis]].groupby(x_axis).sum()

    #displaying chart
    st.subheader(f"{graph_type} of {y_axis} by {x_axis}")
    if graph_type == "Bar Chart":
        st.bar_chart(plot_data)
    elif graph_type == "Line Chart":
        st.line_chart(plot_data)
    elif graph_type == "Area Chart":
        st.area_chart(plot_data)
    
    #SECOND GRAPH
    st.subheader("Categorical distribution (Pie chart)")
    #user selects category
    group_column = st.selectbox("Select categorical column for Pie chart", categorical_cols, key="ticket_graph2")
    #slider for choosing N categories
    top_n = st.slider(
        f"Select number of top {group_column} categories to display",
        1, df[group_column].nunique(), 5
    )

    #counting categories
    counts = df[group_column].value_counts().head(top_n)

    #creating pie chart
    graph2, ax = plt.subplots()
    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=140)
    ax.set_title(f"Top {top_n} {group_column} distribution")
    st.pyplot(graph2)

#============================================================================================================================================
# CRUD Functions
#============================================================================================================================================
    
with tab_CRUD:
    #creating columns for CRUD functions
    col1, col2 = st.columns(2)

    with col1:
        #INSERT TICKET
        with st.expander("➕ Insert Ticket"):
            with st.form("insert ticket form"):
                #user inputs
                ticket_id = st.text_input("Ticket ID")
                priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
                status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
                category = st.text_input("Category")
                subject = st.text_input("Subject")
                description = st.text_area("Description")
                created_date = st.date_input("Created Date")
                resolved_date_input = st.date_input("Resolved Date (optional)", value=None)
                assigned_to = st.text_input("Assigned To")
                created_at = st.date_input("Created At")

                insert_ticket_button = st.form_submit_button("Submit Ticket")

            #Insert ticket into database
            if insert_ticket_button:
                if (not ticket_id or not priority or not status or not category or 
                    not subject or not description or not created_date or not created_at):
                    st.error("❌ Please fill in all required fields. ❌")

                else:
                    ticket_db_id = ticket_model.insert_ticket(
                        ticket_id=ticket_id,
                        priority=priority,
                        status=status,
                        category=category,
                        subject=subject,
                        description=description,
                        created_date=str(created_date),
                        resolved_date=str(resolved_date_input) if resolved_date_input else None,
                        assigned_to=assigned_to,
                        created_at=str(created_at)
                    )

                    st.success(f"✅ Ticket successfully inserted with ID: {ticket_db_id} ✅")

        # DELETE TICKET
        with st.expander("🗑️ Delete Ticket"):
            with st.form("delete ticket form"):
                ticket_id_to_delete = st.number_input("Ticket ID to Delete", min_value=1, step=1)

                delete_ticket_button = st.form_submit_button("Delete Ticket")

            if delete_ticket_button:
                if not ticket_id_to_delete:
                    st.error("❌ Please enter a valid Ticket ID. ❌")
                else:
                    rows_deleted = ticket_model.delete_ticket(int(ticket_id_to_delete))

                    if rows_deleted > 0:
                        st.success(f"✅ Ticket with ID {ticket_id_to_delete} was successfully deleted! ✅")
                    else:
                        st.error(f"❌ No ticket found in the database with ID {ticket_id_to_delete}. ❌")

        #UPDATE TICKET
        with st.expander("🔄 Update Ticket"):
            with st.form("update ticket form"):
                ticket_id = st.number_input("Ticket ID to update", min_value=1, step=1)
                #user selects what column to update
                column_to_update = st.selectbox(
                    "Select column to update",
                    [
                        "ticket_id",
                        "priority",
                        "status",
                        "category",
                        "subject",
                        "description",
                        "created_date",
                        "resolved_date",
                        "assigned_to",
                        "created_at"
                    ]
                )

                #Input types based on selected column
                if column_to_update in ["ticket_id", "priority", "status", "category", "subject", "assigned_to"]:
                    new_value = st.text_input("New value")

                elif column_to_update in ["description"]:
                    new_value = st.text_area("New description")

                elif column_to_update in ["created_date", "resolved_date", "created_at"]:
                    new_value = st.date_input("New date")

                #Submit update
                if st.form_submit_button("Update Ticket"):
                    #Convert date to string
                    if column_to_update in ["created_date", "resolved_date", "created_at"]:
                        new_value = str(new_value)

                    rows_updated = ticket_model.update_ticket(ticket_id, column_to_update, new_value)

                    if rows_updated > 0:
                        st.success(f"✅ Ticket ID {ticket_id} updated successfully!✅")
                    else:
                        st.error(f"❌ Ticket ID {ticket_id} not found.❌")


    with col2:
        #TICKET COUNT BY CATEGORY
        with st.expander("📊 Ticket Count by Category"):
            df_category_count = ticket_model.get_tickets_by_category_count()
            if df_category_count.empty:
                st.warning("❌No tickets found in the database.❌")
            else:
                st.dataframe(df_category_count, use_container_width=True)

        #TICKETS BY STATUS
        with st.expander("📊 Filter Tickets by Status"):
            selected_status = st.selectbox(
                "Select ticket status",
                ["Open", "In Progress", "Resolved", "Closed"]
            )

            df_status = ticket_model.get_tickets_by_status(selected_status)

            if df_status.empty:
                st.info(f"No tickets found with status: {selected_status}")
            else:
                st.dataframe(df_status, use_container_width=True)

        #Getting all tickets
        with st.expander("📊View all tickets"):
            df_all = ticket_model.get_all_tickets()

            if df_all.empty:
                st.warning("❌No tickets found in the database.❌")
            else:
                #dataframe
                st.dataframe(df_all)

# ====================
# AI assistance
# ====================

with tab_ai:
    #checking if the key exists
    if "OPENAI_API_KEY" not in st.secrets:
        st.error("❌ OpenAI API key is missing from Streamlit secrets.")
        st.stop()
    #calling AI instance
    AI = ITTicketsAI(api_key=st.secrets["OPENAI_API_KEY"])

    with st.sidebar:
        st.subheader("🤖 AI Controls")
        choice = st.selectbox(
            "Choose Assistant",
            ["Analyst", "Assistant"]
        )

    #getting all datasets
    df = ticket_model.get_all_tickets()

    #Choice Analyst
    if choice == "Analyst":
        st.header("🤖 AI Ticket Analyst")
        st.text("This AI assistant gives you analysis of a ticket of your choice.")

        #TICKETS ANALYTICS
        if df.empty:
            st.warning("❌ No tickets found in the database. ❌")
        else:
            #letting the user select a ticket
            ticket_options = [
                f"{d['ticket_id']} ({d['category']}) - {d['status']}" 
                for _, d in df.iterrows()
            ]
            selected_idx = st.selectbox(
                "Select ticket to analyze:",
                range(len(ticket_options)),
                format_func=lambda i: ticket_options[i]
            )
            ticket = df.iloc[selected_idx].to_dict()

            #display dataset info
            st.subheader("📋 Ticket Details")
            st.write(f"**Ticket ID:** {ticket['ticket_id']}")
            st.write(f"**Priority:** {ticket['priority']}")
            st.write(f"**Status:** {ticket['status']}")
            st.write(f"**Category:** {ticket['category']}")
            st.write(f"**Subject:** {ticket['subject']}")
            st.write(f"**Description:** {ticket['description']}")
            st.write(f"**Created Date:** {ticket['created_date']}")
            st.write(f"**Resolved Date:** {ticket['resolved_date']}")
            st.write(f"**Assigned To:** {ticket['assigned_to']}")
            st.write(f"**Created At:** {ticket['created_at']}")

            # Button to analyze with AI
            if st.button("🤖 Analyze with AI"):
                with st.spinner("AI analyzing ticket..."):
                    ai_response = AI.analyze_ticket(ticket)
                    st.subheader("🧠 AI Analysis")
                    st.write(ai_response)

    #Choice Assistant
    else:
        st.header("💬 AI IT Assistant")

        if "AIIT" not in st.session_state:
            st.session_state.AIIT = ITTicketsAI(api_key=st.secrets["OPENAI_API_KEY"])

        AI = st.session_state.AIIT

        if "messages_IT" not in st.session_state:
            st.session_state.messages_IT = []  # stores conversation history

        # Display previous messages
        for message in st.session_state.messages_IT:
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
            st.session_state.messages_IT.append({"role": "user", "content": user_input})

            # Prepare AI history
            AI._AIAssistant__history = [{"role": "system", "content": AI._AIAssistant__system_prompt}] + st.session_state.messages_IT

            # Stream AI response
            full_response = ""
            for chunk in AI.stream_message(user_input):
                full_response += chunk
                assistant_placeholder.markdown(full_response + "▌")  # streaming cursor

            # Save final assistant response
            st.session_state.messages_IT.append({"role": "assistant", "content": full_response})
            assistant_placeholder.markdown(full_response)  # remove cursor


        with st.sidebar:
            st.subheader("💬 Chat controls")
            # Show message count
            message_count = sum(1 for message in st.session_state.get("messages_IT", []) if message["role"] in ["user", "assistant"])
            st.metric("Messages", message_count)
            # Clear chat history
            if st.button("🗑️ Clear Chat History"):
                AI.clear_history()
                st.session_state.messages_IT = []
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
    if st.button("Back to Hub"):
        st.switch_page("pages/1_Home_Hub.py")