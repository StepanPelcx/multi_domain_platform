import streamlit as st
import pandas as pd
import numpy as np
from models.dataset import Dataset
from services.database_manager import DatabaseManager
from services.ai_assistant import DatasetsMetadataAI
import matplotlib.pyplot as plt
from openai import OpenAI

st.set_page_config(page_title="📁Datasets Dashboard📁", page_icon="📁📋", layout="wide")

# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
#crud functions
if "insert_incident" not in st.session_state:
    st.session_state.insert_incident = False
if "delete_incident" not in st.session_state:
    st.session_state.delete_incident = False
if "update_incident" not in st.session_state:
    st.session_state.update_incident = False
if "category_count_incidents" not in st.session_state:
    st.session_state.category_count_incidents = False
if "repeating_categories_incidents" not in st.session_state:
    st.session_state.repeating_categories_incidents = False
#AI 
if "AI" not in st.session_state:
    st.session_state.AI = DatasetsMetadataAI(api_key=st.secrets["OPENAI_API_KEY"])


# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py") # back to the first page
    st.stop()

st.header("📁Datasets Metadata📁")

#connecting database through DatabaseManager class
db = DatabaseManager()
#creating an instance of dataset
dataset_model = Dataset(dataset_id=0, name="", size_bytes=0, rows=0, source="", db=db)
#making sure all user are migrated
dataset_model.migrate_datasets()

#creating tabs to show different functions
tab_dashboard, tab_CRUD, tab_ai = st.tabs(["Dashboard", "CRUD Functions", "AI Assistant"])

with tab_dashboard:
    st.header("📁📊📈Datasets Analytics📈📊📁")

    #getting the data
    df = dataset_model.get_all_datasets()

    #first graph
    st.subheader("Record Count per Dataset")

    #user choose category to filter
    categories = df['category'].unique().tolist()
    selected_category = st.selectbox("Filter by Category", ["All"] + categories)

    if selected_category != "All":
        df_filtered = df[df['category'] == selected_category]
    else:
        df_filtered = df.copy()
    #displaying
    st.bar_chart(df_filtered.set_index("dataset_name")["record_count"])

    #second graph
    st.subheader("File Size per Dataset")

    #user choose top N datasets by file size
    top_n = st.slider("Select top N datasets by file size", min_value=1, max_value=len(df_filtered), value=5)
    #filtering based on the user input
    df_top = df_filtered.sort_values("file_size_mb", ascending=False).head(top_n)
    #displaying
    st.area_chart(df_top.set_index("dataset_name")["file_size_mb"])

    #third graph
    st.subheader("Record Count vs File Size")

    #normalize for line chart
    df_filtered["record_count_norm"] = df_filtered["record_count"] / df_filtered["record_count"].max()
    df_filtered["file_size_norm"] = df_filtered["file_size_mb"] / df_filtered["file_size_mb"].max()

    line_data = df_filtered.set_index("dataset_name")[["record_count_norm", "file_size_norm"]]
    #displaying
    st.line_chart(line_data)
    st.caption("Line chart shows normalized values (0-1) of record count and file size for comparison.")

    #GRAPHS WITH MATPLOTLIB

