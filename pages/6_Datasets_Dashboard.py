import streamlit as st
import pandas as pd
import numpy as np
from data.datasets import migrate_datasets, insert_dataset, delete_dataset, update_dataset_record_count, get_datasets_by_category_count, get_repeating_dataset_categories, get_all_datasets

st.set_page_config(page_title="📁Datasets Dashboard📁", page_icon="📁📋", layout="wide")

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



st.header("📁Datasets Dashboard📁")

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


st.subheader("Migrate Datasets From CSV File")
st.info("Make sure CSV file is migrated before working with other functions.")

# Button to trigger migration
if st.button("🚀 Migrate Datasets"):
    migration = migrate_datasets()

    if migration:
        st.success("✅All incidents migrated.✅")
    else:
        st.error("❌Was not able to migrate the incidents.❌")


#============================================================================================================================================
# CRUD Functions
#============================================================================================================================================


st.subheader("Insert Dataset")

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
        dataset_id = insert_dataset(
            dataset_name=dataset_name,
            category=category,
            source=source,
            last_updated=str(last_updated),
            record_count=int(record_count),
            file_size_mb=float(file_size_mb),
            created_at=str(created_at)
        )

        st.success(f"✅ Dataset successfully added with ID: {dataset_id} ✅")


st.subheader("Delete Dataset")

with st.form("delete dataset form"):
    #getting id from the user
    dataset_id = st.number_input("Dataset ID to Delete", min_value=1, step=1)

    delete_dataset_button = st.form_submit_button("Delete Dataset")
#deleting
if delete_dataset_button:
    if not dataset_id:
        st.error("❌ Please enter a valid Dataset ID. ❌")
    else:
        rows_deleted = delete_dataset(int(dataset_id))

        if rows_deleted > 0:
            st.success(f"✅ Dataset with ID {dataset_id} was successfully deleted!✅")
        else:
            st.error(f"❌ No dataset found with ID {dataset_id}.")


st.subheader("Update Dataset Record Count")

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
        rows_updated = update_dataset_record_count(dataset_id=int(dataset_id),new_record_count=int(new_record_count),)

        if rows_updated > 0:
            st.success(
                f"🔄 Dataset ID {dataset_id} successfully updated!\n\n"
                f"📌 New Record Count: {new_record_count}\n"
                f"📅 Last Updated set to today"
                )
        else:
            st.error(f"❌ No dataset found with ID {dataset_id}. Update failed.❌")


st.subheader("Dataset Count by Category")

with st.form("Get datasets by category count"):
    #button to show
    get_datasets_by_category_count_button = st.form_submit_button("Show datasets by category count")

if get_datasets_by_category_count_button:
    #get data from database
    df_category = get_datasets_by_category_count()

    if df_category.empty:
        st.warning("❌No dataset metadata found.❌")
    else:
        #displaying raw data
        st.dataframe(df_category)
        #bar chart
        st.bar_chart(df_category.set_index("category")["count"])


st.subheader("Repeating Dataset Categories")

with st.form("repeating categories form"):
    #getting the min number of datasets from the user
    min_count = st.number_input("Minimum number of datasets per category", min_value=1, value=5, step=1)

    submit_button = st.form_submit_button("Show Results")
#displaying
if submit_button:
    df_repeating = get_repeating_dataset_categories(min_count=min_count)

    if df_repeating.empty:
        st.warning(f"❌No categories found with more than {min_count} datasets.❌")
    else:
        #displaying raw data
        st.dataframe(df_repeating)
        #bar chart
        st.bar_chart(df_repeating.set_index("category")["count"])


st.subheader("View All Datasets")

with st.form("view all datasets"):
    #button to display
    load_button = st.form_submit_button("Load All Datasets")
#displaying
if load_button:
    df_all = get_all_datasets()

    if df_all.empty:
        st.warning("❌No datasets found in the database.❌")
    else:
        #dataframe
        st.dataframe(df_all)
        #visualization
        st.subheader("Record Count per Dataset")
        st.bar_chart(df_all.set_index("dataset_name")["record_count"])