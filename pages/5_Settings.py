import streamlit as st
from services.auth_manager import AuthManager, Hasher
from services.database_manager import DatabaseManager
from models.user import User


st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "show_password_change" not in st.session_state:
    st.session_state.show_password_change = False
if "confirm_password_change" not in st.session_state:
    st.session_state.confirm_password_change = False
if "get_user_role" not in st.session_state:
    st.session_state.get_user_role = False
if "get_all_users" not in st.session_state:
    st.session_state.get_all_users = False

#connecting db
db = DatabaseManager()
#creating instances
auth_model = AuthManager(db=db)
hasher_model = Hasher(db=db)
user_model = User(username='', password_hash='', role='', db=db)


# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the Settings.")
    if st.button("Go to login page"):
        st.switch_page("Home.py") # back to the first page
    st.stop()

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
        st.rerun()

# Sidebar back to dashboard button
with st.sidebar:
    if st.button("Back to Hub"):
        st.switch_page("pages/1_Home_Hub.py")


# If logged in, show dashboard content
st.title("⚙️ Settings")

#button for changing password
if st.button("🔐🔄Change password🔄🔐"):
    st.session_state.show_password_change = True

#password change logic
if st.session_state.show_password_change:
    with st.form("change password form"):
        st.subheader("*Change password*")
        #getting info from the user
        password = st.text_input("🔑Enter your current password", type="password", key="current_password")
        new_password = st.text_input("🔒Enter your new password", type="password", key="changed_password")
        confirmation = st.text_input("🔒Confirm your new password", type="password", key="confirmation_password")
        back = st.form_submit_button("Back", key="ChangeBack")
        submit = st.form_submit_button("Change password", key="Change")

        if back:
            st.session_state.show_password_change = False
            del st.session_state.confirm_password_change
            st.rerun()

        if submit:
            #printing error if the user did not input some values
            if not password or not new_password or not confirmation:
                st.error("❌You did not enter some of the required passwords.❌")
                st.stop()
            #checking if the new password is different from the old one
            if password == new_password:
                st.error("❌New password is the same as the old one.❌")
                st.stop()
            #verifying the current password from user
            if not user_model.verify_password(st.session_state.username, password):
                st.error("❌Incorrect current password.❌")
                st.stop()
            #checking the user input
            if new_password != confirmation:
                st.error("❌Your new password does not match❌")
                st.stop()
            #checking if the password satisfy required conditions
            if not auth_model.validate_password(new_password):
                st.error("❌Your password must satisfy those conditions: password must have from 8 to 24 characters long.❌\n❌It must contain at least one upper letter, one lower letter, one number, and one special character.❌")
                st.stop()
            #after validation confirm the user wants to change password
            st.session_state.confirm_password_change = True

        if st.session_state.confirm_password_change:
            #asking the user to confirm the change
            st.caption("⚠️Are you sure you want to change your password?⚠️")

            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Yes, confirm change"):
                    if hasher_model.change_password(st.session_state.username.strip().capitalize(), new_password):
                        st.success("✅Your password changed successfuly! Please click 'Back' to close this window.✅")
                        if back:
                            st.session_state.show_password_change = False
                            del st.session_state.confirm_password_change
                            st.rerun()
                    else:
                        st.error("❌Failed to update the password in database.❌")
                if st.form_submit_button("Cancel"):
                    st.session_state.show_password_change = False
                    del st.session_state.confirm_password_change
                    st.rerun()

#button for getting user role
if st.button("👤User role👤"):
    st.session_state.get_user_role = True

#printing user role
if st.session_state.get_user_role:
    #calling user role function
    role = user_model.get_role(st.session_state.username)
    if role:
        st.info(f"The users role is '{user_model.get_role(st.session_state.username)}'")
    else:
        st.error("❌User not found in the database.❌")
    if st.button("Done"):
        st.session_state.get_user_role = False
        st.rerun()


#users df, if admin get all the users info

if st.button("All users info"):
    st.session_state.get_all_users = True

if st.session_state.get_all_users:
    user_role = user_model.get_role(st.session_state.username)
    if user_role != "admin":
        st.error('❌Only "Admin" users can view this.❌')
        st.session_state.get_all_users = False
        st.rerun()
    else:
        st.dataframe(auth_model.get_all_users())
        if st.button("Back"):
            st.session_state.get_all_users = False
            st.rerun()
