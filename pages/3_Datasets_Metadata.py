import streamlit as st
from models.dataset import Dataset
from services.database_manager import DatabaseManager
from services.ai_assistant import DatasetsMetadataAI
import matplotlib.pyplot as plt


st.set_page_config(page_title="📁Datasets Dashboard📁", page_icon="📁📋", layout="wide")

#connecting database through DatabaseManager class
db = DatabaseManager()
#creating an instance of dataset
dataset_model = Dataset(dataset_id=0, name="", size_bytes=0, rows=0, source="", db=db)
#making sure all user are migrated
dataset_model.migrate_datasets()

#Loading datasets into df
if ("dashboard_loaded") or ("datasets") not in st.session_state:
    st.session_state.dashboard_loaded = True
    df = dataset_model.get_all_datasets()
    st.session_state.datasets = df  
else:
    df = st.session_state.datasets

# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = "" 
if "messages_DS" not in st.session_state:
    st.session_state.messages_DS = []  # Chat history

# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py") # back to the first page
    st.stop()

st.header("📁Datasets Metadata📁")

#creating tabs to show different functions
tab_dashboard, tab_CRUD, tab_ai = st.tabs(["Dashboard", "CRUD Functions", "AI Assistant"])

with tab_dashboard:
    st.header("📁📊📈Datasets Analytics📈📊📁")
        
    #getting the data
    df = dataset_model.get_all_datasets()

    st.subheader("Dataset Table")
    st.dataframe(df)

    # Let user choose what type of graph
    graph_type = st.selectbox(
        "Choose graph type",
        ["Bar Chart", "Line Chart", "Area Chart"], key="graph1"
    )

    # Let user choose column for x and y axes
    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    x_axis = st.selectbox("Select X-axis", ["category", "dataset_name"])
    y_axis = st.selectbox("Select Y-axis", numeric_columns)

    # Prepare data for plotting
    plot_data = df[[x_axis, y_axis]]
    if x_axis == "category" or x_axis == "dataset_name":
        plot_data = plot_data.groupby(x_axis).sum()  # sum numeric values per category or dataset

    # Display the selected chart
    st.subheader(f"{graph_type} of {y_axis} by {x_axis}")
    if graph_type == "Bar Chart":
        st.bar_chart(plot_data)
    elif graph_type == "Line Chart":
        st.line_chart(plot_data)
    elif graph_type == "Area Chart":
        st.area_chart(plot_data)

    
    st.subheader("Dataset Table")

    #SECOND GRAPH
    # User selects column to group by (only categorical columns)
    categorical_columns = df.select_dtypes(include="object").columns.tolist()
    group_column = st.selectbox("Select column to group by", ["category", "source"])

    # User selects number of top categories to display
    max_items = df[group_column].nunique()
    top_n = st.slider("Select number of top categories to display", 1, max_items, 5)

    # Prepare data
    counts = df[group_column].value_counts().head(top_n)

    # Create pie chart
    graph2, ax = plt.subplots()
    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=140)
    ax.set_title(f"Top {top_n} {group_column} distribution")

    st.pyplot(graph2)

with tab_CRUD:
    #============================================================================================================================================
    # CRUD Functions
    #============================================================================================================================================
    
    col1, col2 = st.columns(2)

    with col1:
        #Insert a dataset
        with st.expander("Insert Dataset"):
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
                    st.session_state.insert_dataset = False
                    st.success(f"✅ Dataset successfully added with ID: {dataset_id} ✅")

        #Deleting a dataset
        with st.expander("🗑️Delete Dataset"):
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

        #Update a dataset based on the user input
        with st.expander("🔄Update Dataset"):
            with st.form("Update Dataset Column"):
                dataset_id = st.number_input("Dataset ID to update", min_value=1, step=1)
                column_to_update = st.selectbox("Select column", ["dataset_name", "category", "source", "last_updated", "record_count", "file_size_mb"])
                #user choose the column to update
                if column_to_update in ["dataset_name", "category", "source"]:
                    new_value = st.text_input("New value")
                elif column_to_update == "last_updated":
                    new_value = st.date_input("New date")
                elif column_to_update == "record_count":
                    new_value = st.number_input("New record count", min_value=0, step=1)
                elif column_to_update == "file_size_mb":
                    new_value = st.number_input("New file size (MB)", min_value=0.0, step=0.01)

                if st.form_submit_button("Update"):
                    if column_to_update == "last_updated":
                        new_value = str(new_value)
                    rows_updated = dataset_model.update_dataset(dataset_id, column_to_update, new_value)
                    if rows_updated > 0:
                        st.success(f"✅ Dataset ID {dataset_id} updated successfully!")
                    else:
                        st.error(f"❌ Dataset ID {dataset_id} not found.")

        #Update a dataset record count
        with st.expander("🔄Update Dataset Record Count"):
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
                        st.session_state.update_dataset = False
                    else:
                        st.error(f"❌ No dataset found with ID {dataset_id}. Update failed.❌")

    with col2:
        #Getting df with category count
        with st.expander("📊Dataset Count by Category"):
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

        #Getting categories with X repeating count
        with st.expander("📊Dataset Categories by Unique Type Count"):
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

        #Getting all datasets
        with st.expander("📊view_all_datasets"):
            df_all = dataset_model.get_all_datasets()

            if df_all.empty:
                st.warning("❌No datasets found in the database.❌")
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
    AI = DatasetsMetadataAI(api_key=st.secrets["OPENAI_API_KEY"])

    with st.sidebar:
        st.subheader("🤖 AI Controls")
        choice = st.selectbox(
            "Choose Assistant",
            ["Analyst", "Assistant"]
        )

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

        if "AI" not in st.session_state:
            st.session_state.AI = DatasetsMetadataAI(api_key=st.secrets["OPENAI_API_KEY"])

        AI = st.session_state.AI

        if "messages_DS" not in st.session_state:
            st.session_state.messages_DS = []  # stores conversation history

        # Display previous messages
        for message in st.session_state.messages_DS:
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
            st.session_state.messages_DS.append({"role": "user", "content": user_input})

            # Prepare AI history
            AI._AIAssistant__history = [{"role": "system", "content": AI._AIAssistant__system_prompt}] + st.session_state.messages_DS

            # Stream AI response
            full_response = ""
            for chunk in AI.stream_message(user_input):
                full_response += chunk
                assistant_placeholder.markdown(full_response + "▌")  # streaming cursor

            # Save final assistant response
            st.session_state.messages_DS.append({"role": "assistant", "content": full_response})
            assistant_placeholder.markdown(full_response)  # remove cursor


        with st.sidebar:
            st.subheader("💬 Chat controls")
            # Show message count
            message_count = sum(1 for message in st.session_state.get("messages_DS", []) if message["role"] in ["user", "assistant"])
            st.metric("Messages", message_count)
            # Clear chat history
            if st.button("🗑️ Clear Chat History"):
                AI.clear_history()
                st.session_state.messages_DS = []
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