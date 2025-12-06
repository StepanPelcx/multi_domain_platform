import streamlit as st
from user_handling.verification import register_user, login_user, check_password_strength
from openai import OpenAI


api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)



st.set_page_config(page_title="Login / Register", page_icon="🔑", layout="centered")

# ---------- Initialise session state ----------
if "users" not in st.session_state:
    # Very simple in-memory "database": {username: password}
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

st.title("🔐 Welcome")

# If already logged in, go straight to dashboard (optional)
if st.session_state.logged_in:
    st.success(f"Already logged in as **{st.session_state.username}**.")
    if st.button("Go to dashboard"):
        # Use the official navigation API to switch pages
        st.switch_page("pages/1_Dashboard.py") # path is relative to Home.py :contentReference[oaicite:1]{index=1}
    # Sidebar logout button
    with st.sidebar:
        if st.button("Log out   ➜]"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.info("You have been logged out.")
            st.switch_page("Home.py")
    st.stop() # Don’t show login/register again

# ---------- Tabs: Login / Register ----------
tab_login, tab_register = st.tabs(["Login", "Register"])

# ----- LOGIN TAB -----
with tab_login:
    st.subheader("Login")

    login_username = st.text_input("Username", key="login_username").strip().capitalize()
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log in", type="primary"):
    # Simple credential check (for teaching only – not secure!)
        users = st.session_state.users
        login = login_user(login_username, login_password)
        if login == "username":
            st.error("Invalid username.")
        elif login == False:
            st.error("Invalid password")
        else:
            st.session_state.logged_in = True
            st.session_state.show_login_success = True
            st.session_state.username = login_username
            st.success(f"Welcome back, {login_username}! 🎉 ")
            # Redirect to dashboard page
            st.switch_page("pages/1_Dashboard.py")

# ----- REGISTER TAB -----
with tab_register:
    st.subheader("Register")

    new_username = st.text_input("Choose a username", key="register_username").strip().capitalize()
    new_password = st.text_input("Choose a password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm password", type="password", key="register_confirm")  
    new_role = st.selectbox("Choose a role", ["user", "admin", "analyst",])

    if st.button("💪🛡️Check Password Strength🛡️💪"):
        if new_password:
            st.info(check_password_strength(new_password))
        else:
            st.error("❌Please enter password to check.❌")

    if st.button("Create account"):
        # Basic checks – again, just for teaching
        if not new_username or not new_password:
            st.warning("Please fill in all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match."      )
        elif new_username in st.session_state.users:
            st.error("Username already exists. Choose another one.")
        else:
            state = register_user(new_username, new_password, new_role)
            if state == False:
                st.error("The user already exists.")
            elif state == "username":
                st.error("Your username must satisfy those conditions: username must have from 3 to 20 characters.\nusername must be only letters or numbers.")
            elif state == "password":
                st.error("Your password must satisfy those conditions: password must have from 8 to 24 characters long.\nIt must contain at least one upper letter, one lower letter, one number, and one special character.")
            else:
                # "Save" user in our simple in-memory store
                st.session_state.users[new_username] = new_password
                st.success("Account created! You can now log in from the Login tab.")
                st.info("Tip: go to the Login tab and sign in with your new account.")
            