with tab_CRUD:
    #============================================================================================================================================
    # CRUD Functions
    #============================================================================================================================================

    #Insert a dataset
    if st.button("Insert Incident"):
        st.session_state.insert_incident = True

    if st.session_state.insert_incident:
        with st.form("dataset form"):
            #getting input from user
            dataset_name = st.text_input("Dataset Name")
            category = st.text_input("Category")
            source = st.text_input("Source")
            last_updated = st.date_input("Last Updated")
            record_count = st.number_input("Record Count", min_value=0, step=1)
            file_size_mb = st.number_input("File Size (MB)", min_value=0.0, step=0.01)
            created_at = st.date_input("Created At")

            insert_dataset_button = st.form_submit_button("Submit Dataset")
        #inserting dataset
        if insert_dataset_button:
            # Validation
            if (not dataset_name or not category or not source or not last_updated or record_count is None or file_size_mb is None or not created_at):
                st.error("❌ Please enter values for all required inputs. ❌")

            else:
                dataset_id = dataset_model.insert_dataset(
                    dataset_name=dataset_name,
                    category=category,
                    source=source,
                    last_updated=str(last_updated),
                    record_count=int(record_count),
                    file_size_mb=float(file_size_mb),
                    created_at=str(created_at)
                )
                st.session_state.insert_incident = False
                st.success(f"✅ Dataset successfully added with ID: {dataset_id} ✅")
        if st.button("Back"):
            st.session_state.insert_incident = False
            st.rerun()


    #Deleting a dataset
    if st.button("Delete Dataset"):
        st.session_state.delete_incident = True

    if st.session_state.delete_incident:
        with st.form("delete dataset form"):
            #getting id from the user
            dataset_id = st.number_input("Dataset ID to Delete", min_value=1, step=1)

            delete_dataset_button = st.form_submit_button("Delete Dataset")
        #deleting
        if delete_dataset_button:
            if not dataset_id:
                st.error("❌ Please enter a valid Dataset ID. ❌")
            else:
                rows_deleted = dataset_model.delete_dataset(int(dataset_id))

                if rows_deleted > 0:
                    st.success(f"✅ Dataset with ID {dataset_id} was successfully deleted!✅")
                else:
                    st.error(f"❌ No dataset found with ID {dataset_id}.")
        if st.button("Back"):
            st.session_state.delete_incident = False
            st.rerun()

    #Update a dataset record count
    if st.button("Update Dataset Record Count"):
        st.session_state.update_incident = True

    if st.session_state.update_incident:
        with st.form("update dataset form"):
            #getting info from the user
            dataset_id = st.number_input("Dataset ID", min_value=1, step=1)
            new_record_count = st.number_input("New Record Count", min_value=0, step=1)

            update_button = st.form_submit_button("Update Record Count")
        #updating
        if update_button:
            if not dataset_id or new_record_count is None:
                st.error("❌ Please enter valid values for all fields. ❌")
            else:
                rows_updated = dataset_model.update_dataset_record_count(dataset_id=int(dataset_id),new_record_count=int(new_record_count),)

                if rows_updated > 0:
                    st.success(
                        f"🔄 Dataset ID {dataset_id} successfully updated!\n\n"
                        f"📌 New Record Count: {new_record_count}\n"
                        f"📅 Last Updated set to today"
                        )
                    st.session_state.update_incident = False
                else:
                    st.error(f"❌ No dataset found with ID {dataset_id}. Update failed.❌")
        if st.button("Back"):
            st.session_state.update_incident = False
            st.rerun()

    #Getting df with category count
    if st.button("Dataset Count by Category"):
        st.session_state.category_count_incidents = True

    if st.session_state.category_count_incidents:
        with st.form("Get datasets by category count"):
            #button to show
            get_datasets_by_category_count_button = st.form_submit_button("Show datasets by category count")

        if get_datasets_by_category_count_button:
            #get data from database
            df_category = dataset_model.get_datasets_by_category_count()

            if df_category.empty:
                st.warning("❌No datasets found.❌")
            else:
                #displaying raw data
                st.dataframe(df_category)
                #bar chart
                st.bar_chart(df_category.set_index("category")["count"])
        if st.button("Back"):
            st.session_state.category_count_incidents = False
            st.rerun()

    #Getting categories with X repeating count
    if st.button("Incident Categories by Unique Type Count"):
        st.session_state.repeating_categories_incidents = True

    if st.session_state.repeating_categories_incidents:
        with st.form("repeating categories form"):
            #getting the min number of datasets from the user
            min_count = st.number_input("Minimum number of datasets per category", min_value=1, value=5, step=1)
            submit = st.form_submit_button("View")
        #displaying
        if submit:
            df_repeating = dataset_model.get_repeating_dataset_categories(min_count=min_count)

            if df_repeating.empty:
                st.warning(f"❌No categories found with more than {min_count} datasets.❌")
            else:
                #displaying raw data
                st.dataframe(df_repeating)
                #bar chart
                st.bar_chart(df_repeating.set_index("category")["count"])
            if st.button("back"):
                st.session_state.repeating_categories_incidents = False
                st.rerun()


    #Getting all datasets
    view_all_button = st.button("view_all_datasets")

    if view_all_button:
        df_all = dataset_model.get_all_datasets()

        if df_all.empty:
            st.warning("❌No datasets found in the database.❌")
        else:
            #dataframe
            st.dataframe(df_all)
            #visualization
            st.subheader("Record Count per Dataset")
            st.bar_chart(df_all.set_index("dataset_name")["record_count"])
        
        if st.button("Back"):
            st.rerun()  

with tab_ai:
    with st.sidebar:
        st.subheader("🤖 AI Controls")
        choice = st.selectbox(
            "Choose Assistant",
            ["Analyst", "Assistant"]
        )
    
    #getting the API key
        #inicializing AI
        AI = st.session_state.AI
        #getting all datasets
        df = dataset_model.get_all_datasets()

    #Choice Analyst
    if choice == "Analyst":
        st.header("🤖 AI Dataset Analyst")
        st.text("This AI assistant gives you analysis of a dataset of your choice.")

        #DATASET ANALYTICS
        if df.empty:
            st.warning("❌ No datasets found in the database. ❌")
        else:
            #letting the user select a dataset
            dataset_options = [
                f"{d['dataset_name']} ({d['category']}) - {d['source']}" 
                for _, d in df.iterrows()
            ]
            selected_idx = st.selectbox(
                "Select dataset to analyze:",
                range(len(dataset_options)),
                format_func=lambda i: dataset_options[i]
            )
            dataset = df.iloc[selected_idx].to_dict()

            #display dataset info
            st.subheader("📋 Dataset Details")
            st.write(f"**Name:** {dataset['dataset_name']}")
            st.write(f"**Category:** {dataset['category']}")
            st.write(f"**Source:** {dataset['source']}")
            st.write(f"**Record Count:** {dataset['record_count']}")
            st.write(f"**File Size (MB):** {dataset['file_size_mb']}")
            st.write(f"**Last Updated:** {dataset['last_updated']}")
            st.write(f"**Created At:** {dataset['created_at']}")

            # Button to analyze with AI
            if st.button("🤖 Analyze with AI"):
                with st.spinner("AI analyzing dataset..."):
                    ai_response = AI.analyze_dataset(dataset)
                    st.subheader("🧠 AI Analysis")
                    st.write(ai_response)
        
    #Choice Assistant
    else:
        st.header("💬 AI Data Science Assistant")

        #init chat history once
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        #displaying previous messages
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # User input
        user_input = st.chat_input("Ask me anything about Data Science...")

        if not user_input:
            st.markdown("This is an AI Assistant specialized in **Data Science** field. Aks any questions reguarding this field...")

        else:
            #storing user message
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })

            #getting AI response
            response_box = st.empty()
            full_response = ""

            with st.spinner("AI is typing..."):
                response = AI.stream_message(user_input)

                for chunk in response:
                    full_response += chunk
                    response_box.markdown(full_response)

            #storing AI reply
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": full_response
            })

            #refreshing to show messages instantly
            st.rerun()
    
    with st.sidebar:
        st.title("💬 Chat Controls")

        #count messages
        message_count = sum(1 for msg in AI.history() if msg["role"] in ["user", "assistant"])
        st.metric("Messages", message_count)

        #clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history.clear()
            AI.clear_history()
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