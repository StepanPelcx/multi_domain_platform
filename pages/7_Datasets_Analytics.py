import streamlit as st
import pandas as pd
import numpy as np
from openai import OpenAI
from user_handling.db import connect_database
from data.datasets import get_all_datasets
import matplotlib.pyplot as plt

st.set_page_config(page_title="📁📊📈Datasets Analytics📈📊📁", page_icon="📊📈", layout="wide")

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




st.header("📁📊📈Datasets Analytics📈📊📁")


col1, col2 = st.columns(2)

with col1:
    #getting the data
    df = get_all_datasets()

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

    #first graph
    st.subheader("📈 Record Count per Dataset")
    #creating the graph
    graph1, ax1 = plt.subplots()
    ax1.bar(df['dataset_name'], df['record_count'], color='skyblue')
    #description
    ax1.set_xlabel("Dataset")
    ax1.set_ylabel("Record Count")
    ax1.set_title("Number of Records per Dataset")
    #displaying
    st.pyplot(graph1)

    #second graph
    st.subheader("🥧 Dataset Category Distribution")
    category_counts = df['category'].value_counts()
    graph2, ax2 = plt.subplots()
    #creating pie graph
    ax2.pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%', colors=['orange','green','purple'])
    #title
    ax2.set_title("Dataset Categories")
    #displaying
    st.pyplot(graph2)

    #third graph
    st.subheader("🔎 File Size vs Record Count")
    graph3, ax3 = plt.subplots()
    ax3.scatter(df['record_count'], df['file_size_mb'], color='red', s=100)
    #for i, txt in enumerate(df['dataset_name']):
    #    ax3.annotate(txt, (df['record_count'][i], df['file_size_mb'][i]), textcoords="offset points", xytext=(5,5), ha='left')
    #description
    ax3.set_xlabel("Record Count")
    ax3.set_ylabel("File Size (MB)")
    ax3.set_title("Correlation: File Size vs Record Count")
    #displaying
    st.pyplot(graph3)


with col2:  
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    st.title("🔍 AI Dataset Analyzer")

    # ═══════════════════════════════════════════════# STEP 1: Fetch datasets from Week 8 database# ═══════════════════════════════════════════════
    datasets = get_all_datasets()
    conn = connect_database()

    datasets = datasets.to_dict(orient="records") 
    if datasets:
        # Let user select an incident
        dataset_options = [
            f"{d['dataset_name']} ({d['category']}) - {d['source']}" for d in datasets
        ]
        
        selected_idx = st.selectbox(
            "Select dataset to analyze:",
            range(len(datasets)),
            format_func=lambda i: dataset_options[i]
        )
        
        dataset = datasets[selected_idx]
        
        # Display dataset details
        st.subheader("📋 Dataset Details")
        st.write(f"**Name:** {dataset['dataset_name']}")
        st.write(f"**Category:** {dataset['category']}")
        st.write(f"**Source:** {dataset['source']}")
        st.write(f"**Last Updated:** {dataset['last_updated']}")
        st.write(f"**Record Count:** {dataset['record_count']}")
        st.write(f"**File Size (MB):** {dataset['file_size_mb']}")
        st.write(f"**Created At:** {dataset['created_at']}")
        
        # ═══════════════════════════════════════════════# STEP 2: Analyze with AI# ═══════════════════════════════════════════════
        if st.button("🤖 Analyze with AI", type="primary"):
            with st.spinner("AI analyzing dataset..."):
                
                # Create analysis prompt
                analysis_prompt = f"""You are a data management expert. Analyze this dataset:

            Dataset Name: {dataset['dataset_name']}
            Category: {dataset['category']}
            Source: {dataset['source']}
            Last Updated: {dataset['last_updated']}
            Record Count: {dataset['record_count']}
            File Size (MB): {dataset['file_size_mb']}
            Created At: {dataset['created_at']}

            Provide:
            1. Assessment of dataset quality
            2. Potential use cases or applications
            3. Risks or issues (e.g., stale data, duplicates)
            4. Recommendations for maintenance or improvement
            5. Any other insights relevant to data operations
            """
                # Call ChatGPT API
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a data management expert."
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