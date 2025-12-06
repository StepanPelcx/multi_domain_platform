import streamlit as st
from openai import OpenAI

# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to use AI assistant.")
    if st.button("Go to login page"):
        st.switch_page("Home.py") # back to the first page
    st.stop()


st.header("IT Operations Assistant")
#st.text("This AI Assistant is not specialyst in any fields. \nIts purpose is mainly for general questions.")

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Handle user input
user_input = st.chat_input("Ask me anything...")


if not user_input:
    st.markdown("This is an AI Assistant specialized in **IT Operations** field. Aks any questions reguarding this field...")
    

# ═══════════════════════════════════════════════# SIDEBAR: Chat Controls# ═══════════════════════════════════════════════
with st.sidebar:
    st.title("💬 Chat Controls")

    
    
    # Show message count
    message_count = sum(1 for message in st.session_state.get("messages_IT", []) if message["role"] in ["user", "assistant"])
    st.metric("Messages", message_count)
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        # Reset messages to initial state
        st.session_state.messages_IT = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ]
        # Rerun to refresh the interface
        st.rerun()

# ═══════════════════════════════════════════════# Initialize session state# ═══════════════════════════════════════════════
if "messages_IT" not in st.session_state:
    st.session_state.messages_IT = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "assistant", "content": "Hello! How can I help you today?"}
    ]


# Display existing messages
for message in st.session_state.messages_IT:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])



if user_input:
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
# Add to session state
    st.session_state.messages_IT.append(
        {"role": "user", "content": user_input}
    )
    
# ═══════════════════════════════════════════════# STREAMING: Enable stream=True parameter# ═══════════════════════════════════════════════
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=st.session_state.messages_IT,
        stream=True # ← Enable streaming!
        )
    
# ═══════════════════════════════════════════════# STEP 1: Create empty placeholder for AI response# ═══════════════════════════════════════════════
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
# ═══════════════════════════════════════════════# STEP 2: Process chunks as they arrive# ═══════════════════════════════════════════════
        with st.spinner("Typing...  "):  
            for chunk in response:
                # Extract content from chunk
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                
# ═══════════════════════════════════════════════# STEP 3: Update display with cursor effect# ═══════════════════════════════════════════════
                    message_placeholder.markdown(full_response + "▌")
        
# ═══════════════════════════════════════════════# STEP 4: Final display without cursor# ═══════════════════════════════════════════════
    message_placeholder.markdown(full_response)
    
    # Save complete response to session state
    st.session_state.messages_IT.append(
            {"role": "assistant", "content": full_response}
        )


# Specialized system prompt for IT
messages = [
    {
        "role": "system",
        "content": """You are an IT operations and support ticket expert assistant.
- Triage and prioritize support tickets
- Provide step-by-step troubleshooting guidance
- Diagnose user-reported issues across systems and applications
- Recommend appropriate system configurations or improvements
- Explain technical issues in clear, accurate terms
- Align responses with standard ITSM practices (e.g., ITIL)
- Prioritize actionable, reliable resolutions
Tone: Professional, technical, service-oriented
Format: Clear steps or structured explanations"""
}

]

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